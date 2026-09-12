import ipaddress
import re
from dataclasses import dataclass, field
from typing import List, Set

from app.analyzers.message.normalizer import NormalizedMessage
from app.analyzers.url.normalizer import refang_url


@dataclass(frozen=True)
class ExtractedIOCs:
    """Structured Indicators of Compromise extracted from a message without network interaction."""
    urls: List[str] = field(default_factory=list)
    domains: List[str] = field(default_factory=list)
    ipv4_addresses: List[str] = field(default_factory=list)
    ipv6_addresses: List[str] = field(default_factory=list)
    email_addresses: List[str] = field(default_factory=list)
    phone_numbers: List[str] = field(default_factory=list)


# URL patterns matching schemes, www prefixes, and defanged indicators
URL_REGEX = re.compile(
    r"""
    (?i)
    \b
    (?:
        (?:https?|hxxps?|ftp)://[^\s<>"'{}|\\^`]+
        |
        www\.[^\s<>"'{}|\\^`]+
        |
        [a-zA-Z0-9_-]+(?:\[\.\]|\(\.\)|\{\\\.\}|\{\.\}|\.)(?:com|net|org|xyz|top|live|info|me|app|dev|co|io|cc|vip|biz|online|site|store|ru|cn|link|click|work|buzz)[^\s<>"'{}|\\^`]*
    )
    """,
    re.VERBOSE,
)

# Email address pattern
EMAIL_REGEX = re.compile(
    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
)

# IPv4 pattern (candidate matches validated by ipaddress module)
IPV4_CANDIDATE_REGEX = re.compile(
    r"\b(?:\d{1,3}\.){3}\d{1,3}\b"
)

# Phone number pattern (E.164 and international format)
PHONE_REGEX = re.compile(
    r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"
)

PUNCTUATION_TO_STRIP = ".,;:!?()[]{}<>\"'“”‘’"


def clean_url_candidate(candidate: str) -> str:
    """Strips trailing and leading punctuation commonly attached in text."""
    cleaned = candidate.strip()
    while cleaned and cleaned[-1] in PUNCTUATION_TO_STRIP:
        cleaned = cleaned[:-1]
    while cleaned and cleaned[0] in PUNCTUATION_TO_STRIP:
        cleaned = cleaned[1:]
    return cleaned.strip()


def extract_iocs(message: NormalizedMessage) -> ExtractedIOCs:
    """Passively extracts unique URLs, domains, IP addresses, and emails from a normalized message.
    
    GUARANTEE:
    This function performs ZERO network sockets, DNS requests, or external calls.
    """
    text = f"{message.subject or ''}\n{message.normalized_content}\n{message.sender or ''}\n{message.sender_metadata or ''}"

    extracted_urls: List[str] = []
    seen_urls: Set[str] = set()

    extracted_domains: List[str] = []
    seen_domains: Set[str] = set()

    extracted_ipv4: List[str] = []
    seen_ipv4: Set[str] = set()

    extracted_ipv6: List[str] = []
    seen_ipv6: Set[str] = set()

    extracted_emails: List[str] = []
    seen_emails: Set[str] = set()

    extracted_phones: List[str] = []
    seen_phones: Set[str] = set()

    # 1. Extract Email Addresses
    for match in EMAIL_REGEX.finditer(text):
        email = match.group(0).lower()
        if email not in seen_emails:
            seen_emails.add(email)
            extracted_emails.append(email)
            # Also extract domain portion
            domain_part = email.split("@")[1].strip()
            if domain_part not in seen_domains:
                seen_domains.add(domain_part)
                extracted_domains.append(domain_part)

    # 2. Extract URLs
    for match in URL_REGEX.finditer(text):
        raw_url = clean_url_candidate(match.group(0))
        if not raw_url:
            continue

        # Refang the candidate to evaluate cleanly
        refanged = refang_url(raw_url)
        if refanged not in seen_urls:
            seen_urls.add(refanged)
            extracted_urls.append(refanged)

            # Extract domain from URL
            domain_match = re.search(r"^(?:https?://)?(?:www\.)?([^/:\s?#]+)", refanged, re.IGNORECASE)
            if domain_match:
                d = domain_match.group(1).lower()
                # Check if it's an IP
                try:
                    ip_obj = ipaddress.ip_address(d)
                    if ip_obj.version == 4 and str(ip_obj) not in seen_ipv4:
                        seen_ipv4.add(str(ip_obj))
                        extracted_ipv4.append(str(ip_obj))
                    elif ip_obj.version == 6 and str(ip_obj) not in seen_ipv6:
                        seen_ipv6.add(str(ip_obj))
                        extracted_ipv6.append(str(ip_obj))
                except ValueError:
                    if d not in seen_domains and "." in d:
                        seen_domains.add(d)
                        extracted_domains.append(d)

    # 3. Extract Standalone IPv4 Addresses
    for match in IPV4_CANDIDATE_REGEX.finditer(text):
        ip_cand = match.group(0)
        try:
            ip_obj = ipaddress.IPv4Address(ip_cand)
            ip_str = str(ip_obj)
            if ip_str not in seen_ipv4:
                seen_ipv4.add(ip_str)
                extracted_ipv4.append(ip_str)
        except ipaddress.AddressValueError:
            pass

    # 4. Extract Standalone Phone Numbers
    for match in PHONE_REGEX.finditer(text):
        phone_cand = match.group(0).strip()
        digits = re.sub(r"\D", "", phone_cand)
        if 10 <= len(digits) <= 15 and phone_cand not in seen_phones:
            seen_phones.add(phone_cand)
            extracted_phones.append(phone_cand)

    return ExtractedIOCs(
        urls=extracted_urls,
        domains=extracted_domains,
        ipv4_addresses=extracted_ipv4,
        ipv6_addresses=extracted_ipv6,
        email_addresses=extracted_emails,
        phone_numbers=extracted_phones,
    )
