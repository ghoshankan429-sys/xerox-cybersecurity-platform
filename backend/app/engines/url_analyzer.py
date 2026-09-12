import math
import re
import socket
import ssl
import time
from datetime import datetime, timezone
from urllib.parse import urlparse
import dns.resolver
import httpx
import tldextract

from app.schemas.threat import (
    DNSRecords,
    SSLCertInfo,
    RedirectHop,
    TechnicalMetadata,
    EvidenceItem,
    EvidenceCategory,
    EvidenceSeverity,
)

HIGH_RISK_TLDS = {
    "xyz", "top", "work", "live", "click", "link", "loan", "buzz", "surf", 
    "monster", "fit", "rest", "cam", "quest", "cfd", "sbs", "icu", "gq", "ml", "tk", "ga"
}

SUSPICIOUS_SUBDOMAINS_OR_SERVICES = [
    "workers.dev", "pages.dev", "vercel.app", "glitch.me", "netlify.app", 
    "web.app", "firebaseapp.com", "duckdns.org", "ngrok-free.app", "ngrok.io"
]

TARGETED_BRANDS = {
    "apple": ["apple.com", "icloud.com"],
    "paypal": ["paypal.com"],
    "google": ["google.com", "accounts.google.com"],
    "microsoft": ["microsoft.com", "live.com", "office.com", "office365.com", "outlook.com"],
    "netflix": ["netflix.com"],
    "amazon": ["amazon.com", "primevideo.com"],
    "chase": ["chase.com"],
    "wellsfargo": ["wellsfargo.com"],
    "bankofamerica": ["bankofamerica.com"],
    "binance": ["binance.com"],
    "coinbase": ["coinbase.com"],
    "facebook": ["facebook.com", "meta.com"],
    "instagram": ["instagram.com"],
    "whatsapp": ["whatsapp.com"],
    "usps": ["usps.com"],
    "dhl": ["dhl.com"],
    "fedex": ["fedex.com"],
    "ups": ["ups.com"],
    "irs": ["irs.gov"],
}

def defang_url(url: str) -> str:
    """Safely defangs URLs to prevent accidental client-side clicking."""
    defanged = url.replace("http://", "hxxp://").replace("https://", "hxxps://")
    defanged = re.sub(r"\.(?=[a-zA-Z0-9_-])", "[.]", defanged)
    return defanged

def normalize_url(raw_url: str) -> str:
    """Normalizes input URL, refangs user defanged inputs, ensures protocol."""
    cleaned = raw_url.strip()
    # Refang
    cleaned = cleaned.replace("hxxps://", "https://").replace("hxxp://", "http://")
    cleaned = cleaned.replace("[.]", ".")
    cleaned = cleaned.replace("(.)", ".")
    if not cleaned.startswith("http://") and not cleaned.startswith("https://"):
        cleaned = "https://" + cleaned
    return cleaned

def calculate_shannon_entropy(text: str) -> float:
    """Calculates Shannon entropy to detect DGA/randomized domain generation."""
    if not text:
        return 0.0
    text_lower = text.lower()
    freq = {}
    for char in text_lower:
        freq[char] = freq.get(char, 0) + 1
    entropy = 0.0
    for count in freq.values():
        p = count / len(text_lower)
        entropy -= p * math.log2(p)
    return round(entropy, 2)

async def resolve_dns(domain: str) -> tuple[DNSRecords, list[str]]:
    dns_records = DNSRecords()
    ip_addresses: list[str] = []
    resolver = dns.resolver.Resolver()
    resolver.timeout = 2.5
    resolver.lifetime = 2.5

    # A Records
    try:
        answers = resolver.resolve(domain, "A")
        dns_records.a = [r.to_text() for r in answers]
        ip_addresses.extend(dns_records.a)
    except Exception:
        pass

    # AAAA Records
    try:
        answers = resolver.resolve(domain, "AAAA")
        dns_records.aaaa = [r.to_text() for r in answers]
    except Exception:
        pass

    # MX Records
    try:
        answers = resolver.resolve(domain, "MX")
        dns_records.mx = [r.to_text() for r in answers]
    except Exception:
        pass

    # NS Records
    try:
        answers = resolver.resolve(domain, "NS")
        dns_records.ns = [r.to_text() for r in answers]
    except Exception:
        pass

    return dns_records, ip_addresses

