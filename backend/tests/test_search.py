import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


class TestSearch:
    @pytest.mark.asyncio
    async def test_search_empty(self, client: AsyncClient):
        resp = await client.get("/api/v1/search")
        assert resp.status_code == 200
        data = resp.json()
        assert data["code"] == 200
        assert data["data"]["total"] == 0

    @pytest.mark.asyncio
    async def test_search_with_keyword(self, client: AsyncClient, tn_entry):
        resp = await client.get("/api/v1/search?keyword=TEST")
        assert resp.status_code == 200
        data = resp.json()
        assert data["data"]["total"] >= 1

    @pytest.mark.asyncio
    async def test_search_with_family_filter(self, client: AsyncClient, tn_entry):
        resp = await client.get("/api/v1/search?family=Tc1-Mariner")
        assert resp.status_code == 200
        data = resp.json()
        for item in data["data"]["items"]:
            assert item["family"] == "Tc1-Mariner"

    @pytest.mark.asyncio
    async def test_search_pagination(self, client: AsyncClient):
        resp = await client.get("/api/v1/search?page=1&page_size=10")
        assert resp.status_code == 200
        data = resp.json()
        assert data["data"]["page"] == 1

    @pytest.mark.asyncio
    async def test_search_origin_filter(self, client: AsyncClient, tn_entry):
        resp = await client.get("/api/v1/search?origin=Drosophila melanogaster")
        assert resp.status_code == 200
        data = resp.json()
        for item in data["data"]["items"]:
            assert "Drosophila" in item.get("origin", "")


class TestSearchSuggestions:
    @pytest.mark.asyncio
    async def test_suggestions_empty_keyword(self, client: AsyncClient):
        resp = await client.get("/api/v1/search/suggestions?keyword=test")
        assert resp.status_code == 200
        data = resp.json()
        assert data["code"] == 200
        assert isinstance(data["data"], list)

    @pytest.mark.asyncio
    async def test_suggestions_with_data(self, client: AsyncClient, tn_entry):
        resp = await client.get("/api/v1/search/suggestions?keyword=TEST")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data["data"], list)
