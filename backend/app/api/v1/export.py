from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional
import io

from app.core.database import get_db
from app.models import TnEntry, User
from app.schemas import ApiResponse
from app.api.v1.auth import get_current_user

router = APIRouter(prefix="/export", tags=["Export"])


class BatchExportRequest(BaseModel):
    format: str = "fasta"
    ids: list[str] = []
    family: Optional[str] = None


@router.get("/fasta/{tn_id}")
async def export_fasta(
    tn_id: str,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(TnEntry).where(TnEntry.name == tn_id, TnEntry.status == "approved")
    )
    entry = result.scalar_one_or_none()

    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found or not yet approved")

    seq = entry.dna_sequence or ""
    fasta_content = f">{entry.name} {entry.family} transposon from {entry.origin or 'unknown'}\n"
    for i in range(0, len(seq), 80):
        fasta_content += seq[i:i+80] + "\n"

    return StreamingResponse(
        io.BytesIO(fasta_content.encode()),
        media_type="text/plain",
        headers={"Content-Disposition": f"attachment; filename={entry.name}.fasta"}
    )


@router.get("/embl/{tn_id}")
async def export_embl(
    tn_id: str,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(TnEntry).where(TnEntry.name == tn_id, TnEntry.status == "approved")
    )
    entry = result.scalar_one_or_none()

    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found or not yet approved")

    embl_content = generate_embl(entry)

    return StreamingResponse(
        io.BytesIO(embl_content.encode()),
        media_type="text/plain",
        headers={"Content-Disposition": f"attachment; filename={entry.name}.embl"}
    )


@router.post("/batch")
async def batch_export(
    data: BatchExportRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Permission denied")

    query = select(TnEntry)

    if data.ids:
        query = query.where(TnEntry.name.in_(data.ids))
    if data.family:
        query = query.where(TnEntry.family == data.family)

    result = await db.execute(query.limit(10000))
    entries = result.scalars().all()

    if not entries:
        raise HTTPException(status_code=404, detail="No data found")

    content = ""
    if data.format == "fasta":
        for entry in entries:
            seq = entry.dna_sequence or ""
            content += f">{entry.name} {entry.family} transposon from {entry.origin or 'unknown'}\n"
            for i in range(0, len(seq), 80):
                content += seq[i:i+80] + "\n"
    elif data.format == "embl":
        for entry in entries:
            content += generate_embl(entry) + "\n"

    filename = f"tndb_export.{data.format}"
    return StreamingResponse(
        io.BytesIO(content.encode()),
        media_type="text/plain",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


def generate_embl(entry: TnEntry) -> str:
    lines = []
    lines.append(f"ID   {entry.name} DNA; {entry.mge_type or 'TE'}; {entry.length or 0} BP.")
    lines.append("XX")
    lines.append(f"AC   {entry.accession_number or '.'}")
    lines.append("XX")
    lines.append(f"DE   {entry.family} transposon from the {entry.origin or 'unknown'} genome.")
    lines.append("XX")

    species_name = entry.origin or "Unknown"
    lines.append(f"OS   {species_name}")
    lines.append(f"OC   {entry.family}; {entry.tn_group}.")
    lines.append("XX")

    lines.append("FH   Key             Location/Qualifiers")
    lines.append(f"FT   source          1..{entry.length or 0}")
    lines.append(f'FT                   /organism="{species_name}"')
    lines.append('FT                   /mol_type="genomic DNA"')
    lines.append("XX")

    if entry.irl:
        lines.append("FT   IRL             .")
        lines.append('FT                   /note="left TIR"')
        lines.append(f'FT                   /sequence="{entry.irl}"')

    if entry.irr:
        lines.append("FT   IRR             .")
        lines.append('FT                   /note="right TIR"')
        lines.append(f'FT                   /sequence="{entry.irr}"')

    if entry.ir:
        lines.append(f"FT   IR              {entry.ir}")

    if entry.dr is not None:
        lines.append(f"FT   DR              {entry.dr}")

    lines.append("XX")

    if entry.orf1_begin and entry.orf1_end:
        lines.append(f"FT   CDS             {entry.orf1_begin}..{entry.orf1_end}")
        lines.append(f'FT                   /strand="{entry.orf1_strand or "+"}"')
        if entry.orf1_function:
            lines.append(f'FT                   /function="{entry.orf1_function}"')
        if entry.orf1_chemistry:
            lines.append(f'FT                   /chemistry="{entry.orf1_chemistry}"')
        if entry.orf1_length:
            lines.append(f'FT                   /length="{entry.orf1_length}"')

    if entry.orf2_begin and entry.orf2_end:
        lines.append(f"FT   CDS             {entry.orf2_begin}..{entry.orf2_end}")
        lines.append(f'FT                   /strand="{entry.orf2_strand or "-"}"')
        if entry.orf2_function:
            lines.append(f'FT                   /function="{entry.orf2_function}"')
        if entry.orf2_chemistry:
            lines.append(f'FT                   /chemistry="{entry.orf2_chemistry}"')
        if entry.orf2_length:
            lines.append(f'FT                   /length="{entry.orf2_length}"')

    lines.append("XX")
    lines.append(f"SQ   Sequence {entry.length or 0} BP;")

    seq = entry.dna_sequence or ""
    for i in range(0, len(seq), 60):
        lines.append(f"     {seq[i:i+60]}")

    lines.append("//")

    return "\n".join(lines)
