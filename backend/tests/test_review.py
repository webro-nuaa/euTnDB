import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


class TestReviewPending:
    @pytest.mark.asyncio
    async def test_pending_list_admin(self, client: AsyncClient, admin_token, tn_entry):
        resp = await client.get("/api/v1/review/pending", headers={
            "Authorization": f"Bearer {admin_token}"
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["code"] == 200
        items = data["data"]["items"]
        assert len(items) >= 1
        names = [i["name"] for i in items]
        assert "TEST-TE-1" in names

    @pytest.mark.asyncio
    async def test_pending_list_unauthorized(self, client: AsyncClient):
        resp = await client.get("/api/v1/review/pending")
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_pending_list_as_user(self, client: AsyncClient, user_token):
        resp = await client.get("/api/v1/review/pending", headers={
            "Authorization": f"Bearer {user_token}"
        })
        assert resp.status_code == 403

    @pytest.mark.asyncio
    async def test_pending_pagination(self, client: AsyncClient, admin_token):
        resp = await client.get("/api/v1/review/pending?page=1&page_size=5", headers={
            "Authorization": f"Bearer {admin_token}"
        })
        assert resp.status_code == 200
        assert resp.json()["data"]["page"] == 1


class TestReviewAction:
    @pytest.mark.asyncio
    async def test_approve_entry(self, client: AsyncClient, admin_token, tn_entry):
        resp = await client.post(f"/api/v1/review/{tn_entry.name}", json={
            "action": "approve",
            "comment": "Looks good",
        }, headers={"Authorization": f"Bearer {admin_token}"})
        assert resp.status_code == 200
        assert resp.json()["message"] == "Review completed"

    @pytest.mark.asyncio
    async def test_reject_entry(self, client: AsyncClient, admin_token, tn_entry):
        resp = await client.post(f"/api/v1/review/{tn_entry.name}", json={
            "action": "reject",
            "comment": "Insufficient data",
        }, headers={"Authorization": f"Bearer {admin_token}"})
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_review_already_reviewed(self, client: AsyncClient, admin_token, tn_entry):
        # Approve first
        await client.post(f"/api/v1/review/{tn_entry.name}", json={
            "action": "approve",
        }, headers={"Authorization": f"Bearer {admin_token}"})
        # Try again
        resp = await client.post(f"/api/v1/review/{tn_entry.name}", json={
            "action": "approve",
        }, headers={"Authorization": f"Bearer {admin_token}"})
        assert resp.status_code == 400

    @pytest.mark.asyncio
    async def test_review_invalid_action(self, client: AsyncClient, admin_token, tn_entry):
        resp = await client.post(f"/api/v1/review/{tn_entry.name}", json={
            "action": "delete",
        }, headers={"Authorization": f"Bearer {admin_token}"})
        # Pydantic validation catches at 422; app-level check at 400 — both valid
        assert resp.status_code in (400, 422)

    @pytest.mark.asyncio
    async def test_review_not_found(self, client: AsyncClient, admin_token):
        resp = await client.post("/api/v1/review/NONEXISTENT", json={
            "action": "approve",
        }, headers={"Authorization": f"Bearer {admin_token}"})
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_review_unauthorized(self, client: AsyncClient, tn_entry):
        resp = await client.post(f"/api/v1/review/{tn_entry.name}", json={
            "action": "approve",
        })
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_review_as_user(self, client: AsyncClient, user_token, tn_entry):
        resp = await client.post(f"/api/v1/review/{tn_entry.name}", json={
            "action": "approve",
        }, headers={"Authorization": f"Bearer {user_token}"})
        assert resp.status_code == 403


class TestReviewHistory:
    @pytest.mark.asyncio
    async def test_history_after_review(self, client: AsyncClient, admin_token, tn_entry):
        # Approve to create history
        await client.post(f"/api/v1/review/{tn_entry.name}", json={
            "action": "approve",
        }, headers={"Authorization": f"Bearer {admin_token}"})

        resp = await client.get("/api/v1/review/history", headers={
            "Authorization": f"Bearer {admin_token}"
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["data"]["total"] >= 1

    @pytest.mark.asyncio
    async def test_history_unauthorized(self, client: AsyncClient):
        resp = await client.get("/api/v1/review/history")
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_history_as_user(self, client: AsyncClient, user_token):
        resp = await client.get("/api/v1/review/history", headers={
            "Authorization": f"Bearer {user_token}"
        })
        assert resp.status_code == 403
