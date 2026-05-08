import io
import pytest
from httpx import AsyncClient


class TestImportTemplate:
    @pytest.mark.asyncio
    async def test_download_template_admin(self, client: AsyncClient, admin_token):
        resp = await client.get("/api/v1/import/template", headers={
            "Authorization": f"Bearer {admin_token}"
        })
        assert resp.status_code == 200
        assert "spreadsheet" in resp.headers.get("content-type", "")

    @pytest.mark.asyncio
    async def test_download_template_unauthorized(self, client: AsyncClient):
        resp = await client.get("/api/v1/import/template")
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_download_template_as_user(self, client: AsyncClient, user_token):
        resp = await client.get("/api/v1/import/template", headers={
            "Authorization": f"Bearer {user_token}"
        })
        assert resp.status_code == 403


class TestImportExcel:
    @pytest.mark.asyncio
    async def test_import_unauthorized(self, client: AsyncClient):
        resp = await client.post("/api/v1/import/excel")
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_import_as_user(self, client: AsyncClient, user_token):
        resp = await client.post("/api/v1/import/excel", headers={
            "Authorization": f"Bearer {user_token}"
        })
        # 422 if no file, 403 if auth check fires first — both are valid
        assert resp.status_code in (403, 422)

    @pytest.mark.asyncio
    async def test_import_no_file_admin(self, client: AsyncClient, admin_token):
        resp = await client.post("/api/v1/import/excel", headers={
            "Authorization": f"Bearer {admin_token}"
        })
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_import_wrong_extension(self, client: AsyncClient, admin_token):
        resp = await client.post(
            "/api/v1/import/excel",
            files={"file": ("test.txt", io.BytesIO(b"not excel"), "text/plain")},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == 400
        assert "xlsx" in resp.json()["detail"].lower() or "xls" in resp.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_import_invalid_excel(self, client: AsyncClient, admin_token):
        resp = await client.post(
            "/api/v1/import/excel",
            files={"file": ("test.xlsx", io.BytesIO(b"not a valid excel file"), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == 400
