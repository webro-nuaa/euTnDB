import pytest
from httpx import AsyncClient


class TestAnalyzeSequence:
    @pytest.mark.asyncio
    async def test_analyze_basic(self, client: AsyncClient):
        seq = "ATCG" * 100  # 400 bp
        resp = await client.post("/api/v1/analyze/sequence", json={
            "dna_sequence": seq,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["code"] == 200
        result = data["data"]
        assert result["length"] == 400
        assert 0 <= result["gc_content"] <= 100

    @pytest.mark.asyncio
    async def test_analyze_with_family(self, client: AsyncClient):
        seq = "ATCG" * 300
        resp = await client.post("/api/v1/analyze/sequence", json={
            "dna_sequence": seq,
            "family": "Tc1-Mariner",
        })
        assert resp.status_code == 200
        data = resp.json()
        result = data["data"]
        assert result["orf1_function"] == "Transposase"
        assert result["transposition"] == "Cut-and-paste"
        assert result["mge_type"] is not None

    @pytest.mark.asyncio
    async def test_analyze_empty_sequence(self, client: AsyncClient):
        resp = await client.post("/api/v1/analyze/sequence", json={
            "dna_sequence": "",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["data"]["length"] == 0

    @pytest.mark.asyncio
    async def test_analyze_piggybac_family(self, client: AsyncClient):
        seq = "ATCG" * 500
        resp = await client.post("/api/v1/analyze/sequence", json={
            "dna_sequence": seq,
            "family": "PiggyBac",
        })
        assert resp.status_code == 200
        result = resp.json()["data"]
        assert result["orf1_chemistry"] == "DDD"

    @pytest.mark.asyncio
    async def test_analyze_helitron_family(self, client: AsyncClient):
        seq = "ATCG" * 500
        resp = await client.post("/api/v1/analyze/sequence", json={
            "dna_sequence": seq,
            "family": "Helitron",
        })
        assert resp.status_code == 200
        result = resp.json()["data"]
        assert result["orf1_function"] == "RepHel"
        assert result["transposition"] == "Rolling-circle"
