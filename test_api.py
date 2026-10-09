"""End-to-end API tests against MySQL (skipped unless TEST_DATABASE_URL is set)."""

PHISH = ("URGENT: Dear customer, your account will be suspended within 24 hours. "
         "Share your OTP at http://secure-login-verify.xyz/login")


def test_health(client):
    body = client.get("/health").json()
    assert "database" in body and "features" in body


def test_message_scan_is_saved_and_listed(client):
    res = client.post("/api/v1/analyze/message", json={"message": PHISH})
    assert res.status_code == 200
    scan = res.json()
    assert scan["risk_score"] >= 60 and scan["findings"]
    assert scan["sources_checked"] and scan["limitations"] and scan["recommendations"]
    assert "OTP" not in scan["input_summary"]       # raw message text is not stored

    listed = client.get("/api/v1/scans").json()
    assert listed["total"] == 1 and listed["items"][0]["id"] == scan["id"]
    detail = client.get(f"/api/v1/scans/{scan['id']}").json()
    assert len(detail["findings"]) == len(scan["findings"])


def test_all_scan_types(client):
    calls = [
        ("url", {"url": "https://paypa1.com/verify"}),
        ("profile", {"profile_text": "Hiring for Google, Amazon, Microsoft. Pay certification fee first. " * 2}),
        ("recruiter", {"requested_fees": "Rs 999 training fee", "recruiter_email": "jobs@gmail.com"}),
        ("company", {"company_name": "Acme", "website": "https://acme.example.com", "email_domain": "gmail.com"}),
    ]
    for kind, body in calls:
        res = client.post(f"/api/v1/analyze/{kind}", json=body)
        assert res.status_code == 200, (kind, res.text)
        assert res.json()["scan_type"] == kind
    doc = client.post("/api/v1/analyze/document",
                      files={"file": ("offer.txt", b"Pay a refundable deposit and send your Aadhaar card", "text/plain")})
    assert doc.status_code == 200 and doc.json()["scan_type"] == "document"
    stats = client.get("/api/v1/dashboard/stats").json()
    assert stats["total_scans"] == 5
    assert sum(c["count"] for c in stats["scan_categories"]) == 5


def test_validation_errors(client):
    assert client.post("/api/v1/analyze/message", json={"message": "   "}).status_code == 422
    assert client.post("/api/v1/analyze/url", json={"url": "javascript:alert(1)"}).status_code == 422
    assert client.post("/api/v1/analyze/profile", json={}).status_code == 422
    bad_file = client.post("/api/v1/analyze/document", files={"file": ("x.exe", b"MZ", "application/octet-stream")})
    assert bad_file.status_code == 400


def test_upload_size_limit(client):
    big = b"a" * (6 * 1024 * 1024)
    assert client.post("/api/v1/analyze/document", files={"file": ("big.txt", big, "text/plain")}).status_code == 413


def test_reports_and_delete(client):
    scan_id = client.post("/api/v1/analyze/message", json={"message": PHISH}).json()["id"]
    report = client.post("/api/v1/reports", json={"scan_id": scan_id, "report_type": "detailed"})
    assert report.status_code == 201
    report_id = report.json()["id"]
    assert report.json()["report_data"]["scan"]["id"] == scan_id
    assert client.get("/api/v1/reports").json()[0]["id"] == report_id
    assert client.get(f"/api/v1/reports/{report_id}").status_code == 200

    assert client.delete(f"/api/v1/scans/{scan_id}").status_code == 200
    assert client.get(f"/api/v1/scans/{scan_id}").status_code == 404
    assert client.get(f"/api/v1/reports/{report_id}").status_code == 404   # cascades
    assert client.post("/api/v1/reports", json={"scan_id": 99999}).status_code == 404


def test_history_filters(client):
    client.post("/api/v1/analyze/message", json={"message": PHISH})
    client.post("/api/v1/analyze/url", json={"url": "https://www.amazon.in"})
    assert client.get("/api/v1/scans", params={"scan_type": "url"}).json()["total"] == 1
    assert client.get("/api/v1/scans", params={"search": "amazon"}).json()["total"] == 1
    items = client.get("/api/v1/scans", params={"sort": "score_high"}).json()["items"]
    assert items[0]["scan_type"] == "message"
