import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


class TestUserAdminList:
    @pytest.mark.asyncio
    async def test_list_users_admin(self, client: AsyncClient, admin_token, normal_user):
        resp = await client.get("/api/v1/admin/users", headers={
            "Authorization": f"Bearer {admin_token}"
        })
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["total"] >= 1
        usernames = [u["username"] for u in data["items"]]
        assert "user1" in usernames

    @pytest.mark.asyncio
    async def test_list_users_pagination(self, client: AsyncClient, admin_token):
        resp = await client.get("/api/v1/admin/users?page=1&page_size=5", headers={
            "Authorization": f"Bearer {admin_token}"
        })
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_list_users_filter_role(self, client: AsyncClient, admin_token, normal_user):
        resp = await client.get("/api/v1/admin/users?role=admin", headers={
            "Authorization": f"Bearer {admin_token}"
        })
        assert resp.status_code == 200
        items = resp.json()["data"]["items"]
        for u in items:
            assert u["role"] == "admin"

    @pytest.mark.asyncio
    async def test_list_users_search(self, client: AsyncClient, admin_token, normal_user):
        resp = await client.get("/api/v1/admin/users?keyword=user1", headers={
            "Authorization": f"Bearer {admin_token}"
        })
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["total"] >= 1

    @pytest.mark.asyncio
    async def test_list_users_unauthorized(self, client: AsyncClient):
        resp = await client.get("/api/v1/admin/users")
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_list_users_as_user(self, client: AsyncClient, user_token):
        resp = await client.get("/api/v1/admin/users", headers={
            "Authorization": f"Bearer {user_token}"
        })
        assert resp.status_code == 403


class TestUserAdminCreate:
    @pytest.mark.asyncio
    async def test_create_user_admin(self, client: AsyncClient, admin_token):
        resp = await client.post("/api/v1/admin/users", json={
            "username": "createdbyadmin",
            "email": "created@admin.com",
            "password": "secure123",
            "role": "user",
        }, headers={"Authorization": f"Bearer {admin_token}"})
        assert resp.status_code == 200
        assert resp.json()["data"]["username"] == "createdbyadmin"

    @pytest.mark.asyncio
    async def test_create_user_duplicate_username(self, client: AsyncClient, admin_token, normal_user):
        resp = await client.post("/api/v1/admin/users", json={
            "username": "user1",
            "email": "newemail@test.com",
            "password": "secure123",
        }, headers={"Authorization": f"Bearer {admin_token}"})
        assert resp.status_code == 400

    @pytest.mark.asyncio
    async def test_create_user_duplicate_email(self, client: AsyncClient, admin_token, normal_user):
        resp = await client.post("/api/v1/admin/users", json={
            "username": "newname",
            "email": "user1@example.com",
            "password": "secure123",
        }, headers={"Authorization": f"Bearer {admin_token}"})
        assert resp.status_code == 400

    @pytest.mark.asyncio
    async def test_create_user_unauthorized(self, client: AsyncClient):
        resp = await client.post("/api/v1/admin/users", json={
            "username": "hacker",
            "email": "hacker@evil.com",
            "password": "hack123",
        })
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_create_user_as_user(self, client: AsyncClient, user_token):
        resp = await client.post("/api/v1/admin/users", json={
            "username": "createdbyuser",
            "email": "usercreated@test.com",
            "password": "secure123",
        }, headers={"Authorization": f"Bearer {user_token}"})
        assert resp.status_code == 403


class TestUserAdminUpdate:
    @pytest.mark.asyncio
    async def test_update_user(self, client: AsyncClient, admin_token, normal_user):
        resp = await client.put(f"/api/v1/admin/users/{normal_user.id}", json={
            "role": "admin",
            "institution": "Updated Inst",
        }, headers={"Authorization": f"Bearer {admin_token}"})
        assert resp.status_code == 200
        assert resp.json()["data"]["role"] == "admin"

    @pytest.mark.asyncio
    async def test_update_user_not_found(self, client: AsyncClient, admin_token):
        resp = await client.put("/api/v1/admin/users/99999", json={
            "role": "admin",
        }, headers={"Authorization": f"Bearer {admin_token}"})
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_update_user_unauthorized(self, client: AsyncClient, normal_user):
        resp = await client.put(f"/api/v1/admin/users/{normal_user.id}", json={
            "role": "admin",
        })
        assert resp.status_code == 401


class TestUserAdminDelete:
    @pytest.mark.asyncio
    async def test_delete_user(self, client: AsyncClient, admin_token, normal_user):
        resp = await client.delete(f"/api/v1/admin/users/{normal_user.id}", headers={
            "Authorization": f"Bearer {admin_token}"
        })
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_delete_self(self, client: AsyncClient, admin_token, admin_user):
        resp = await client.delete(f"/api/v1/admin/users/{admin_user.id}", headers={
            "Authorization": f"Bearer {admin_token}"
        })
        assert resp.status_code == 400

    @pytest.mark.asyncio
    async def test_delete_not_found(self, client: AsyncClient, admin_token):
        resp = await client.delete("/api/v1/admin/users/99999", headers={
            "Authorization": f"Bearer {admin_token}"
        })
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_unauthorized(self, client: AsyncClient):
        resp = await client.delete("/api/v1/admin/users/1")
        assert resp.status_code == 401
