import asyncio
import os
from typing import AsyncGenerator
from unittest.mock import patch, MagicMock

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

# Mock Celery tasks before any app imports
_mock_task = MagicMock()
_mock_task.delay = MagicMock()
_patches = [
    patch("app.tasks.blast_task.run_blast_task", _mock_task),
    patch("app.tasks.minetn_task.run_minetn_task", _mock_task),
]
for _p in _patches:
    _p.start()

from app.core.database import Base, get_db
from app.core.security import get_password_hash

import app.models  # noqa: F401 — ensure all models loaded

TEST_DB_URL = os.getenv(
    "TEST_DATABASE_URL",
    "sqlite+aiosqlite:///./test.db",
)


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def engine():
    engine = create_async_engine(TEST_DB_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
async def async_session(engine) -> AsyncGenerator[AsyncSession, None]:
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session


@pytest.fixture
async def client(async_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    from app.main import app

    async def override_get_db():
        yield async_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
async def admin_user(async_session: AsyncSession):
    from app.models import User
    user = User(
        username="admin",
        email="admin@tndb.org",
        password_hash=get_password_hash("admin123"),
        role="admin",
        is_active=True,
    )
    async_session.add(user)
    await async_session.commit()
    await async_session.refresh(user)
    return user


@pytest.fixture
async def normal_user(async_session: AsyncSession):
    from app.models import User
    user = User(
        username="user1",
        email="user1@example.com",
        password_hash=get_password_hash("user123"),
        role="user",
        is_active=True,
    )
    async_session.add(user)
    await async_session.commit()
    await async_session.refresh(user)
    return user


async def login_as(client: AsyncClient, username: str, password: str) -> str:
    """Log in and return the auth token."""
    resp = await client.post("/api/v1/auth/login", json={
        "username": username,
        "password": password,
    })
    assert resp.status_code == 200
    return resp.json()["data"]["token"]


@pytest.fixture
async def admin_token(client: AsyncClient, admin_user) -> str:
    return await login_as(client, "admin", "admin123")


@pytest.fixture
async def user_token(client: AsyncClient, normal_user) -> str:
    return await login_as(client, "user1", "user123")


@pytest.fixture
async def tn_entry(async_session: AsyncSession, admin_user):
    from app.models import TnEntry
    entry = TnEntry(
        name="TEST-TE-1",
        family="Tc1-Mariner",
        tn_group="Tc1",
        origin="Drosophila melanogaster",
        mge_type="TE",
        length=1500,
        dna_sequence="ATCG" * 375,
        status="pending",
        submitted_by=admin_user.id,
    )
    async_session.add(entry)
    await async_session.commit()
    await async_session.refresh(entry)
    return entry


@pytest.fixture
async def approved_entry(async_session: AsyncSession, admin_user):
    from app.models import TnEntry
    entry = TnEntry(
        name="TEST-APPROVED",
        family="hAT",
        tn_group="hAT-Group",
        origin="Homo sapiens",
        mge_type="TE",
        length=2000,
        dna_sequence="GCTA" * 500,
        status="approved",
        submitted_by=admin_user.id,
    )
    async_session.add(entry)
    await async_session.commit()
    await async_session.refresh(entry)
    return entry
