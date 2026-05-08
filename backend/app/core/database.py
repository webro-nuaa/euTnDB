import logging
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings


def utcnow() -> datetime:
    return datetime.now(timezone.utc)

logger = logging.getLogger("tndb")

engine = create_async_engine(settings.DATABASE_URL, echo=False, pool_pre_ping=True)

async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncSession:
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    import app.models  # noqa: F401 — ensure all models are loaded

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    logger.info("Database tables verified")
