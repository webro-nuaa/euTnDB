from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
from pydantic import BaseModel

from app.core.database import get_db
from app.models import User
from app.schemas import UserResponse, ApiResponse
from app.core.security import get_password_hash
from app.api.v1.auth import get_current_user

router = APIRouter(prefix="/admin/users", tags=["User Management"])


class UserCreateRequest(BaseModel):
    username: str
    email: str
    password: str
    role: str = "user"
    institution: Optional[str] = None


class UserUpdateRequest(BaseModel):
    email: Optional[str] = None
    role: Optional[str] = None
    institution: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None


@router.get("", response_model=ApiResponse)
async def get_user_list(
    keyword: Optional[str] = None,
    role: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Permission denied")

    query = select(User)

    if keyword:
        query = query.where(
            User.username.ilike(f"%{keyword}%") |
            User.email.ilike(f"%{keyword}%")
        )
    if role:
        query = query.where(User.role == role)

    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar() or 0

    query = query.offset((page - 1) * page_size).limit(page_size)
    query = query.order_by(User.created_at.desc())

    result = await db.execute(query)
    users = result.scalars().all()

    items = [UserResponse.model_validate(u).model_dump() for u in users]

    return ApiResponse(data={"items": items, "total": total, "page": page, "page_size": page_size})


@router.post("", response_model=ApiResponse[UserResponse])
async def create_user(
    data: UserCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Permission denied")

    result = await db.execute(select(User).where(User.username == data.username))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Username already exists")

    result = await db.execute(select(User).where(User.email == data.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        username=data.username,
        email=data.email,
        password_hash=get_password_hash(data.password),
        role=data.role,
        institution=data.institution
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    return ApiResponse(data=UserResponse.model_validate(user))


@router.put("/{user_id}", response_model=ApiResponse[UserResponse])
async def update_user(
    user_id: int,
    data: UserUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Permission denied")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if data.email is not None:
        user.email = data.email
    if data.role is not None:
        user.role = data.role
    if data.institution is not None:
        user.institution = data.institution
    if data.is_active is not None:
        user.is_active = data.is_active
    if data.password is not None:
        user.password_hash = get_password_hash(data.password)

    await db.commit()
    await db.refresh(user)

    return ApiResponse(data=UserResponse.model_validate(user))


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Permission denied")

    if current_user.id == user_id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    await db.delete(user)
    await db.commit()

    return ApiResponse(data=None, message="Deleted successfully")
