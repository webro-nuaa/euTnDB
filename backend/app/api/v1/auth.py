import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel

from app.core.database import get_db
from app.core.security import verify_password, create_access_token, decode_access_token, get_password_hash
from app.models import User
from app.schemas import UserCreate, UserResponse, LoginRequest, TokenResponse, ApiResponse

logger = logging.getLogger("tndb.auth")
router = APIRouter(prefix="/auth", tags=["Authentication"])

COOKIE_NAME = "tndb_token"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


class ChangePasswordRequest(BaseModel):
    oldPassword: str
    newPassword: str


async def get_current_user(
    request: Request,
    token: str | None = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Try cookie first, then Authorization header
    token = token or request.cookies.get(COOKIE_NAME)
    if not token:
        raise credentials_exception

    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    username: Optional[str] = payload.get("sub")
    if username is None:
        raise credentials_exception

    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()

    if user is None or not user.is_active:
        raise credentials_exception

    return user


@router.post("/register", response_model=ApiResponse[UserResponse])
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    raise HTTPException(status_code=403, detail="Registration is not available")


@router.post("/login", response_model=ApiResponse[TokenResponse])
async def login(response: Response, login_data: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.username == login_data.username))
    user = result.scalar_one_or_none()

    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(status_code=400, detail="User account is disabled")

    token = create_access_token(user.username)

    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        httponly=True,
        secure=False,  # Set True in production with HTTPS
        samesite="lax",
        max_age=60 * 60 * 24 * 7,  # 7 days
        path="/",
    )

    logger.info("User '%s' logged in", user.username)
    return ApiResponse(data=TokenResponse(
        token=token,
        user=UserResponse.model_validate(user),
    ))


@router.get("/me", response_model=ApiResponse[UserResponse])
async def get_me(current_user: User = Depends(get_current_user)):
    return ApiResponse(data=UserResponse.model_validate(current_user))


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(key=COOKIE_NAME, path="/")
    return ApiResponse(message="Logged out successfully")


@router.post("/change-password")
async def change_password(
    data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not verify_password(data.oldPassword, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Old password is incorrect",
        )

    if len(data.newPassword) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be at least 6 characters",
        )

    current_user.password_hash = get_password_hash(data.newPassword)
    await db.commit()

    logger.info("User '%s' changed password", current_user.username)
    return ApiResponse(message="Password changed successfully")
