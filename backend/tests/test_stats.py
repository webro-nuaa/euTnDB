import pytest
from httpx import AsyncClient


class TestStatsOverview:
    @pytest.mark.asyncio
    async def test_overview_empty(self, client: AsyncClient):
        resp = await client.get("/api/v1/stats/overview")
        assert resp.status_code == 200
        data = resp.json()
        assert data["code"] == 200
        assert data["data"]["tn_count"] == 0
        assert "species_count" in data["data"]
        assert "family_count" in data["data"]

    @pytest.mark.asyncio
    async def test_overview_with_data(self, client: AsyncClient, tn_entry):
        resp = await client.get("/api/v1/stats/overview")
        assert resp.status_code == 200
        data = resp.json()
        assert data["data"]["tn_count"] >= 1
        assert data["data"]["family_count"] >= 1
        assert data["data"]["species_count"] >= 1


class TestFamilyStats:
    @pytest.mark.asyncio
    async def test_family_stats_empty(self, client: AsyncClient):
        resp = await client.get("/api/v1/stats/family")
        assert resp.status_code == 200
        assert resp.json()["code"] == 200

    @pytest.mark.asyncio
    async def test_family_stats_with_data(self, client: AsyncClient, tn_entry):
        resp = await client.get("/api/v1/stats/family")
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert len(data) >= 1
        assert any(f["family"] == "Tc1-Mariner" for f in data)


class TestSpeciesStats:
    @pytest.mark.asyncio
    async def test_species_stats(self, client: AsyncClient, tn_entry):
        resp = await client.get("/api/v1/stats/species")
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert len(data) >= 1
        assert any(s["species"] == "Drosophila melanogaster" for s in data)


class TestStatusStats:
    @pytest.mark.asyncio
    async def test_status_stats(self, client: AsyncClient, tn_entry):
        resp = await client.get("/api/v1/stats/status")
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert len(data) >= 1
        statuses = [s["status"] for s in data]
        assert "pending" in statuses
