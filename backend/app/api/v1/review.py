from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional

from app.core.database import get_db, utcnow
from app.models import TnEntry, ReviewHistory, User
from app.schemas import ReviewAction, ReviewHistoryResponse, TnEntryResponse, ApiResponse
from app.api.v1.auth import get_current_user

router = APIRouter(prefix="/review", tags=["Review"])


@router.get("/pending", response_model=ApiResponse)
async def get_pending_reviews(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Permission denied")

    query = select(TnEntry).where(TnEntry.status == "pending")

    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar() or 0

    query = query.offset((page - 1) * page_size).limit(page_size)
    query = query.order_by(TnEntry.created_at.asc())

    result = await db.execute(query)
    entries = result.scalars().all()

    items = [TnEntryResponse.model_validate(entry).model_dump() for entry in entries]

    return ApiResponse(data={"items": items, "total": total, "page": page, "page_size": page_size})


@router.post("/{tn_id}", response_model=ApiResponse)
async def review_tn(
    tn_id: str,
    action_data: ReviewAction,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Permission denied")

    if action_data.action not in ["approve", "reject"]:
        raise HTTPException(status_code=400, detail="Action must be approve or reject")

    result = await db.execute(select(TnEntry).where(TnEntry.name == tn_id))
    entry = result.scalar_one_or_none()

    if not entry:
        raise HTTPException(status_code=404, detail="Tn entry not found")

    if entry.status != "pending":
        raise HTTPException(status_code=400, detail="Entry is not pending review")

    old_status = entry.status
    entry.status = "approved" if action_data.action == "approve" else "rejected"
    entry.reviewed_by = current_user.id
    entry.reviewed_at = utcnow()

    history = ReviewHistory(
        tn_entry_id=entry.id,
        reviewer_id=current_user.id,
        action=action_data.action,
        comment=action_data.comment,
        old_data={"status": old_status},
        new_data={"status": entry.status}
    )
    db.add(history)

    await db.commit()

    return ApiResponse(data=None, message="Review completed")


@router.get("/history", response_model=ApiResponse)
async def get_review_history(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Permission denied")

    query = select(ReviewHistory).order_by(ReviewHistory.created_at.desc())

    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar() or 0

    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    histories = result.scalars().all()

    items = [ReviewHistoryResponse.model_validate(h).model_dump() for h in histories]

    return ApiResponse(data={"items": items, "total": total, "page": page, "page_size": page_size})
