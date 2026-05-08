import json
import os
import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db, utcnow
from app.core.config import settings
from app.models import MineTnTask, TnEntry, User
from app.schemas import (
    MineTnTaskCreate, MineTnTaskResponse, MineTnImportRequest, ApiResponse,
)
from app.api.v1.auth import get_current_user
from app.tasks.minetn_task import run_minetn_task

router = APIRouter(prefix="/minetn", tags=["MineTn"])


@router.post("/upload", response_model=ApiResponse)
async def upload_genome(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Permission denied")

    if not file.filename.endswith(('.fa', '.fasta', '.fna')):
        raise HTTPException(status_code=400, detail="FASTA format required")

    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(settings.UPLOAD_DIR, f"{uuid.uuid4().hex[:8]}_{file.filename}")
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    return ApiResponse(data={"filepath": file_path, "filename": file.filename})


@router.post("", response_model=ApiResponse)
async def create_minetn_task(
    data: MineTnTaskCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Permission denied")

    task_id = f"minetn_{uuid.uuid4().hex[:12]}"

    task = MineTnTask(
        task_id=task_id,
        user_id=current_user.id,
        genome_file=data.genome_file,
        parameters=data.model_dump(),
        status="pending",
        progress=0,
        started_at=utcnow(),
    )
    db.add(task)
    await db.commit()

    run_minetn_task.delay(
        task_id=task_id,
        genome_file=data.genome_file,
        parameters=data.model_dump(),
    )

    return ApiResponse(data={"task_id": task_id, "status": "pending"})


@router.get("", response_model=ApiResponse)
async def get_minetn_task_list(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Permission denied")

    result = await db.execute(
        select(MineTnTask).order_by(MineTnTask.created_at.desc())
    )
    tasks = result.scalars().all()
    items = [MineTnTaskResponse.model_validate(t).model_dump() for t in tasks]
    return ApiResponse(data=items)


@router.get("/{task_id}", response_model=ApiResponse)
async def get_minetn_task(
    task_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Permission denied")

    result = await db.execute(select(MineTnTask).where(MineTnTask.task_id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return ApiResponse(data=MineTnTaskResponse.model_validate(task))


@router.get("/{task_id}/results", response_model=ApiResponse)
async def get_minetn_results(
    task_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Permission denied")

    result = await db.execute(select(MineTnTask).where(MineTnTask.task_id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.status != "completed":
        raise HTTPException(status_code=400, detail="Task not completed")
    if not task.result_file or not os.path.exists(task.result_file):
        return ApiResponse(data=[])

    with open(task.result_file, "r") as f:
        results = json.load(f)
    return ApiResponse(data=results)


@router.post("/{task_id}/import", response_model=ApiResponse)
async def import_minetn_results(
    task_id: str,
    data: MineTnImportRequest = MineTnImportRequest(),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Permission denied")

    result = await db.execute(select(MineTnTask).where(MineTnTask.task_id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if not task.result_file or not os.path.exists(task.result_file):
        raise HTTPException(status_code=400, detail="Result file not found")

    with open(task.result_file, "r") as f:
        all_results = json.load(f)

    selected = [
        r for r in all_results if r["element_id"] in data.element_ids
    ] if data.element_ids else all_results

    count = 0
    for r in selected:
        existing = await db.execute(select(TnEntry).where(TnEntry.name == r["element_id"]))
        if existing.scalar_one_or_none():
            continue
        entry = TnEntry(
            name=r["element_id"],
            family=r.get("family", "Unknown"),
            tn_group="Unknown",
            dna_sequence=r.get("sequence", ""),
            length=r.get("length", 0),
            irl=r.get("irl"),
            irr=r.get("irr"),
            ir=r.get("ir"),
            dr=r.get("dr"),
            mge_type=r.get("mge_type", "TE"),
            status="pending",
            submitted_by=current_user.id,
        )
        db.add(entry)
        count += 1

    await db.commit()
    return ApiResponse(data={"count": count})
