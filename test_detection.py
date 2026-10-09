"""Unit tests for the detection rules and scoring (no database needed)."""
import pytest

from app import detection, scoring, url_checker
from app.analysis import Finding, redact
from app.document_parser import DocumentError, extract_text


def rule_ids(outcome):
    return {f.rule_id for f in outcome.findings}


def test_phishing_message_is_high_risk():
    outcome = detection.analyze_message(
        "URGENT: your account will be suspended. Share your OTP now to keep it active.",
        "Bank Support <alerts.bank@gmail.com>", None)
    ids = rule_ids(outcome)
    assert {"credential_request", "threat_pressure", "urgency", "free_email_official"} <= ids
    status, score, label = scoring.assess(outcome)
    assert status == "completed" and score >= 60 and label in ("High Risk", "Very High Risk")


def test_ordinary_message_has_low_risk():
    outcome = detection.analyze_message(
        "Hi Priya, the project review meeting has moved to Thursday at 3pm in room 4. Thanks!", None, None)
    status, score, label = scoring.assess(outcome)
    assert outcome.findings == []
    assert status == "completed" and score == 0 and label == "Lower Observed Risk"


def test_very_short_input_is_insufficient_evidence():
    outcome = detection.analyze_message("ok", None, None)
    status, score, label = scoring.assess(outcome)
    assert (status, score, label) == ("insufficient_evidence", None, "Insufficient Evidence")


def test_repeated_warning_sign_counts_once():
    once = detection.scan_text("Act now, this is urgent.")
    many = detection.scan_text("Urgent! urgent! URGENT! act now, immediately, urgent!!!")
    assert [f.rule_id for f in once].count("urgency") == 1
    assert [f.rule_id for f in many].count("urgency") == 1
    assert scoring.compute_score(once) == scoring.compute_score(many)


def test_same_words_do_not_trigger_two_rules():
    # "registration fee" belongs to the upfront-fee rule; UPI is a separate sign.
    ids = [f.rule_id for f in detection.scan_text("Please pay the registration fee via UPI today only")]
    assert ids.count("advance_fee") == 1
    assert "untraceable_payment" in ids


def test_score_formula_and_bounds():
    def f(w):
        return Finding("r", "x", "high", "strong", w, "", "")
    assert scoring.compute_score([]) == 0
    assert scoring.compute_score([f(45)]) == 45
    assert scoring.compute_score([f(50), f(50)]) == 75
    assert scoring.compute_score([f(95)] * 20) <= 100


@pytest.mark.parametrize("score,label", [(0, "Lower Observed Risk"), (19, "Lower Observed Risk"),
                                         (20, "Caution"), (40, "Suspicious"), (59, "Suspicious"),
                                         (60, "High Risk"), (80, "Very High Risk"), (100, "Very High Risk")])
def test_risk_bands(score, label):
    assert scoring.label_for(score) == label


def test_url_lookalike_and_typosquat():
    assert "url_brand_lookalike" in {f.rule_id for f in url_checker.check_url("http://paypal-account-verify.com/login").findings}
    assert "url_typosquat" in {f.rule_id for f in url_checker.check_url("https://paypa1.com").findings}


def test_official_domain_is_not_flagged():
    report = url_checker.check_url("https://www.amazon.in/gp/your-account")
    assert report.official_brand == "amazon"
    assert report.findings == []


def test_ip_punycode_and_at_sign():
    assert "url_ip_host" in {f.rule_id for f in url_checker.check_url("http://192.168.10.5/pay").findings}
    assert "url_punycode" in {f.rule_id for f in url_checker.check_url("https://xn--pypal-4ve.com").findings}
    assert "url_at_symbol" in {f.rule_id for f in url_checker.check_url("https://google.com@evil.example/x").findings}


@pytest.mark.parametrize("bad", ["", "javascript:alert(1)", "file:///etc/passwd", "not a url", "http://"])
def test_invalid_urls_are_rejected(bad):
    with pytest.raises(ValueError):
        url_checker.check_url(bad)


def test_recruiter_fee_is_critical_and_not_double_counted():
    outcome = detection.analyze_recruiter({
        "recruiter_email": "careers.team@gmail.com", "company_name": "Example Corp",
        "requested_fees": "INR 1500 registration fee",
        "recruitment_message": "You are selected without interview. Pay the registration fee to confirm.",
    })
    ids = [f.rule_id for f in outcome.findings]
    assert "requested_fee" in ids and "advance_fee" not in ids
    assert {"recruiter_free_email", "no_interview_offer"} <= set(ids)


def test_recruiter_without_fee_value_is_not_flagged():
    outcome = detection.analyze_recruiter({"requested_fees": "None", "job_description": "x" * 80})
    assert "requested_fee" not in rule_ids(outcome)


def test_company_checks_and_unverified_items():
    outcome = detection.analyze_company("Bright Futures Ltd", "https://brightfutures.example.com",
                                        "hr@gmail.com", None, None)
    assert "company_free_email" in rule_ids(outcome)
    assert any("registration" in u.lower() for u in outcome.unavailable_checks)


def test_profile_limitation_is_always_reported():
    outcome = detection.analyze_profile(None, "Recruiter at Google, Amazon and Microsoft. Hiring now! 12 connections",
                                        None, None, None)
    assert any("not accessed" in l for l in outcome.limitations)
    assert {"profile_many_brands", "profile_few_connections"} <= rule_ids(outcome)


def test_redaction_hides_emails_and_long_numbers():
    text = redact("Mail john.doe@example.com or call +91 98765 43210, account 123456789012")
    assert "john.doe" not in text and "98765" not in text and "123456789012" not in text
    assert "@example.com" in text and "10" in text


def test_document_parser_txt_and_validation():
    doc = extract_text("letter.txt", b"Pay a processing fee to receive your offer letter.")
    assert doc.kind == "TXT" and "processing fee" in doc.text
    with pytest.raises(DocumentError):
        extract_text("evil.exe", b"MZ...")
    with pytest.raises(DocumentError):
        extract_text("fake.pdf", b"not really a pdf")
    with pytest.raises(DocumentError):
        extract_text("empty.txt", b"")
