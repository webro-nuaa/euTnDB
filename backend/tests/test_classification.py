import pytest
from httpx import AsyncClient


class TestClassificationTree:
    @pytest.mark.asyncio
    async def test_get_tree(self, client: AsyncClient):
        resp = await client.get("/api/v1/classification/tree")
        assert resp.status_code == 200
        data = resp.json()
        assert data["code"] == 200
        tree = data["data"]
        assert "name" in tree
        assert tree["name"] == "Transposable Element"
        assert "children" in tree
        # Should have Class I and Class II
        class_names = [c["name"] for c in tree["children"]]
        assert "Class I: Retrotransposon" in class_names
        assert "Class II: DNA Transposon" in class_names


class TestSuperfamilies:
    @pytest.mark.asyncio
    async def test_get_superfamilies_empty(self, client: AsyncClient):
        resp = await client.get("/api/v1/classification/superfamilies")
        assert resp.status_code == 200
        data = resp.json()
        assert data["code"] == 200
        assert isinstance(data["data"], list)

    @pytest.mark.asyncio
    async def test_get_superfamilies_with_data(self, client: AsyncClient, tn_entry):
        resp = await client.get("/api/v1/classification/superfamilies")
        assert resp.status_code == 200
        data = resp.json()
        items = data["data"]
        assert len(items) > 0
        families = [i["name"] for i in items]
        assert "Tc1-Mariner" in families
        tc1 = next(i for i in items if i["name"] == "Tc1-Mariner")
        assert tc1["count"] >= 1
        assert "code" in tc1
