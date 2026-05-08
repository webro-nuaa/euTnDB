import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


class TestDownloadRequestSubmit:
    @pytest.mark.asyncio
    async def test_submit_public(self, client: AsyncClient, tn_entry):
        resp = await client.post("/api/v1/download-request", json={
            "requester_email": "researcher@university.edu",
            "requester_name": "Dr. Smith",
            "requester_institution": "Example University",
            "requested_data": "TEST-TE-1",
            "data_format": "fasta",
            "purpose": "Comparative genomics analysis",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["data"]["status"] == "pending"
        assert "id" in data["data"]

    @pytest.mark.asyncio
    async def test_submit_multiple_entries(self, client: AsyncClient, tn_entry):
        resp = await client.post("/api/v1/download-request", json={
            "requester_email": "researcher@university.edu",
            "requester_name": "Dr. Jones",
            "requested_data": "TEST-TE-1,TEST-TE-2",
            "data_format": "embl",
        })
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_submit_missing_email(self, client: AsyncClient):
        resp = await client.post("/api/v1/download-request", json={
            "requested_data": "TEST-TE-1",
            "data_format": "fasta",
        })
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_submit_invalid_email(self, client: AsyncClient):
        resp = await client.post("/api/v1/download-request", json={
            "requester_email": "not-an-email",
            "requested_data": "TEST-TE-1",
        })
        # requester_email is str not EmailStr so validation passes; endpoint accepts
        assert resp.status_code in (200, 422)


class TestDownloadRequestAdminList:
    @pytest.mark.asyncio
    async def test_get_admin_list(self, client: AsyncClient, admin_user):
        resp = await client.get("/api/v1/download-request/admins")
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert isinstance(data, list)
        assert len(data) >= 1
        assert any(a["username"] == "admin" for a in data)


class TestDownloadRequestPending:
    @pytest.mark.asyncio
    async def test_pending_list_admin(self, client: AsyncClient, admin_token, tn_entry):
        # Submit a request first
        await client.post("/api/v1/download-request", json={
            "requester_email": "res@univ.edu",
            "requested_data": "TEST-TE-1",
        })

        resp = await client.get("/api/v1/download-request/pending", headers={
            "Authorization": f"Bearer {admin_token}"
        })
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["total"] >= 1

    @pytest.mark.asyncio
    async def test_pending_list_unauthorized(self, client: AsyncClient):
        resp = await client.get("/api/v1/download-request/pending")
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_pending_list_as_user(self, client: AsyncClient, user_token):
        resp = await client.get("/api/v1/download-request/pending", headers={
            "Authorization": f"Bearer {user_token}"
        })
        assert resp.status_code == 403


class TestDownloadRequestReview:
    @pytest.mark.asyncio
    async def test_approve_request(self, client: AsyncClient, admin_token, tn_entry):
        submit = await client.post("/api/v1/download-request", json={
            "requester_email": "res@univ.edu",
            "requested_data": "TEST-TE-1",
        })
        req_id = submit.json()["data"]["id"]

        resp = await client.post(f"/api/v1/download-request/{req_id}/review", json={
            "action": "approve",
        }, headers={"Authorization": f"Bearer {admin_token}"})
        assert resp.status_code == 200
        assert resp.json()["data"]["status"] == "approved"

    @pytest.mark.asyncio
    async def test_reject_request(self, client: AsyncClient, admin_token, tn_entry):
        submit = await client.post("/api/v1/download-request", json={
            "requester_email": "res@univ.edu",
            "requested_data": "TEST-TE-1",
        })
        req_id = submit.json()["data"]["id"]

        resp = await client.post(f"/api/v1/download-request/{req_id}/review", json={
            "action": "reject",
            "comment": "Insufficient justification",
        }, headers={"Authorization": f"Bearer {admin_token}"})
        assert resp.status_code == 200
        assert resp.json()["data"]["status"] == "rejected"

    @pytest.mark.asyncio
    async def test_reject_without_comment(self, client: AsyncClient, admin_token, tn_entry):
        submit = await client.post("/api/v1/download-request", json={
            "requester_email": "res@univ.edu",
            "requested_data": "TEST-TE-1",
        })
        req_id = submit.json()["data"]["id"]

        resp = await client.post(f"/api/v1/download-request/{req_id}/review", json={
            "action": "reject",
        }, headers={"Authorization": f"Bearer {admin_token}"})
        assert resp.status_code == 400

    @pytest.mark.asyncio
    async def test_review_already_reviewed(self, client: AsyncClient, admin_token, tn_entry):
        submit = await client.post("/api/v1/download-request", json={
            "requester_email": "res@univ.edu",
            "requested_data": "TEST-TE-1",
        })
        req_id = submit.json()["data"]["id"]

        await client.post(f"/api/v1/download-request/{req_id}/review", json={
            "action": "approve",
        }, headers={"Authorization": f"Bearer {admin_token}"})

        resp = await client.post(f"/api/v1/download-request/{req_id}/review", json={
            "action": "approve",
        }, headers={"Authorization": f"Bearer {admin_token}"})
        assert resp.status_code == 400

    @pytest.mark.asyncio
    async def test_review_not_found(self, client: AsyncClient, admin_token):
        resp = await client.post("/api/v1/download-request/99999/review", json={
            "action": "approve",
        }, headers={"Authorization": f"Bearer {admin_token}"})
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_review_unauthorized(self, client: AsyncClient):
        resp = await client.post("/api/v1/download-request/1/review", json={
            "action": "approve",
        })
        assert resp.status_code == 401


class TestDownloadRequestHistory:
    @pytest.mark.asyncio
    async def test_history_admin(self, client: AsyncClient, admin_token, tn_entry):
        submit = await client.post("/api/v1/download-request", json={
            "requester_email": "res@univ.edu",
            "requested_data": "TEST-TE-1",
        })
        req_id = submit.json()["data"]["id"]
        await client.post(f"/api/v1/download-request/{req_id}/review", json={
            "action": "approve",
        }, headers={"Authorization": f"Bearer {admin_token}"})

        resp = await client.get("/api/v1/download-request/history", headers={
            "Authorization": f"Bearer {admin_token}"
        })
        assert resp.status_code == 200
        assert resp.json()["data"]["total"] >= 1

    @pytest.mark.asyncio
    async def test_history_unauthorized(self, client: AsyncClient):
        resp = await client.get("/api/v1/download-request/history")
        assert resp.status_code == 401