def inspect_ssl(hostname: str) -> SSLCertInfo:
    info = SSLCertInfo()
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE

    try:
        with socket.create_connection((hostname, 443), timeout=3.0) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert(binary_form=False)
                if not cert:
                    cert_bin = ssock.getpeercert(binary_form=True)
                    if cert_bin:
                        info.is_valid = True
                        info.issuer = "Encoded Binary Certificate"
                    return info

                # Extract Issuer & Subject
                issuer_dict = dict(x[0] for x in cert.get("issuer", []))
                subject_dict = dict(x[0] for x in cert.get("subject", []))
                
                info.issuer = issuer_dict.get("organizationName") or issuer_dict.get("commonName") or "Unknown"
                info.subject = subject_dict.get("commonName") or hostname
                
                not_before = cert.get("notBefore")
                not_after = cert.get("notAfter")
                info.valid_from = not_before
                info.valid_until = not_after

                if not_after:
                    # e.g., 'May 20 23:59:59 2026 GMT'
                    try:
                        exp_date = datetime.strptime(not_after, "%b %d %H:%M:%S %Y %Z").replace(tzinfo=timezone.utc)
                        remaining = (exp_date - datetime.now(timezone.utc)).days
                        info.days_remaining = remaining
                        info.is_valid = remaining > 0
                    except Exception:
                        info.is_valid = True
                else:
                    info.is_valid = True

                # Self-signed check
                if issuer_dict == subject_dict:
                    info.is_self_signed = True

    except Exception:
        info.is_valid = False
    return info

async def trace_redirects(start_url: str) -> list[RedirectHop]:
    hops: list[RedirectHop] = []
    current_url = start_url

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Xerox-Security/1.0"
    }

    try:
        async with httpx.AsyncClient(follow_redirects=False, timeout=5.0, verify=False) as client:
            for hop_idx in range(1, 8):
                t0 = time.time()
                try:
                    resp = await client.get(current_url, headers=headers)
                    duration_ms = round((time.time() - t0) * 1000, 1)
                    
                    next_url = None
                    if resp.is_redirect and "location" in resp.headers:
                        loc = resp.headers["location"]
                        if loc.startswith("/"):
                            parsed = urlparse(current_url)
                            next_url = f"{parsed.scheme}://{parsed.netloc}{loc}"
                        elif not loc.startswith("http"):
                            parsed = urlparse(current_url)
                            next_url = f"{parsed.scheme}://{parsed.netloc}/{loc}"
                        else:
                            next_url = loc

                    hops.append(
                        RedirectHop(
                            hop_number=hop_idx,
                            from_url=current_url,
                            to_url=next_url or current_url,
                            status_code=resp.status_code,
                            response_time_ms=duration_ms,
                        )
                    )

                    if not next_url or next_url == current_url:
                        break
                    current_url = next_url
                except httpx.RequestError:
                    hops.append(
                        RedirectHop(
                            hop_number=hop_idx,
                            from_url=current_url,
                            to_url=current_url,
                            status_code=0,
                            response_time_ms=0.0,
                        )
                    )
                    break
    except Exception:
        pass

    return hops

