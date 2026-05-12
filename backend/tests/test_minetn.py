import io
import pytest
from httpx import AsyncClient


class TestMineTnUpload:
    @pytest.mark.asyncio
    async def test_upload_fasta_admin(self, client: AsyncClient, admin_token):
        resp = await client.post(
            "/api/v1/minetn/upload",
            files={"file": ("genome.fa", io.BytesIO(b">chr1\nATCGATCGATCG"), "text/plain")},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "filepath" in data["data"]
        assert "filename" in data["data"]

    @pytest.mark.asyncio
    async def test_upload_wrong_extension(self, client: AsyncClient, admin_token):
        resp = await client.post(
            "/api/v1/minetn/upload",
            files={"file": ("genome.txt", io.BytesIO(b"not fasta"), "text/plain")},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == 400

    @pytest.mark.asyncio
    async def test_upload_unauthorized(self, client: AsyncClient):
        resp = await client.post("/api/v1/minetn/upload")
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_upload_as_user(self, client: AsyncClient, user_token):
        resp = await client.post(
            "/api/v1/minetn/upload",
            files={"file": ("genome.fa", io.BytesIO(b">chr1\nATCG"), "text/plain")},
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert resp.status_code == 403


class TestMineTnCreate:
    @pytest.mark.asyncio
    async def test_create_task(self, client: AsyncClient, admin_token):
        resp = await client.post("/api/v1/minetn", json={
            "genome_file": "/tmp/test_genome.fa",
            "min_tir_length": 10,
            "max_tir_length": 50,
            "min_tir_similarity": 0.8,
        }, headers={"Authorization": f"Bearer {admin_token}"})
        assert resp.status_code == 200
        data = resp.json()
        assert "task_id" in data["data"]

    @pytest.mark.asyncio
    async def test_create_task_unauthorized(self, client: AsyncClient):
        resp = await client.post("/api/v1/minetn", json={
            "genome_file": "/tmp/test.fa",
        })
        assert resp.status_code == 401


class TestMineTnTaskList:
    @pytest.mark.asyncio
    async def test_list_tasks(self, client: AsyncClient, admin_token):
        # Create a task first
        await client.post("/api/v1/minetn", json={
            "genome_file": "/tmp/test.fa",
        }, headers={"Authorization": f"Bearer {admin_token}"})

        resp = await client.get("/api/v1/minetn", headers={
            "Authorization": f"Bearer {admin_token}"
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "items" in data["data"]
        assert isinstance(data["data"]["items"], list)

    @pytest.mark.asyncio
    async def test_list_tasks_unauthorized(self, client: AsyncClient):
        resp = await client.get("/api/v1/minetn")
        assert resp.status_code == 401


class TestMineTnTaskDetail:
    @pytest.mark.asyncio
    async def test_task_detail(self, client: AsyncClient, admin_token):
        create = await client.post("/api/v1/minetn", json={
            "genome_file": "/tmp/test_genome.fa",
        }, headers={"Authorization": f"Bearer {admin_token}"})
        task_id = create.json()["data"]["task_id"]

        resp = await client.get(f"/api/v1/minetn/{task_id}", headers={
            "Authorization": f"Bearer {admin_token}"
        })
        assert resp.status_code == 200
        assert resp.json()["data"]["task_id"] == task_id

    @pytest.mark.asyncio
    async def test_task_detail_not_found(self, client: AsyncClient, admin_token):
        resp = await client.get("/api/v1/minetn/nonexistent", headers={
            "Authorization": f"Bearer {admin_token}"
        })
        assert resp.status_code == 404


class TestMineTnResults:
    @pytest.mark.asyncio
    async def test_results_not_completed(self, client: AsyncClient, admin_token):
        create = await client.post("/api/v1/minetn", json={
            "genome_file": "/tmp/test.fa",
        }, headers={"Authorization": f"Bearer {admin_token}"})
        task_id = create.json()["data"]["task_id"]

        resp = await client.get(f"/api/v1/minetn/{task_id}/results", headers={
            "Authorization": f"Bearer {admin_token}"
        })
        assert resp.status_code == 400  # not completed


class TestMineTnImport:
    @pytest.mark.asyncio
    async def test_import_not_completed(self, client: AsyncClient, admin_token):
        create = await client.post("/api/v1/minetn", json={
            "genome_file": "/tmp/test.fa",
        }, headers={"Authorization": f"Bearer {admin_token}"})
        task_id = create.json()["data"]["task_id"]

        resp = await client.post(f"/api/v1/minetn/{task_id}/import", json={
            "element_ids": ["Tn_001"],
        }, headers={"Authorization": f"Bearer {admin_token}"})
        assert resp.status_code == 400
