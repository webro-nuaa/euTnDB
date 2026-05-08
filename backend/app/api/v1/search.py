from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from typing import Optional

from app.core.database import get_db
from app.models import TnEntry
from app.schemas import TnEntryResponse, TnListResponse, ApiResponse

router = APIRouter(prefix="/search", tags=["Search"])


@router.get("", response_model=ApiResponse[TnListResponse])
async def search_tn(
    keyword: Optional[str] = None,
    family: Optional[str] = None,
    tn_group: Optional[str] = None,
    origin: Optional[str] = None,
    mge_type: Optional[str] = None,
    min_length: Optional[int] = None,
    max_length: Optional[int] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    query = select(TnEntry)

    if keyword:
        query = query.where(
            or_(
                TnEntry.name.ilike(f"%{keyword}%"),
                TnEntry.family.ilike(f"%{keyword}%"),
                TnEntry.tn_group.ilike(f"%{keyword}%"),
                TnEntry.origin.ilike(f"%{keyword}%"),
                TnEntry.accession_number.ilike(f"%{keyword}%"),
            )
        )

    if family:
        query = query.where(TnEntry.family == family)

    if tn_group:
        query = query.where(TnEntry.tn_group == tn_group)

    if origin:
        query = query.where(TnEntry.origin.ilike(f"%{origin}%"))

    if mge_type:
        query = query.where(TnEntry.mge_type == mge_type)

    if min_length is not None:
        query = query.where(TnEntry.length >= min_length)

    if max_length is not None:
        query = query.where(TnEntry.length <= max_length)

    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar() or 0

    query = query.offset((page - 1) * page_size).limit(page_size)
    query = query.order_by(TnEntry.created_at.desc())

    result = await db.execute(query)
    entries = result.scalars().all()

    items = [TnEntryResponse.model_validate(entry) for entry in entries]

    return ApiResponse(data=TnListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size
    ))


@router.get("/suggestions", response_model=ApiResponse)
async def get_search_suggestions(
    keyword: str,
    db: AsyncSession = Depends(get_db)
):
    suggestions = []

    name_result = await db.execute(
        select(TnEntry.name, TnEntry.family)
        .where(TnEntry.name.ilike(f"%{keyword}%"))
        .limit(5)
    )
    for row in name_result.all():
        suggestions.append({"type": "name", "value": row.name, "label": f"{row.name} - {row.family}"})

    fam_result = await db.execute(
        select(TnEntry.family)
        .where(TnEntry.family.ilike(f"%{keyword}%"))
        .distinct()
        .limit(5)
    )
    for row in fam_result.all():
        suggestions.append({"type": "family", "value": row.family, "label": row.family})

    grp_result = await db.execute(
        select(TnEntry.tn_group)
        .where(TnEntry.tn_group.ilike(f"%{keyword}%"))
        .distinct()
        .limit(5)
    )
    for row in grp_result.all():
        suggestions.append({"type": "tn_group", "value": row.tn_group, "label": row.tn_group})

    origin_result = await db.execute(
        select(TnEntry.origin)
        .where(TnEntry.origin.ilike(f"%{keyword}%"))
        .distinct()
        .limit(5)
    )
    for row in origin_result.all():
        suggestions.append({"type": "origin", "value": row.origin, "label": row.origin})

    return ApiResponse(data=suggestions[:10])
