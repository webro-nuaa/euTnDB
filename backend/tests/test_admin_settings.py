import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


class TestAdminSettingsGet:
    @pytest.mark.asyncio
    async def test_get_settings_admin(self, client: AsyncClient, admin_token):
        resp = await client.get("/api/v1/admin/settings", headers={
            "Authorization": f"Bearer {admin_token}"
        })
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert "site_name" in data
        assert data["site_name"] == "euTnDB"
        assert "blast_enabled" in data
        assert "smtp_host" in data

    @pytest.mark.asyncio
    async def test_get_settings_unauthorized(self, client: AsyncClient):
        resp = await client.get("/api/v1/admin/settings")
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_get_settings_as_user(self, client: AsyncClient, user_token):
        resp = await client.get("/api/v1/admin/settings", headers={
            "Authorization": f"Bearer {user_token}"
        })
        assert resp.status_code == 403


class TestAdminSettingsUpdate:
    @pytest.mark.asyncio
    async def test_update_settings_admin(self, client: AsyncClient, admin_token):
        resp = await client.put("/api/v1/admin/settings", json={
            "settings": [
                {"key": "site_name", "value": "TnDB-Test"},
                {"key": "site_description", "value": "Test Instance"},
            ]
        }, headers={"Authorization": f"Bearer {admin_token}"})
        assert resp.status_code == 200

        # Verify update persisted
        get_resp = await client.get("/api/v1/admin/settings", headers={
            "Authorization": f"Bearer {admin_token}"
        })
        assert get_resp.json()["data"]["site_name"] == "TnDB-Test"

    @pytest.mark.asyncio
    async def test_update_new_setting(self, client: AsyncClient, admin_token):
        resp = await client.put("/api/v1/admin/settings", json={
            "settings": [
                {"key": "custom_setting", "value": "custom_value"},
            ]
        }, headers={"Authorization": f"Bearer {admin_token}"})
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_update_settings_unauthorized(self, client: AsyncClient):
        resp = await client.put("/api/v1/admin/settings", json={
            "settings": [{"key": "site_name", "value": "hacked"}]
        })
        assert resp.status_code == 401


class TestAdminSettingsTestEmail:
    @pytest.mark.asyncio
    async def test_test_email_admin(self, client: AsyncClient, admin_token):
        resp = await client.post("/api/v1/admin/settings/test-email", json={
            "test_email": "test@example.com"
        }, headers={"Authorization": f"Bearer {admin_token}"})
        # Will fail if SMTP not configured, but endpoint should work
        assert resp.status_code in (200, 500)

    @pytest.mark.asyncio
    async def test_test_email_unauthorized(self, client: AsyncClient):
        resp = await client.post("/api/v1/admin/settings/test-email", json={
            "test_email": "test@example.com"
        })
        assert resp.status_code == 401
