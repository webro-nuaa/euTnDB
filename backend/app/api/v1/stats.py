from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.models import TnEntry
from app.schemas.common import ApiResponse

router = APIRouter(prefix="/stats", tags=["Statistics"])


@router.get("/overview")
async def get_overview(db: AsyncSession = Depends(get_db)):
    tn_count = (await db.execute(select(func.count(TnEntry.id)))).scalar() or 0
    origin_count = (await db.execute(
        select(func.count(func.distinct(TnEntry.origin))).where(TnEntry.origin != None)
    )).scalar() or 0
    family_count = (await db.execute(
        select(func.count(func.distinct(TnEntry.family))).where(TnEntry.family != None)
    )).scalar() or 0

    return ApiResponse(data={
        "tn_count": tn_count,
        "species_count": origin_count,
        "family_count": family_count,
    })


@router.get("/family")
async def get_family_stats(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(
            TnEntry.family,
            func.count(TnEntry.id).label("count")
        )
        .group_by(TnEntry.family)
        .order_by(func.count(TnEntry.id).desc())
    )

    all_stats = [{"family": row.family, "count": row.count} for row in result.all()]

    top_n = 10
    if len(all_stats) > top_n:
        top = all_stats[:top_n]
        other_count = sum(item["count"] for item in all_stats[top_n:])
        top.append({"family": "Other", "count": other_count})
        return ApiResponse(data=top)

    return ApiResponse(data=all_stats)


@router.get("/species")
async def get_species_stats(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(
            TnEntry.origin,
            func.count(TnEntry.id).label("count")
        )
        .where(TnEntry.origin != None)
        .group_by(TnEntry.origin)
        .order_by(func.count(TnEntry.id).desc())
        .limit(20)
    )

    stats = [{"species": row.origin, "count": row.count} for row in result.all()]

    return ApiResponse(data=stats)


@router.get("/status")
async def get_status_stats(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(
            TnEntry.status,
            func.count(TnEntry.id).label("count")
        )
        .group_by(TnEntry.status)
        .order_by(func.count(TnEntry.id).desc())
    )

    stats = [{"status": row.status, "count": row.count} for row in result.all()]

    return ApiResponse(data=stats)
