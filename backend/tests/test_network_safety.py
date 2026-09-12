import pytest
from app.analyzers.url.network_safety import (
    classify_hostname_safety,
    NetworkClassification,
)


def test_ipv4_private_ranges():
    """RFC 1918 addresses must be classified as PRIVATE without network requests."""
    for ip in ("10.0.0.1", "172.16.5.10", "172.31.255.254", "192.168.1.1"):
        res = classify_hostname_safety(ip)
        assert res.is_private_or_local is True
        assert res.is_raw_ip is True
        assert res.classification == "PRIVATE_RFC1918_IP"
        assert res.ip_version == 4


def test_ipv4_loopback():
    """127.0.0.0/8 addresses must be classified as LOOPBACK."""
    for ip in ("127.0.0.1", "127.1.2.3"):
        res = classify_hostname_safety(ip)
        assert res.is_private_or_local is True
        assert res.is_raw_ip is True
        assert res.classification == "LOOPBACK_IP"
        assert res.ip_version == 4


def test_ipv4_link_local_and_reserved():
    """169.254.0.0/16 and 0.0.0.0 must be recognized as LINK_LOCAL / RESERVED."""
    res_ll = classify_hostname_safety("169.254.1.1")
    assert res_ll.is_private_or_local is True
    assert res_ll.is_raw_ip is True
    assert res_ll.classification == "LINK_LOCAL_IP"

    res_res = classify_hostname_safety("0.0.0.0")
    assert res_res.is_private_or_local is True
    assert res_res.classification == "RESERVED_OR_MULTICAST_IP"


def test_ipv4_multicast():
    """224.0.0.0/4 multicast range."""
    res = classify_hostname_safety("224.0.0.1")
    assert res.is_private_or_local is True
    assert res.classification == "RESERVED_OR_MULTICAST_IP"


def test_ipv6_loopback_and_special():
    """IPv6 loopback, link-local, and unique-local must be correctly categorized."""
    res_loop = classify_hostname_safety("::1")
    assert res_loop.is_private_or_local is True
    assert res_loop.classification == "LOOPBACK_IP"
    assert res_loop.ip_version == 6

    res_ll = classify_hostname_safety("fe80::1")
    assert res_ll.is_private_or_local is True
    assert res_ll.classification == "LINK_LOCAL_IP"

    res_ula = classify_hostname_safety("fc00::1")
    assert res_ula.is_private_or_local is True
    assert res_ula.classification == "PRIVATE_RFC1918_IP"


def test_localhost_literals():
    """Localhost names must be classified as LOCAL_DOMAIN."""
    for host in ("localhost", "localhost.localdomain", "myhost.local", "router.internal"):
        res = classify_hostname_safety(host)
        assert res.is_private_or_local is True
        assert res.is_raw_ip is False
        assert res.classification == "LOCAL_DOMAIN"


def test_public_ip():
    """Public internet IP addresses must be classified as PUBLIC_IP_LITERAL."""
    for ip in ("8.8.8.8", "1.1.1.1"):
        res = classify_hostname_safety(ip)
        assert res.is_private_or_local is False
        assert res.is_raw_ip is True
        assert res.classification == "PUBLIC_IP_LITERAL"


def test_domain_names_are_domain_classification():
    """Regular domain names must be classified as PUBLIC_DOMAIN."""
    for domain in ("example.com", "google.com", "phishing-portal.xyz"):
        res = classify_hostname_safety(domain)
        assert res.is_private_or_local is False
        assert res.is_raw_ip is False
        assert res.classification == "PUBLIC_DOMAIN"
