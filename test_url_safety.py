"""The optional live link check must never connect to internal addresses (SSRF protection)."""
import pytest

from app.threat_intel import UnsafeTarget, follow_redirects, is_public_ip, validate_target


@pytest.mark.parametrize("url", [
    "http://127.0.0.1/admin",
    "http://localhost:80/",
    "http://10.0.0.5/",
    "http://192.168.1.1/",
    "http://169.254.169.254/latest/meta-data/",   # cloud metadata service
    "http://[::1]/",
    "http://[::ffff:127.0.0.1]/",
    "http://0.0.0.0/",
    "ftp://example.com/file",
    "http://example.com:8080/",
    "http://user:pass@example.com/",
    "http://printer.local/",
])
def test_unsafe_targets_are_blocked(url):
    with pytest.raises(UnsafeTarget):
        validate_target(url)


def test_follow_redirects_reports_block_without_connecting():
    result = follow_redirects("http://127.0.0.1:80/")
    assert result.blocked and result.hops == []


def test_public_ip_detection():
    assert is_public_ip("8.8.8.8")
    assert not is_public_ip("172.16.0.1")
    assert not is_public_ip("100.64.0.1")   # carrier-grade NAT
