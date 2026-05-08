import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


class TestAdminStats:
    @pytest.mark.asyncio
    async def test_stats_admin(self, client: AsyncClient, admin_token):
        resp = await client.get("/api/v1/admin/stats", headers={
            "Authorization": f"Bearer {admin_token}"
        })
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert "tn_count" in data
        assert "family_count" in data
        assert "species_count" in data
        assert "pending_count" in data
        assert "task_count" in data
        assert "user_count" in data

    @pytest.mark.asyncio
    async def test_stats_with_data(self, client: AsyncClient, admin_token, tn_entry):
        resp = await client.get("/api/v1/admin/stats", headers={
            "Authorization": f"Bearer {admin_token}"
        })
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["tn_count"] >= 1
        assert data["user_count"] >= 1

    @pytest.mark.asyncio
    async def test_stats_unauthorized(self, client: AsyncClient):
        resp = await client.get("/api/v1/admin/stats")
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_stats_as_user(self, client: AsyncClient, user_token):
        resp = await client.get("/api/v1/admin/stats", headers={
            "Authorization": f"Bearer {user_token}"
        })
        assert resp.status_code == 403
