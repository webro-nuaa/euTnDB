from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.models import TnEntry, User, MineTnTask
from app.schemas import ApiResponse
from app.api.v1.auth import get_current_user

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/stats", response_model=ApiResponse)
async def get_admin_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Permission denied")
    
    tn_count = (await db.execute(select(func.count(TnEntry.id)))).scalar() or 0
    family_count = (await db.execute(
        select(func.count(func.distinct(TnEntry.family)))
    )).scalar() or 0
    origin_count = (await db.execute(
        select(func.count(func.distinct(TnEntry.origin))).where(TnEntry.origin != None)
    )).scalar() or 0
    pending_count = (await db.execute(
        select(func.count(TnEntry.id)).where(TnEntry.status == "pending")
    )).scalar() or 0
    task_count = (await db.execute(
        select(func.count(MineTnTask.id)).where(MineTnTask.status == "running")
    )).scalar() or 0
    user_count = (await db.execute(select(func.count(User.id)))).scalar() or 0
    
    return ApiResponse(data={
        "tn_count": tn_count,
        "family_count": family_count,
        "species_count": origin_count,
        "pending_count": pending_count,
        "task_count": task_count,
        "user_count": user_count
    })
