"""
End-to-end user flow tests covering complete operation chains.

Each chain is a single test function because the test database is reset
per function (function-scoped engine fixture). The chains exercise the
full lifecycle a real user would follow.
"""

import pytest
from httpx import AsyncClient


# ---------------------------------------------------------------------------
# Chain 1: Browse → Search → Filter → Detail → Export
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_chain_browse_search_export(client: AsyncClient, approved_entry):
    """Anonymous user browses, searches, views detail, and exports approved data."""

    # Step 1: Browse all entries
    resp = await client.get("/api/v1/tn")
    assert resp.status_code == 200
    body = resp.json()
    assert body["data"]["total"] >= 1

    # Step 2: Search by keyword
    resp = await client.get("/api/v1/tn", params={"keyword": "hAT"})
    items = resp.json()["data"]["items"]
    assert any("hAT" in e["family"] for e in items)

    # Step 3: Filter by family
    resp = await client.get("/api/v1/tn", params={"family": "hAT"})
    for item in resp.json()["data"]["items"]:
        assert item["family"] == "hAT"

    # Step 4: View detail
    resp = await client.get(f"/api/v1/tn/{approved_entry.name}")
    assert resp.status_code == 200
    detail = resp.json()["data"]
    assert detail["name"] == "TEST-APPROVED"
    assert detail["dna_sequence"] is not None

    # Step 5: Export FASTA (public, only approved)
    resp = await client.get(f"/api/v1/export/fasta/{approved_entry.name}")
    assert resp.status_code == 200
    assert resp.text.startswith(f">{approved_entry.name}")

    # Step 6: Export EMBL
    resp = await client.get(f"/api/v1/export/embl/{approved_entry.name}")
    assert resp.status_code == 200
    assert "ID" in resp.text and "//" in resp.text

    # Step 7: Pagination
    resp = await client.get("/api/v1/tn", params={"page": 1, "page_size": 2})
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["page"] == 1
    assert len(data["items"]) <= 2


