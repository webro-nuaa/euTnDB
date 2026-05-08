import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


class TestExportFasta:
    @pytest.mark.asyncio
    async def test_export_fasta_found(self, client: AsyncClient, tn_entry):
        resp = await client.get(f"/api/v1/export/fasta/{tn_entry.name}")
        assert resp.status_code == 200
        content = resp.text
        assert content.startswith(">")
        assert "TEST-TE-1" in content

    @pytest.mark.asyncio
    async def test_export_fasta_not_found(self, client: AsyncClient):
        resp = await client.get("/api/v1/export/fasta/NONEXISTENT")
        assert resp.status_code == 404


class TestExportEmbl:
    @pytest.mark.asyncio
    async def test_export_embl_found(self, client: AsyncClient, tn_entry):
        resp = await client.get(f"/api/v1/export/embl/{tn_entry.name}")
        assert resp.status_code == 200
        content = resp.text
        assert "ID   TEST-TE-1" in content
        assert "//" in content

    @pytest.mark.asyncio
    async def test_export_embl_not_found(self, client: AsyncClient):
        resp = await client.get("/api/v1/export/embl/NONEXISTENT")
        assert resp.status_code == 404


class TestBatchExport:
    @pytest.mark.asyncio
    async def test_batch_export_by_ids_admin(self, client: AsyncClient, admin_token, tn_entry):
        resp = await client.post("/api/v1/export/batch", json={
            "format": "fasta",
            "ids": [tn_entry.name],
        }, headers={"Authorization": f"Bearer {admin_token}"})
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_batch_export_by_family_admin(self, client: AsyncClient, admin_token, tn_entry):
        resp = await client.post("/api/v1/export/batch", json={
            "format": "fasta",
            "family": "Tc1-Mariner",
        }, headers={"Authorization": f"Bearer {admin_token}"})
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_batch_export_embl_format(self, client: AsyncClient, admin_token, tn_entry):
        resp = await client.post("/api/v1/export/batch", json={
            "format": "embl",
            "ids": [tn_entry.name],
        }, headers={"Authorization": f"Bearer {admin_token}"})
        assert resp.status_code == 200
        assert "ID   " in resp.text

    @pytest.mark.asyncio
    async def test_batch_export_unauthorized(self, client: AsyncClient, tn_entry):
        resp = await client.post("/api/v1/export/batch", json={
            "format": "fasta",
            "ids": [tn_entry.name],
        })
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_batch_export_as_user(self, client: AsyncClient, user_token, tn_entry):
        resp = await client.post("/api/v1/export/batch", json={
            "format": "fasta",
            "ids": [tn_entry.name],
        }, headers={"Authorization": f"Bearer {user_token}"})
        assert resp.status_code == 403

    @pytest.mark.asyncio
    async def test_batch_export_empty_ids(self, client: AsyncClient, admin_token):
        resp = await client.post("/api/v1/export/batch", json={
            "format": "fasta",
            "ids": [],
        }, headers={"Authorization": f"Bearer {admin_token}"})
        assert resp.status_code == 404
