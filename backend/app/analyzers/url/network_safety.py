import ipaddress
import re
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class NetworkClassification:
    is_private_or_local: bool
    is_raw_ip: bool
    classification: Optional[str]
    ip_version: Optional[int]
    explanation: Optional[str]


# Localhost and mDNS / local domain suffixes
LOCAL_DOMAINS = {
    "localhost",
    "local",
    "localdomain",
    "internal",
    "corp",
    "lan",
    "home",
}


def classify_hostname_safety(hostname: str) -> NetworkClassification:
    """Statically analyzes hostname to identify private, loopback, or reserved network destinations.
    
    CRITICAL SECURITY GUARANTEE:
    This function NEVER initiates network sockets, DNS resolution, or HTTP traffic.
    It protects against SSRF by identifying addresses destined for internal perimeters.
    """
    cleaned = hostname.strip().lower().rstrip(".")

    # 1. Check for localhost literals or local domain suffixes
    parts = cleaned.split(".")
    if cleaned in LOCAL_DOMAINS or (len(parts) > 1 and parts[-1] in LOCAL_DOMAINS):
        return NetworkClassification(
            is_private_or_local=True,
            is_raw_ip=False,
            classification="LOCAL_DOMAIN",
            ip_version=None,
            explanation=(
                f"Hostname '{hostname}' resolves to an internal local domain or loopback environment. "
                "Target is prohibited from outbound network resolution."
            ),
        )

    # 2. Check if hostname is an IPv4 or IPv6 literal
    ip_str = cleaned.strip("[]")  # Handle IPv6 bracket format [::1]

    try:
        ip_obj = ipaddress.ip_address(ip_str)
        is_raw_ip = True
        ip_version = ip_obj.version

        if ip_obj.is_loopback:
            return NetworkClassification(
                is_private_or_local=True,
                is_raw_ip=True,
                classification="LOOPBACK_IP",
                ip_version=ip_version,
                explanation=f"Target points directly to loopback IP address '{ip_str}'.",
            )

        if ip_obj.is_link_local:
            return NetworkClassification(
                is_private_or_local=True,
                is_raw_ip=True,
                classification="LINK_LOCAL_IP",
                ip_version=ip_version,
                explanation=f"Target points directly to link-local IP address '{ip_str}'.",
            )

        if ip_obj.is_reserved or ip_obj.is_multicast or ip_obj.is_unspecified:
            return NetworkClassification(
                is_private_or_local=True,
                is_raw_ip=True,
                classification="RESERVED_OR_MULTICAST_IP",
                ip_version=ip_version,
                explanation=f"Target points directly to reserved, multicast, or unspecified IP address '{ip_str}'.",
            )

        if ip_obj.is_private:
            return NetworkClassification(
                is_private_or_local=True,
                is_raw_ip=True,
                classification="PRIVATE_RFC1918_IP",
                ip_version=ip_version,
                explanation=f"Target points directly to private RFC 1918 / ULA IP address '{ip_str}'.",
            )

        # Public IP address literal
        return NetworkClassification(
            is_private_or_local=False,
            is_raw_ip=True,
            classification="PUBLIC_IP_LITERAL",
            ip_version=ip_version,
            explanation=(
                f"Target uses raw public numerical IP '{ip_str}' instead of an accredited domain name."
            ),
        )

    except ValueError:
        # Not an IP address literal; standard domain name
        pass

    # Safe public domain format
    return NetworkClassification(
        is_private_or_local=False,
        is_raw_ip=False,
        classification="PUBLIC_DOMAIN",
        ip_version=None,
        explanation=None,
    )
