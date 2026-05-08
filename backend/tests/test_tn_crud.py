import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


class TestTnList:
    @pytest.mark.asyncio
    async def test_list_empty(self, client: AsyncClient):
        resp = await client.get("/api/v1/tn")
        assert resp.status_code == 200
        data = resp.json()
        assert data["code"] == 200
        assert data["data"]["total"] == 0
        assert data["data"]["items"] == []

    @pytest.mark.asyncio
    async def test_list_with_data(self, client: AsyncClient, tn_entry):
        resp = await client.get("/api/v1/tn")
        assert resp.status_code == 200
        data = resp.json()
        assert data["data"]["total"] >= 1
        items = data["data"]["items"]
        names = [i["name"] for i in items]
        assert "TEST-TE-1" in names

    @pytest.mark.asyncio
    async def test_list_pagination(self, client: AsyncClient):
        resp = await client.get("/api/v1/tn?page=1&page_size=5")
        assert resp.status_code == 200
        data = resp.json()
        assert data["data"]["page"] == 1
        assert data["data"]["page_size"] == 5

    @pytest.mark.asyncio
    async def test_list_filter_by_family(self, client: AsyncClient, tn_entry):
        resp = await client.get("/api/v1/tn?family=Tc1-Mariner")
        assert resp.status_code == 200
        data = resp.json()
        assert all("Tc1-Mariner" in i.get("family", "") for i in data["data"]["items"])

    @pytest.mark.asyncio
    async def test_list_filter_by_status(self, client: AsyncClient, tn_entry):
        resp = await client.get("/api/v1/tn?status=pending")
        assert resp.status_code == 200
        data = resp.json()
        assert all(i["status"] == "pending" for i in data["data"]["items"])

        resp = await client.get("/api/v1/tn?status=approved")
        assert resp.status_code == 200
        assert resp.json()["data"]["total"] == 0

    @pytest.mark.asyncio
    async def test_list_keyword_search(self, client: AsyncClient, tn_entry):
        resp = await client.get("/api/v1/tn?keyword=TEST")
        assert resp.status_code == 200
        data = resp.json()
        assert data["data"]["total"] >= 1


class TestTnDetail:
    @pytest.mark.asyncio
    async def test_detail_found(self, client: AsyncClient, tn_entry):
        resp = await client.get(f"/api/v1/tn/{tn_entry.name}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["data"]["name"] == "TEST-TE-1"
        assert data["data"]["family"] == "Tc1-Mariner"

    @pytest.mark.asyncio
    async def test_detail_not_found(self, client: AsyncClient):
        resp = await client.get("/api/v1/tn/NONEXISTENT")
        assert resp.status_code == 404


class TestTnCreate:
    @pytest.mark.asyncio
    async def test_create_success(self, client: AsyncClient, admin_token):
        resp = await client.post("/api/v1/tn", json={
            "name": "NEW-TE",
            "family": "hAT",
            "tn_group": "hAT-Group",
            "origin": "Homo sapiens",
        }, headers={"Authorization": f"Bearer {admin_token}"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["data"]["name"] == "NEW-TE"
        assert data["data"]["family"] == "hAT"
        assert data["data"]["status"] == "pending"

    @pytest.mark.asyncio
    async def test_create_duplicate_name(self, client: AsyncClient, admin_token, tn_entry):
        resp = await client.post("/api/v1/tn", json={
            "name": "TEST-TE-1",
            "family": "hAT",
            "tn_group": "hAT-Group",
        }, headers={"Authorization": f"Bearer {admin_token}"})
        assert resp.status_code == 400

    @pytest.mark.asyncio
    async def test_create_missing_required(self, client: AsyncClient, admin_token):
        resp = await client.post("/api/v1/tn", json={
            "name": "Incomplete",
        }, headers={"Authorization": f"Bearer {admin_token}"})
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_create_no_auth(self, client: AsyncClient):
        # Public submission — no auth required
        resp = await client.post("/api/v1/tn", json={
            "name": "NOAUTH-TE",
            "family": "hAT",
            "tn_group": "hAT-Group",
        })
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_create_as_regular_user(self, client: AsyncClient, user_token):
        resp = await client.post("/api/v1/tn", json={
            "name": "USERTE",
            "family": "hAT",
            "tn_group": "hAT-Group",
        }, headers={"Authorization": f"Bearer {user_token}"})
        # Regular users can submit data
        assert resp.status_code == 200


class TestTnUpdate:
    @pytest.mark.asyncio
    async def test_update_success(self, client: AsyncClient, admin_token, tn_entry):
        resp = await client.put(f"/api/v1/tn/{tn_entry.name}", json={
            "family": "Updated-Family",
            "origin": "Updated Origin",
        }, headers={"Authorization": f"Bearer {admin_token}"})
        assert resp.status_code == 200
        assert resp.json()["data"]["family"] == "Updated-Family"

    @pytest.mark.asyncio
    async def test_update_not_found(self, client: AsyncClient, admin_token):
        resp = await client.put("/api/v1/tn/NONEXISTENT", json={
            "family": "DoesntMatter",
        }, headers={"Authorization": f"Bearer {admin_token}"})
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_update_unauthorized(self, client: AsyncClient, tn_entry):
        resp = await client.put(f"/api/v1/tn/{tn_entry.name}", json={
            "family": "Hacked",
        })
        assert resp.status_code == 401


class TestTnDelete:
    @pytest.mark.asyncio
    async def test_delete_success(self, client: AsyncClient, admin_token, tn_entry):
        resp = await client.delete(f"/api/v1/tn/{tn_entry.name}", headers={
            "Authorization": f"Bearer {admin_token}"
        })
        assert resp.status_code == 200
        # Verify deleted
        resp2 = await client.get(f"/api/v1/tn/{tn_entry.name}")
        assert resp2.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_not_found(self, client: AsyncClient, admin_token):
        resp = await client.delete("/api/v1/tn/NONEXISTENT", headers={
            "Authorization": f"Bearer {admin_token}"
        })
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_unauthorized(self, client: AsyncClient, tn_entry):
        resp = await client.delete(f"/api/v1/tn/{tn_entry.name}")
        assert resp.status_code == 401