@pytest.mark.asyncio
async def test_chain_pending_not_exportable(client: AsyncClient, tn_entry):
    """A pending (non-approved) entry cannot be publicly exported."""
    resp = await client.get(f"/api/v1/export/fasta/{tn_entry.name}")
    assert resp.status_code == 404

    resp = await client.get(f"/api/v1/export/embl/{tn_entry.name}")
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Chain 2: Submit → Review → Approve → Export
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_chain_submit_review_approve_export(client: AsyncClient, admin_token):
    """Admin submits, then reviews & approves, then the entry is publicly exportable."""

    # Step 1: Admin submits new entry
    resp = await client.post("/api/v1/tn", json={
        "name": "E2E-APPROVE-TEST",
        "family": "Tc1-Mariner",
        "tn_group": "Tc1",
        "origin": "Drosophila melanogaster",
        "mge_type": "TE",
        "length": 1500,
        "dna_sequence": "ATCG" * 375,
    }, headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["name"] == "E2E-APPROVE-TEST"
    assert data["status"] == "pending"

    # Step 2: Admin sees it in pending list
    resp = await client.get("/api/v1/review/pending", headers={
        "Authorization": f"Bearer {admin_token}"
    })
    assert resp.status_code == 200
    names = [e["name"] for e in resp.json()["data"]["items"]]
    assert "E2E-APPROVE-TEST" in names

    # Step 3: Admin approves
    resp = await client.post("/api/v1/review/E2E-APPROVE-TEST", json={
        "action": "approve",
        "comment": "Validated by E2E test."
    }, headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 200

    # Step 4: Entry is now approved
    resp = await client.get("/api/v1/tn/E2E-APPROVE-TEST")
    assert resp.status_code == 200
    assert resp.json()["data"]["status"] == "approved"

    # Step 5: Public can now export
    resp = await client.get("/api/v1/export/fasta/E2E-APPROVE-TEST")
    assert resp.status_code == 200

    # Step 6: Review history shows the action
    resp = await client.get("/api/v1/review/history", headers={
        "Authorization": f"Bearer {admin_token}"
    })
    assert resp.status_code == 200
    history = resp.json()["data"]["items"]
    assert len(history) >= 1
    assert history[0]["action"] == "approve"


# ---------------------------------------------------------------------------
# Chain 3: Submit → Reject
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_chain_submit_reject(client: AsyncClient, admin_token):
    """Admin submits an entry, then rejects it. Entry stays rejected and non-exportable."""

    # Step 1: Submit
    resp = await client.post("/api/v1/tn", json={
        "name": "E2E-REJECT-TEST",
        "family": "hAT",
        "tn_group": "hAT-Group",
        "origin": "Homo sapiens",
        "mge_type": "TE",
        "length": 1000,
        "dna_sequence": "GCTA" * 250,
    }, headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 200

    # Step 2: Admin rejects
    resp = await client.post("/api/v1/review/E2E-REJECT-TEST", json={
        "action": "reject",
        "comment": "Insufficient evidence for classification."
    }, headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 200

    # Step 3: Entry is rejected
    resp = await client.get("/api/v1/tn/E2E-REJECT-TEST")
    assert resp.status_code == 200
    assert resp.json()["data"]["status"] == "rejected"

    # Step 4: Rejected entries are not exportable
    resp = await client.get("/api/v1/export/fasta/E2E-REJECT-TEST")
    assert resp.status_code == 404

    # Step 5: Cannot re-review an already-reviewed entry
    resp = await client.post("/api/v1/review/E2E-REJECT-TEST", json={
        "action": "approve",
    }, headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 400

    # Step 6: Unauthorized users cannot review (clear cookies from admin_token fixture first)
    client.cookies.clear()
    resp = await client.post("/api/v1/review/E2E-REJECT-TEST", json={
        "action": "approve",
    })
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# Chain 4: Download Request Flow
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_chain_download_request(client: AsyncClient, approved_entry, admin_token, user_token):
    """Public submits download request → admin reviews & approves → data sent."""

    # Step 1: Public submits a download request
    resp = await client.post("/api/v1/download-request", json={
        "requester_email": "researcher@example.com",
        "requester_name": "Dr. Smith",
        "requester_institution": "MIT",
        "requested_data": approved_entry.name,
        "data_format": "fasta",
        "purpose": "Comparative genomics study.",
    })
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["status"] == "pending"
    assert data["entry_count"] >= 1

    # Step 2: Anyone can see admin list
    resp = await client.get("/api/v1/download-request/admins")
    assert resp.status_code == 200
    admins = resp.json()["data"]
    assert isinstance(admins, list)
    assert len(admins) >= 1

    # Step 3: Admin lists pending requests
    resp = await client.get("/api/v1/download-request/pending", headers={
        "Authorization": f"Bearer {admin_token}"
    })
    assert resp.status_code == 200
    items = resp.json()["data"]["items"]
    assert len(items) >= 1
    assert any(r["requester_email"] == "researcher@example.com" for r in items)

    # Step 4: Admin approves the request
    req_id = next(r["id"] for r in items if r["requester_email"] == "researcher@example.com")
    resp = await client.post(f"/api/v1/download-request/{req_id}/review", json={
        "action": "approve",
    }, headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 200
    assert resp.json()["data"]["status"] == "approved"

    # Step 5: History shows approved request
    resp = await client.get("/api/v1/download-request/history", headers={
        "Authorization": f"Bearer {admin_token}"
    })
    assert resp.status_code == 200
    history = resp.json()["data"]["items"]
    assert len(history) >= 1

    # Step 6: Non-admin cannot access pending list
    resp = await client.get("/api/v1/download-request/pending", headers={
        "Authorization": f"Bearer {user_token}"
    })
    assert resp.status_code == 403

    # Step 7: Too many entries rejected
    names = ",".join(f"TE-{i}" for i in range(100))
    resp = await client.post("/api/v1/download-request", json={
        "requester_email": "greedy@example.com",
        "requested_data": names,
        "data_format": "fasta",
    })
    assert resp.status_code == 400

    # Step 8: Rejection without a reason fails
    resp2 = await client.post("/api/v1/download-request", json={
        "requester_email": "someone@example.com",
        "requested_data": approved_entry.name,
        "data_format": "fasta",
    })
    assert resp2.status_code == 200
    req2_id = resp2.json()["data"]["id"]

    resp = await client.post(f"/api/v1/download-request/{req2_id}/review", json={
        "action": "reject",
    }, headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 400  # reason required for rejection


# ---------------------------------------------------------------------------
# Chain 5: Analysis → Submit
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_chain_analyze_then_submit(client: AsyncClient, admin_token):
    """User analyzes a sequence, then uses analysis results to submit an entry."""

    seq = "ATCG" * 500  # 2000 bp

    # Step 1: Analyze sequence
    resp = await client.post("/api/v1/analyze/sequence", json={
        "dna_sequence": seq,
        "family": "Tc1-Mariner",
    })
    assert resp.status_code == 200
    result = resp.json()["data"]
    assert result["length"] == 2000
    assert result["gc_content"] == 50.0
    assert result["orf1_function"] == "Transposase"
    assert result["orf1_chemistry"] == "DDE"
    assert result["transposition"] == "Cut-and-paste"
    assert result["mge_type"] == "TE"

    # Step 2: Submit based on analysis
    resp = await client.post("/api/v1/tn", json={
        "name": "E2E-ANALYZE-TE",
        "family": "Tc1-Mariner",
        "tn_group": "Tc1",
        "origin": "Unknown",
        "mge_type": result["mge_type"],
        "length": result["length"],
        "dna_sequence": seq,
        "orf1_function": result["orf1_function"],
        "orf1_chemistry": result["orf1_chemistry"],
        "transposition": result["transposition"],
    }, headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 200
    entry = resp.json()["data"]
    assert entry["name"] == "E2E-ANALYZE-TE"
    assert entry["orf1_function"] == "Transposase"

    # Step 3: Empty sequence analysis
    resp = await client.post("/api/v1/analyze/sequence", json={
        "dna_sequence": "",
    })
    assert resp.status_code == 200
    empty = resp.json()["data"]
    assert empty["length"] == 0


# ---------------------------------------------------------------------------
# Chain 6: Full Auth Lifecycle
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_chain_auth_lifecycle(client: AsyncClient, normal_user):
    """Login → access protected → change password → re-login → logout."""

    # Step 1: Login
    resp = await client.post("/api/v1/auth/login", json={
        "username": "user1",
        "password": "user123",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["data"]["user"]["username"] == "user1"
    token = data["data"]["token"]
    assert token is not None
    assert "tndb_token" in resp.cookies

    # Step 2: Access protected endpoint with token
    resp = await client.get("/api/v1/auth/me", headers={
        "Authorization": f"Bearer {token}"
    })
    assert resp.status_code == 200
    assert resp.json()["data"]["username"] == "user1"

    # Step 3: Access without token/cookie fails
    client.cookies.clear()
    resp = await client.get("/api/v1/auth/me")
    assert resp.status_code == 401

    # Step 4: Change password (re-authenticate via header since cookie was cleared)
    resp = await client.post("/api/v1/auth/change-password", json={
        "oldPassword": "user123",
        "newPassword": "newpass789",
    }, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200

    # Step 5: New password works
    client.cookies.clear()
    resp = await client.post("/api/v1/auth/login", json={
        "username": "user1",
        "password": "newpass789",
    })
    assert resp.status_code == 200

    # Step 6: Logout
    resp = await client.post("/api/v1/auth/logout")
    assert resp.status_code == 200


# ---------------------------------------------------------------------------
# Chain 7: Admin User Management
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_chain_admin_user_management(client: AsyncClient, admin_token, admin_user):
    """Admin creates user, user logs in and submits, admin manages user list."""

    # Step 1: Admin creates a new user
    resp = await client.post("/api/v1/admin/users", json={
        "username": "e2eresearcher",
        "email": "e2eresearcher@tndb.org",
        "password": "research123",
        "institution": "Harvard",
        "role": "user",
    }, headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 200
    user_data = resp.json()["data"]
    assert user_data["username"] == "e2eresearcher"
    assert user_data["role"] == "user"

    # Step 2: New user logs in
    login_resp = await client.post("/api/v1/auth/login", json={
        "username": "e2eresearcher",
        "password": "research123",
    })
    assert login_resp.status_code == 200
    user_token = login_resp.json()["data"]["token"]

    # Step 3: New user submits an entry
    submit_resp = await client.post("/api/v1/tn", json={
        "name": "E2E-RESEARCHER-TE",
        "family": "PiggyBac",
        "tn_group": "PiggyBac",
        "origin": "Mus musculus",
        "mge_type": "TE",
        "length": 2500,
        "dna_sequence": "TTTA" * 625,
    }, headers={"Authorization": f"Bearer {user_token}"})
    assert submit_resp.status_code == 200
    assert submit_resp.json()["data"]["name"] == "E2E-RESEARCHER-TE"

    # Step 4: Admin lists users
    resp = await client.get("/api/v1/admin/users", headers={
        "Authorization": f"Bearer {admin_token}"
    })
    assert resp.status_code == 200
    usernames = [u["username"] for u in resp.json()["data"]["items"]]
    assert "e2eresearcher" in usernames

    # Step 5: Admin filters users by role
    resp = await client.get("/api/v1/admin/users", params={"role": "user"}, headers={
        "Authorization": f"Bearer {admin_token}"
    })
    assert resp.status_code == 200
    for u in resp.json()["data"]["items"]:
        assert u["role"] == "user"

    # Step 6: Admin searches users
    resp = await client.get("/api/v1/admin/users", params={"search": "e2eresearcher"}, headers={
        "Authorization": f"Bearer {admin_token}"
    })
    assert resp.status_code == 200
    users = resp.json()["data"]["items"]
    matched = [u for u in users if u["username"] == "e2eresearcher"]
    assert len(matched) == 1
    user_id = matched[0]["id"]

    # Step 7: Admin updates user
    resp = await client.put(f"/api/v1/admin/users/{user_id}", json={
        "institution": "Stanford",
    }, headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 200

    # Step 8: Admin cannot delete self
    resp = await client.delete(f"/api/v1/admin/users/{admin_user.id}", headers={
        "Authorization": f"Bearer {admin_token}"
    })
    assert resp.status_code == 400

    # Step 9: Admin deletes user
    resp = await client.delete(f"/api/v1/admin/users/{user_id}", headers={
        "Authorization": f"Bearer {admin_token}"
    })
    assert resp.status_code == 200

    # Step 10: Deleted user cannot log in
    resp = await client.post("/api/v1/auth/login", json={
        "username": "e2eresearcher",
        "password": "research123",
    })
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# Chain 8: Stats & Health
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_chain_stats_health(client: AsyncClient, approved_entry):
    """Verify health check and statistics endpoints."""

    # Health
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"

    # Status stats - should include "approved" from approved_entry
    resp = await client.get("/api/v1/stats/status")
    assert resp.status_code == 200
    statuses = [s["status"] for s in resp.json()["data"]]
    assert "approved" in statuses

    # Family stats
    resp = await client.get("/api/v1/stats/family")
    assert resp.status_code == 200
    assert isinstance(resp.json()["data"], list)


# ---------------------------------------------------------------------------
# Chain 9: Batch Export (admin-only)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_chain_batch_export(client: AsyncClient, admin_token, user_token, approved_entry):
    """Admin performs batch export; regular users cannot."""

    # Admin: batch by IDs
    resp = await client.post("/api/v1/export/batch", json={
        "format": "fasta",
        "ids": [approved_entry.name],
    }, headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 200
    assert resp.text.startswith(f">{approved_entry.name}")

    # Admin: batch by family
    resp = await client.post("/api/v1/export/batch", json={
        "format": "fasta",
        "family": "hAT",
    }, headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 200

    # Admin: EMBL format
    resp = await client.post("/api/v1/export/batch", json={
        "format": "embl",
        "ids": [approved_entry.name],
    }, headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 200
    assert "ID" in resp.text

    # Unauthorized (no token — clear cookie first)
    client.cookies.clear()
    resp = await client.post("/api/v1/export/batch", json={
        "format": "fasta",
        "ids": ["TEST-APPROVED"],
    })
    assert resp.status_code == 401

    # Regular user (forbidden)
    resp = await client.post("/api/v1/export/batch", json={
        "format": "fasta",
        "ids": ["TEST-APPROVED"],
    }, headers={"Authorization": f"Bearer {user_token}"})
    assert resp.status_code == 403


# ---------------------------------------------------------------------------
# Chain 10: Error handling and edge cases
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_chain_error_handling(client: AsyncClient, admin_token, tn_entry):
    """Verify proper error handling across endpoints."""

    # 404 for non-existent entry
    resp = await client.get("/api/v1/tn/NONEXISTENT")
    assert resp.status_code == 404

    # Duplicate name
    resp = await client.post("/api/v1/tn", json={
        "name": tn_entry.name,
        "family": "Test",
        "tn_group": "Test",
    }, headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 400

    # Missing required fields
    resp = await client.post("/api/v1/tn", json={
        "name": "INCOMPLETE",
    })
    assert resp.status_code == 422

    # Unauthorized delete (clear cookie first)
    client.cookies.clear()
    resp = await client.delete(f"/api/v1/tn/{tn_entry.name}")
    assert resp.status_code == 401

    # Invalid review action
    resp = await client.post("/api/v1/review/{tn_entry.name}", json={
        "action": "invalid_action",
    }, headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 400

    # Review without auth (clear cookie first)
    client.cookies.clear()
    resp = await client.post(f"/api/v1/review/{tn_entry.name}", json={
        "action": "approve",
    })
    assert resp.status_code == 401
