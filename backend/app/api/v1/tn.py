from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from typing import Optional

from app.core.database import get_db
from app.models import TnEntry, User
from app.schemas import TnEntryCreate, TnEntryUpdate, TnEntryResponse, TnListResponse, ApiResponse
from app.api.v1.auth import get_current_user

router = APIRouter(prefix="/tn", tags=["Tn Data"])


@router.get("", response_model=ApiResponse[TnListResponse])
async def get_tn_list(
    keyword: Optional[str] = None,
    family: Optional[str] = None,
    tn_group: Optional[str] = None,
    origin: Optional[str] = None,
    mge_type: Optional[str] = None,
    status: Optional[str] = None,
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

    if status:
        query = query.where(TnEntry.status == status)

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


@router.get("/{tn_id}", response_model=ApiResponse[TnEntryResponse])
async def get_tn_detail(tn_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(TnEntry).where(TnEntry.name == tn_id)
    )
    entry = result.scalar_one_or_none()

    if not entry:
        raise HTTPException(status_code=404, detail="Tn entry not found")

    return ApiResponse(data=TnEntryResponse.model_validate(entry))


@router.post("", response_model=ApiResponse[TnEntryResponse])
async def create_tn(
    tn_data: TnEntryCreate,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(TnEntry).where(TnEntry.name == tn_data.name))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Name already exists")

    entry = TnEntry(**tn_data.model_dump())

    db.add(entry)
    await db.commit()
    await db.refresh(entry)

    return ApiResponse(data=TnEntryResponse.model_validate(entry))


@router.put("/{tn_id}", response_model=ApiResponse[TnEntryResponse])
async def update_tn(
    tn_id: str,
    tn_data: TnEntryUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Permission denied")

    result = await db.execute(
        select(TnEntry).where(TnEntry.name == tn_id)
    )
    entry = result.scalar_one_or_none()

    if not entry:
        raise HTTPException(status_code=404, detail="Tn entry not found")

    update_data = tn_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(entry, key, value)

    await db.commit()
    await db.refresh(entry)

    return ApiResponse(data=TnEntryResponse.model_validate(entry))


@router.delete("/{tn_id}")
async def delete_tn(
    tn_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Permission denied")

    result = await db.execute(select(TnEntry).where(TnEntry.name == tn_id))
    entry = result.scalar_one_or_none()

    if not entry:
        raise HTTPException(status_code=404, detail="Tn entry not found")

    await db.delete(entry)
    await db.commit()

    return ApiResponse(message="Deleted successfully")
