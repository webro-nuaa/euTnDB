import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.rate_limit import RateLimitMiddleware
from app.api.v1 import api_router

logger = logging.getLogger("tndb")


@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.core.logging import setup_logging
    setup_logging()
    from app.core.database import init_db
    await init_db()
    await _ensure_default_admin()
    yield
    from app.core.redis import close_redis
    await close_redis()


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type", "Authorization"],
)

app.add_middleware(RateLimitMiddleware)

app.include_router(api_router, prefix=settings.API_V1_PREFIX)


async def _ensure_default_admin():
    from sqlalchemy import select
    from app.core.database import async_session_maker
    from app.models import User
    from app.core.security import get_password_hash

    if not settings.ADMIN_PASSWORD:
        logger.warning("ADMIN_PASSWORD not set — skipping admin creation")
        return

    async with async_session_maker() as session:
        result = await session.execute(select(User).where(User.role == "admin").limit(1))
        if result.scalar_one_or_none():
            return
        admin = User(
            username=settings.ADMIN_USERNAME,
            email=settings.ADMIN_EMAIL,
            password_hash=get_password_hash(settings.ADMIN_PASSWORD),
            role="admin",
            is_active=True,
        )
        session.add(admin)
        await session.commit()
        logger.info("Default admin account created")


@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": settings.VERSION}
