import io
import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel

from app.core.database import get_db, utcnow
from app.models import DownloadRequest, TnEntry, User
from app.schemas.common import ApiResponse
from app.api.v1.auth import get_current_user

logger = logging.getLogger("tndb.download_request")

router = APIRouter(prefix="/download-request", tags=["Download Request"])


class SubmitDownloadRequest(BaseModel):
    requester_email: str
    requester_name: Optional[str] = None
    requester_institution: Optional[str] = None
    requested_data: str
    data_format: str = "fasta"
    purpose: Optional[str] = None


class ReviewDownloadRequest(BaseModel):
    action: str
    comment: Optional[str] = None


@router.post("", response_model=ApiResponse)
async def submit_download_request(
    data: SubmitDownloadRequest,
    db: AsyncSession = Depends(get_db),
):
    entry_names = [n.strip() for n in data.requested_data.split(",") if n.strip()]
    entry_count = len(entry_names)

    max_entries = await _get_max_download_entries(db)
    if entry_count > max_entries:
        raise HTTPException(
            status_code=400,
            detail=f"Too many entries requested ({entry_count}). Maximum allowed is {max_entries}.",
        )

    req = DownloadRequest(
        requester_email=data.requester_email,
        requester_name=data.requester_name,
        requester_institution=data.requester_institution,
        requested_data=data.requested_data,
        data_format=data.data_format,
        purpose=data.purpose,
        status="pending",
    )
    db.add(req)
    await db.commit()
    await db.refresh(req)

    return ApiResponse(data={"id": req.id, "status": "pending", "entry_count": entry_count}, message="Download request submitted successfully")


async def _get_max_download_entries(db: AsyncSession) -> int:
    from app.models import SystemSetting
    result = await db.execute(
        select(SystemSetting).where(SystemSetting.key == "max_download_entries")
    )
    setting = result.scalar_one_or_none()
    if setting and setting.value:
        try:
            return int(setting.value)
        except ValueError:
            pass
    return 50


@router.get("/admins", response_model=ApiResponse)
async def get_admin_list(
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(User).where(User.role == "admin", User.is_active == True)
    )
    admins = result.scalars().all()

    admin_list = []
    for admin in admins:
        admin_list.append({
            "id": admin.id,
            "username": admin.username,
            "email": admin.email,
            "institution": admin.institution,
        })

    return ApiResponse(data=admin_list)


@router.get("/pending", response_model=ApiResponse)
async def get_pending_download_requests(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Permission denied")

    query = select(DownloadRequest).where(DownloadRequest.status == "pending").order_by(DownloadRequest.created_at.asc())

    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar() or 0

    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    requests = result.scalars().all()

    items = []
    for req in requests:
        items.append({
            "id": req.id,
            "requester_email": req.requester_email,
            "requester_name": req.requester_name,
            "requester_institution": req.requester_institution,
            "requested_data": req.requested_data,
            "data_format": req.data_format,
            "purpose": req.purpose,
            "status": req.status,
            "created_at": req.created_at.isoformat() if req.created_at else None,
        })

    return ApiResponse(data={"items": items, "total": total, "page": page, "page_size": page_size})


@router.get("/history", response_model=ApiResponse)
async def get_download_request_history(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Permission denied")

    query = select(DownloadRequest).where(DownloadRequest.status != "pending").order_by(DownloadRequest.reviewed_at.desc())

    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar() or 0

    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    requests = result.scalars().all()

    items = []
    for req in requests:
        items.append({
            "id": req.id,
            "requester_email": req.requester_email,
            "requester_name": req.requester_name,
            "requested_data": req.requested_data,
            "data_format": req.data_format,
            "status": req.status,
            "review_comment": req.review_comment,
            "reviewed_at": req.reviewed_at.isoformat() if req.reviewed_at else None,
        })

    return ApiResponse(data={"items": items, "total": total, "page": page, "page_size": page_size})


@router.post("/{request_id}/review", response_model=ApiResponse)
async def review_download_request(
    request_id: int,
    data: ReviewDownloadRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Permission denied")

    if data.action not in ["approve", "reject"]:
        raise HTTPException(status_code=400, detail="Action must be approve or reject")

    if data.action == "reject" and not data.comment:
        raise HTTPException(status_code=400, detail="Rejection reason is required")

    result = await db.execute(select(DownloadRequest).where(DownloadRequest.id == request_id))
    req = result.scalar_one_or_none()

    if not req:
        raise HTTPException(status_code=404, detail="Download request not found")

    if req.status != "pending":
        raise HTTPException(status_code=400, detail="Request already reviewed")

    req.status = "approved" if data.action == "approve" else "rejected"
    req.reviewer_id = current_user.id
    req.review_comment = data.comment
    req.reviewed_at = utcnow()

    email_sent = False

    if data.action == "approve":
        attachment_content = None
        attachment_filename = None

        try:
            export_data = _parse_requested_data(req.requested_data)
            entries_result = await db.execute(
                select(TnEntry).where(TnEntry.name.in_(export_data["names"]))
            )
            entries = entries_result.scalars().all()

            if entries:
                if req.data_format == "embl":
                    content = _generate_embl_batch(entries)
                    attachment_filename = "tndb_export.embl"
                else:
                    content = _generate_fasta_batch(entries)
                    attachment_filename = "tndb_export.fasta"
                attachment_content = content.encode("utf-8")
        except Exception as e:
            logger.error("Failed to generate export: %s", e)

        from app.core.email import send_download_approved_email
        email_sent = send_download_approved_email(
            to_email=req.requester_email,
            requester_name=req.requester_name,
            data_description=req.requested_data,
            attachment_content=attachment_content,
            attachment_filename=attachment_filename,
        )

    elif data.action == "reject":
        from app.core.email import send_download_rejected_email
        email_sent = send_download_rejected_email(
            to_email=req.requester_email,
            requester_name=req.requester_name,
            data_description=req.requested_data,
            reason=data.comment or "",
        )

    await db.commit()

    return ApiResponse(data={
        "id": req.id,
        "status": req.status,
        "email_sent": email_sent,
    }, message=f"Request {req.status}, email {'sent' if email_sent else 'not configured'}")


def _parse_requested_data(requested_data: str) -> dict:
    names = [n.strip() for n in requested_data.split(",") if n.strip()]
    return {"names": names}


def _generate_fasta_batch(entries: list) -> str:
    content = ""
    for entry in entries:
        seq = entry.dna_sequence or ""
        content += f">{entry.name} {entry.family} transposon from {entry.origin or 'unknown'}\n"
        for i in range(0, len(seq), 80):
            content += seq[i:i+80] + "\n"
    return content


def _generate_embl_batch(entries: list) -> str:
    from app.api.v1.export import generate_embl
    content = ""
    for entry in entries:
        content += generate_embl(entry) + "\n"
    return content
