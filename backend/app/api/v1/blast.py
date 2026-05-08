import json
import os
import re
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db, utcnow
from app.core.config import settings as app_settings
from app.models import BlastTask, TnEntry, User
from app.schemas import BlastTaskCreate, ApiResponse
from app.api.v1.auth import get_current_user
from app.tasks.blast_task import run_blast_task

router = APIRouter(prefix="/blast", tags=["BLAST"])

VALID_DNA = set("ATGCN")
VALID_PROTEIN = set("ACDEFGHIKLMNPQRSTVWYX*")
NUCL_PROGRAMS = {"blastn", "blastx", "tblastn"}
PROT_PROGRAMS = {"blastp", "tblastx"}
PROT_DB_PROGRAMS = {"blastp", "blastx"}


def clean_sequence(seq: str, is_nucleotide: bool = True) -> str:
    seq = seq.upper()
    seq = re.sub(r'\s+', '', seq)
    seq = re.sub(r'\d+', '', seq)
    if seq.startswith(">"):
        first_newline = seq.find('\n')
        if first_newline != -1:
            seq = seq[first_newline + 1:]
        seq = re.sub(r'\s+', '', seq)
    if is_nucleotide:
        seq = ''.join(c for c in seq if c in VALID_DNA)
    else:
        seq = ''.join(c for c in seq if c in VALID_PROTEIN)
    return seq


@router.post("", response_model=ApiResponse)
async def submit_blast(data: BlastTaskCreate, db: AsyncSession = Depends(get_db)):
    is_protein_query = data.program in PROT_PROGRAMS
    is_nucleotide_query = data.program in NUCL_PROGRAMS

    cleaned_seq = clean_sequence(data.sequence, is_nucleotide=is_nucleotide_query)
    if not cleaned_seq:
        raise HTTPException(status_code=400, detail="Invalid sequence")

    min_len = 5 if is_protein_query else 10
    if len(cleaned_seq) < min_len:
        raise HTTPException(
            status_code=400,
            detail=f"Sequence too short (min {min_len} {'aa' if is_protein_query else 'bp'})",
        )

    task_id = f"blast_{uuid.uuid4().hex[:12]}"

    task = BlastTask(
        task_id=task_id,
        sequence=cleaned_seq,
        program=data.program,
        evalue=data.evalue,
        max_target_seqs=data.max_target_seqs,
        status="pending",
        started_at=utcnow(),
    )
    db.add(task)
    await db.commit()

    run_blast_task.delay(
        task_id=task_id,
        sequence=cleaned_seq,
        program=data.program,
        evalue=data.evalue,
        max_target_seqs=data.max_target_seqs,
    )

    return ApiResponse(data={"task_id": task_id, "status": "pending"})


@router.get("/{task_id}", response_model=ApiResponse)
async def get_blast_status(task_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(BlastTask).where(BlastTask.task_id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    resp = {
        "task_id": task.task_id,
        "status": task.status,
        "program": task.program,
        "created_at": task.created_at.isoformat() if task.created_at else None,
    }
    if task.status == "completed":
        resp["hits"] = task.result or []
    if task.status == "failed" and task.error_message:
        resp["error_message"] = task.error_message
    return ApiResponse(data=resp)


@router.get("/{task_id}/result", response_model=ApiResponse)
async def get_blast_result(task_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(BlastTask).where(BlastTask.task_id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.status != "completed":
        raise HTTPException(status_code=400, detail="Task not completed")
    return ApiResponse(data={
        "task_id": task.task_id, "status": task.status, "hits": task.result or [],
    })


@router.post("/rebuild-db", response_model=ApiResponse)
async def rebuild_blast_db(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Permission denied")

    db_dir = app_settings.BLAST_DB_DIR
    for is_prot in [False, True]:
        prefix = "tndb_prot" if is_prot else "tndb"
        for ext in ([".phr", ".pin", ".psq", ".fasta"] if is_prot else [".nhr", ".nin", ".nsq", ".fasta"]):
            p = os.path.join(db_dir, prefix + ext)
            if os.path.exists(p):
                os.unlink(p)

    tn_result = await db.execute(select(TnEntry))
    entries = tn_result.scalars().all()

    nucl_entries = []
    for e in entries:
        seq = (e.dna_sequence or "").upper()
        seq = re.sub(r'[^ATGCN]', '', seq)
        if seq and len(seq) >= 10:
            nucl_entries.append((e.name, seq))

    prot_entries = []
    for e in entries:
        for field in ("orf1_sequence", "orf2_sequence"):
            seq = (getattr(e, field, None) or "").upper()
            seq = re.sub(r'[^ACDEFGHIKLMNPQRSTVWYX*]', '', seq)
            if seq and len(seq) >= 5:
                prot_entries.append((f"{e.name}_{field.replace('_sequence', '')}", seq))

    from app.tasks.blast_task import _build_blast_db

    results = []
    if nucl_entries:
        _build_blast_db(db_dir, nucl_entries, is_protein=False)
        results.append(f"nucleotide DB: {len(nucl_entries)} seqs")
    if prot_entries:
        _build_blast_db(db_dir, prot_entries, is_protein=True)
        results.append(f"protein DB: {len(prot_entries)} seqs")

    return ApiResponse(message=f"BLAST databases rebuilt: {', '.join(results)}")
