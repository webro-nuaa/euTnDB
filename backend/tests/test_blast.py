import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


class TestBlastSubmit:
    @pytest.mark.asyncio
    async def test_submit_blast_dna(self, client: AsyncClient):
        resp = await client.post("/api/v1/blast", json={
            "sequence": "ATCGATCGATCGATCGATCG",
            "program": "blastn",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["code"] == 200
        assert "task_id" in data["data"]

    @pytest.mark.asyncio
    async def test_submit_blast_protein(self, client: AsyncClient):
        resp = await client.post("/api/v1/blast", json={
            "sequence": "MVLSPADKTNVKAAWGKVGAHAGEYGAEALERMFLSFPTTKTYFPHF",
            "program": "blastp",
        })
        assert resp.status_code == 200
        assert "task_id" in resp.json()["data"]

    @pytest.mark.asyncio
    async def test_submit_blast_missing_sequence(self, client: AsyncClient):
        resp = await client.post("/api/v1/blast", json={
            "program": "blastn",
        })
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_submit_blast_custom_params(self, client: AsyncClient):
        resp = await client.post("/api/v1/blast", json={
            "sequence": "ATCGATCGATCGATCGATCG",
            "program": "blastn",
            "evalue": 1e-3,
            "max_target_seqs": 5,
        })
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_submit_blast_empty_sequence(self, client: AsyncClient):
        resp = await client.post("/api/v1/blast", json={
            "sequence": "",
            "program": "blastn",
        })
        # Empty sequence after cleaning should return 400
        assert resp.status_code == 400


class TestBlastStatus:
    @pytest.mark.asyncio
    async def test_status_not_found(self, client: AsyncClient):
        resp = await client.get("/api/v1/blast/nonexistent-task-id")
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_status_after_submit(self, client: AsyncClient):
        submit = await client.post("/api/v1/blast", json={
            "sequence": "ATCGATCGATCGATCGATCG",
            "program": "blastn",
        })
        task_id = submit.json()["data"]["task_id"]
        resp = await client.get(f"/api/v1/blast/{task_id}")
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["task_id"] == task_id
        assert data["status"] in ("pending", "running", "completed", "failed")


class TestBlastResult:
    @pytest.mark.asyncio
    async def test_result_not_found(self, client: AsyncClient):
        resp = await client.get("/api/v1/blast/nonexistent/result")
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_result_not_completed(self, client: AsyncClient):
        submit = await client.post("/api/v1/blast", json={
            "sequence": "ATCGATCGATCGATCGATCG",
            "program": "blastn",
        })
        task_id = submit.json()["data"]["task_id"]
        resp = await client.get(f"/api/v1/blast/{task_id}/result")
        # Task is pending, not completed
        assert resp.status_code == 400


class TestBlastRebuildDb:
    @pytest.mark.asyncio
    async def test_rebuild_db_admin(self, client: AsyncClient, admin_token):
        resp = await client.post("/api/v1/blast/rebuild-db", headers={
            "Authorization": f"Bearer {admin_token}"
        })
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_rebuild_db_unauthorized(self, client: AsyncClient):
        resp = await client.post("/api/v1/blast/rebuild-db")
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_rebuild_db_as_user(self, client: AsyncClient, user_token):
        resp = await client.post("/api/v1/blast/rebuild-db", headers={
            "Authorization": f"Bearer {user_token}"
        })
        assert resp.status_code == 403