async def analyze_url_target(raw_url: str) -> tuple[TechnicalMetadata, list[EvidenceItem], list[str]]:
    """Performs end-to-end technical inspection of the URL."""
    norm_url = normalize_url(raw_url)
    parsed = urlparse(norm_url)
    hostname = parsed.hostname or ""

    # Extract domains
    ext = tldextract.extract(norm_url)
    subdomain = ext.subdomain
    registered_domain = ext.registered_domain
    domain = ext.domain
    suffix = ext.suffix

    entropy = calculate_shannon_entropy(domain)
    dns_records, ip_addresses = await resolve_dns(hostname)
    ssl_info = inspect_ssl(hostname)
    redirect_hops = await trace_redirects(norm_url)

    evidence_items: list[EvidenceItem] = []
    detected_brands: list[str] = []
    social_flags: list[str] = []

    # 1. Brand Impersonation Check
    lower_host = hostname.lower()
    for brand, legit_domains in TARGETED_BRANDS.items():
        if brand in lower_host:
            is_legit = any(legit_d in registered_domain for legit_d in legit_domains)
            if not is_legit:
                detected_brands.append(brand)
                evidence_items.append(
                    EvidenceItem(
                        category=EvidenceCategory.IDENTITY,
                        severity=EvidenceSeverity.CRITICAL,
                        title=f"Brand Impersonation Detected: {brand.upper()}",
                        description=f"The domain mentions '{brand}', but the registered entity '{registered_domain}' does not belong to the official brand.",
                        technical_proof=f"Hostname: {hostname} | Registered Domain: {registered_domain} | Official Domains: {', '.join(legit_domains)}",
                        why_this_matters="Phishing kits commonly include trusted corporate brand names in lookalike domains or subdomains to deceive victims into submitting credentials."
                    )
                )

    # 2. High Risk TLD Check
    if suffix in HIGH_RISK_TLDS:
        evidence_items.append(
            EvidenceItem(
                category=EvidenceCategory.REPUTATION,
                severity=EvidenceSeverity.HIGH,
                title=f"High-Risk Top-Level Domain (.{suffix})",
                description=f"The top-level domain '.{suffix}' exhibits an elevated rate of malicious abuse and cybercriminal activity across global threat intelligence feeds.",
                technical_proof=f"TLD: .{suffix}",
                why_this_matters="Disposable or ultra-cheap TLDs are frequently preferred by threat actors for zero-day phishing operations because they lack strict KYC registration verification."
            )
        )

    # 3. Dynamic DNS / Free Hosting Infrastructure Abuse
    for suspicious_host in SUSPICIOUS_SUBDOMAINS_OR_SERVICES:
        if suspicious_host in lower_host:
            evidence_items.append(
                EvidenceItem(
                    category=EvidenceCategory.INFRASTRUCTURE,
                    severity=EvidenceSeverity.HIGH,
                    title="Public Tunnel / Ephemeral Cloud Hosting Abuse",
                    description=f"The target utilizes '{suspicious_host}', a free public cloud hosting or tunneling platform frequently co-opted to host credential harvesting landing pages.",
                    technical_proof=f"Host signature: {hostname}",
                    why_this_matters="Adversaries use free application hosting and tunnels to evade traditional reputation firewalls by riding on trusted root domains."
                )
            )

    # 4. IP-in-URL Detection
    if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", hostname):
        evidence_items.append(
            EvidenceItem(
                category=EvidenceCategory.INFRASTRUCTURE,
                severity=EvidenceSeverity.HIGH,
                title="Direct IP Address In URL Destination",
                description="The target URL bypasses domain name registration and points directly to a raw public IP address.",
                technical_proof=f"Direct IP: {hostname}",
                why_this_matters="Legitimate financial, corporate, and social institutions almost never present raw numerical IP addresses to end users."
            )
        )

    # 5. DNS Presence Validation
    if not dns_records.a and not dns_records.aaaa:
        evidence_items.append(
            EvidenceItem(
                category=EvidenceCategory.INFRASTRUCTURE,
                severity=EvidenceSeverity.MEDIUM,
                title="No Valid DNS Resolution (NXDOMAIN or Dormant)",
                description="DNS servers were unable to resolve standard A or AAAA records for this host. The server may be dormant, offline, or takedown-quarantined.",
                technical_proof=f"Resolver failed query for {hostname}",
                why_this_matters="Dead or rapid-flux domains that drop offline quickly are common after automated security takedown notifications."
            )
        )

    # 6. High Shannon Entropy (DGA Detection)
    if entropy > 3.8 and len(domain) > 10:
        evidence_items.append(
            EvidenceItem(
                category=EvidenceCategory.INFRASTRUCTURE,
                severity=EvidenceSeverity.MEDIUM,
                title="High Domain Randomness (Potential DGA)",
                description=f"The domain name has an unusually high Shannon entropy score ({entropy}), indicating algorithmic or randomized character generation.",
                technical_proof=f"Domain token: '{domain}' has entropy score {entropy} (threshold: 3.8)",
                why_this_matters="Domain Generation Algorithms (DGAs) generate random-looking domain strings to dynamically bypass static blocklists."
            )
        )

    # 7. Redirect Chain Analysis
    if len(redirect_hops) > 2:
        evidence_items.append(
            EvidenceItem(
                category=EvidenceCategory.INFRASTRUCTURE,
                severity=EvidenceSeverity.MEDIUM,
                title=f"Multi-Hop Redirection Chain ({len(redirect_hops)} hops)",
                description="The target link passes through multiple intermediate redirect locations before terminating at its final destination.",
                technical_proof=f"Initial: {redirect_hops[0].from_url} -> Final: {redirect_hops[-1].to_url}",
                why_this_matters="Attackers use layered redirect hops and URL shorteners to evade crawler inspection and disguise the destination site."
            )
        )

    # 8. SSL Certificate Inspection
    if ssl_info.is_self_signed:
        evidence_items.append(
            EvidenceItem(
                category=EvidenceCategory.CRYPTOGRAPHY,
                severity=EvidenceSeverity.HIGH,
                title="Self-Signed SSL/TLS Certificate",
                description="The website serves an untrusted self-signed certificate rather than one issued by an accredited public Certificate Authority.",
                technical_proof=f"Issuer matches Subject: {ssl_info.issuer}",
                why_this_matters="Untrusted certificates enable Man-In-The-Middle (MITM) attacks and indicate non-standard, rogue server administration."
            )
        )
    elif ssl_info.is_valid:
        evidence_items.append(
            EvidenceItem(
                category=EvidenceCategory.CRYPTOGRAPHY,
                severity=EvidenceSeverity.INFO,
                title="Active SSL/TLS Certificate Present",
                description=f"The connection is encrypted with a certificate issued by {ssl_info.issuer}.",
                technical_proof=f"Issuer: {ssl_info.issuer} | Days Remaining: {ssl_info.days_remaining}",
                why_this_matters="Valid encryption protects communication in transit, but note that 80%+ of modern phishing websites also deploy free TLS certificates."
            )
        )

    metadata = TechnicalMetadata(
        domain=hostname,
        subdomain=subdomain,
        registered_domain=registered_domain,
        tld=suffix,
        ip_addresses=ip_addresses,
        dns=dns_records,
        ssl=ssl_info,
        redirect_hops=redirect_hops,
        entropy=entropy,
        detected_brands=detected_brands,
        extracted_urls=[norm_url],
        social_engineering_flags=social_flags,
    )

    return metadata, evidence_items, detected_brands
