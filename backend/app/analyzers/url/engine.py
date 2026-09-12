import math
import re
from dataclasses import dataclass, field
from typing import List, Optional
import tldextract

from app.analyzers.url.normalizer import NormalizedURL
from app.analyzers.url.network_safety import classify_hostname_safety
from app.schemas.threat import (
    EvidenceItem,
    EvidenceCategory,
    EvidenceSeverity,
    TechnicalMetadata,
)

HIGH_RISK_TLDS = {
    "xyz", "top", "work", "live", "click", "link", "loan", "buzz", "surf",
    "monster", "fit", "rest", "cam", "quest", "cfd", "sbs", "icu", "gq",
    "ml", "tk", "ga", "cf", "pw", "cc", "ws"
}

SUSPICIOUS_SUBDOMAINS_OR_SERVICES = [
    "workers.dev", "pages.dev", "vercel.app", "glitch.me", "netlify.app",
    "web.app", "firebaseapp.com", "duckdns.org", "ngrok-free.app", "ngrok.io",
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
    "steam": ["steampowered.com", "steamcommunity.com"],
    "roblox": ["roblox.com"],
}

PHISHING_LEXICAL_KEYWORDS = [
    "login", "verify", "verification", "secure", "account", "update",
    "password", "wallet", "banking", "payment", "authentication", "recovery",
    "signin", "confirm", "support", "security", "billing", "invoice",
    "authenticate", "credential", "suspend", "unlock", "alert", "validate"
]

OPEN_REDIRECT_PARAMS = {
    "url", "redirect", "redirect_url", "redirect_uri", "next", "dest",
    "destination", "return", "return_to", "r", "goto", "out"
}

DANGEROUS_EXTENSIONS = {
    ".exe", ".scr", ".bat", ".cmd", ".ps1", ".vbs", ".js", ".iso", ".img",
    ".zip", ".rar", ".7z", ".tar", ".gz", ".apk", ".dmg", ".pkg", ".docm", ".xlsm"
}

COMMON_PORTS = {80, 443, 8080, 8443}


def calculate_shannon_entropy(text: str) -> float:
    """Calculates Shannon entropy to detect DGA / randomized domain strings."""
    if not text:
        return 0.0
    text_lower = text.lower()
    freq: dict[str, int] = {}
    for char in text_lower:
        freq[char] = freq.get(char, 0) + 1
    entropy = 0.0
    for count in freq.values():
        p = count / len(text_lower)
        entropy -= p * math.log2(p)
    return round(entropy, 2)


@dataclass
class HeuristicAnalysisResult:
    normalized_url: NormalizedURL
    metadata: TechnicalMetadata
    findings: List[EvidenceItem] = field(default_factory=list)
    detected_brands: List[str] = field(default_factory=list)
    is_private_network: bool = False


def analyze_url_heuristics(norm_url: NormalizedURL) -> HeuristicAnalysisResult:
    """Performs deterministic static analysis on a normalized URL.
    
    Zero outbound requests. Zero code execution. Completely SSRF-safe.
    """
    findings: List[EvidenceItem] = []
    detected_brands: List[str] = []

    # 1. Static Network Safety Classification
    net_class = classify_hostname_safety(norm_url.host)
    is_private_network = net_class.is_private_or_local

    if net_class.is_private_or_local:
        findings.append(
            EvidenceItem(
                category=EvidenceCategory.INFRASTRUCTURE,
                severity=EvidenceSeverity.CRITICAL,
                title="Internal Network / Localhost Destination",
                description=net_class.explanation or "Target routes to private or loopback IP range.",
                technical_proof=f"Classification: {net_class.classification} | Host: {norm_url.host}",
                why_this_matters=(
                    "Target addresses internal services or loopback interfaces. "
                    "In enterprise or web applications, submission of internal addresses is a primary indicator of SSRF attempts."
                ),
            )
        )

    if net_class.is_raw_ip and not net_class.is_private_or_local:
        findings.append(
            EvidenceItem(
                category=EvidenceCategory.INFRASTRUCTURE,
                severity=EvidenceSeverity.HIGH,
                title="Direct Public IP Destination",
                description="Target URL routes directly to a raw public IP address rather than an accredited domain name.",
                technical_proof=f"Raw IP: {norm_url.host}",
                why_this_matters=(
                    "Legitimate organizations almost never provide raw numerical IP addresses in public user-facing communications. "
                    "Attackers use IP addresses to bypass domain reputation blocklists."
                ),
            )
        )

    # 2. Extract Domain & Subdomain hierarchy using tldextract
    ext = tldextract.extract(norm_url.normalized_url)
    subdomain = ext.subdomain
    registered_domain = ext.registered_domain
    domain = ext.domain
    suffix = ext.suffix

    entropy = calculate_shannon_entropy(domain)

    # 3. Embedded Credentials in Authority
    if norm_url.has_credentials:
        findings.append(
            EvidenceItem(
                category=EvidenceCategory.CONTENT,
                severity=EvidenceSeverity.HIGH,
                title="Credentials Embedded in URL Authority",
                description="URL includes explicit userinfo/password credentials before the host delimiter (@).",
                technical_proof=f"User: {norm_url.user or 'redacted'} | Host: {norm_url.host}",
                why_this_matters=(
                    "Embedding user credentials in URLs is an obsolete pattern often used to disguise actual destinations "
                    "or leak authorization secrets across access logs."
                ),
            )
        )

    # 4. Brand Impersonation & Targeted Phishing
    host_lower = norm_url.host.lower()
    for brand, legit_domains in TARGETED_BRANDS.items():
        if brand in host_lower:
            is_legit = any(registered_domain == legit_d or registered_domain.endswith(f".{legit_d}") for legit_d in legit_domains)
            if not is_legit:
                detected_brands.append(brand)
                findings.append(
                    EvidenceItem(
                        category=EvidenceCategory.IDENTITY,
                        severity=EvidenceSeverity.CRITICAL,
                        title=f"Brand Impersonation Detected: {brand.upper()}",
                        description=(
                            f"The target hostname mentions '{brand}', but the registered domain '{registered_domain}' "
                            f"has no verified cryptographic or organizational affiliation with {brand.upper()}."
                        ),
                        technical_proof=(
                            f"Hostname: {norm_url.host} | Registered Domain: {registered_domain} | "
                            f"Official Brand Domains: {', '.join(legit_domains)}"
                        ),
                        why_this_matters=(
                            "Credential harvesting operations routinely weaponize trademarked brand names in subdomains or deceptive "
                            "root domains to instill false trust in victims."
                        ),
                    )
                )

    # 5. High-Risk TLD Abuse
    if suffix in HIGH_RISK_TLDS:
        findings.append(
            EvidenceItem(
                category=EvidenceCategory.REPUTATION,
                severity=EvidenceSeverity.HIGH,
                title=f"High-Risk Top-Level Domain (.{suffix})",
                description=f"The top-level domain '.{suffix}' exhibits statistically elevated abuse and zero-day threat prevalence.",
                technical_proof=f"TLD: .{suffix} | Domain: {registered_domain}",
                why_this_matters=(
                    "Disposable or ultra-low-cost TLDs are preferred by adversaries for disposable phishing infrastructure "
                    "due to lenient identity registration requirements."
                ),
            )
        )

    # 6. Ephemeral Cloud / Dynamic DNS Hosting Abuse
    for suspicious_host in SUSPICIOUS_SUBDOMAINS_OR_SERVICES:
        if suspicious_host in host_lower:
            findings.append(
                EvidenceItem(
                    category=EvidenceCategory.INFRASTRUCTURE,
                    severity=EvidenceSeverity.HIGH,
                    title="Public Tunnel / Ephemeral App Hosting Abuse",
                    description=f"Target operates on '{suspicious_host}', a public developer tunnel or free hosting platform.",
                    technical_proof=f"Host matches platform signature: {suspicious_host}",
                    why_this_matters=(
                        "Adversaries leverage free cloud application providers to evade IP reputation filters "
                        "and gain free HTTPS padlocks on landing pages."
                    ),
                )
            )

    # 7. Phishing-Oriented Lexical Indicators
    matched_keywords: list[str] = []
    full_path_query = (norm_url.path + "?" + norm_url.query).lower()
    for kw in PHISHING_LEXICAL_KEYWORDS:
        if kw in host_lower or kw in full_path_query:
            matched_keywords.append(kw)

    if len(matched_keywords) >= 2:
        findings.append(
            EvidenceItem(
                category=EvidenceCategory.CONTENT,
                severity=EvidenceSeverity.MEDIUM,
                title=f"Phishing Lexical Keywords Present ({len(matched_keywords)} triggers)",
                description=f"URL contains multiple terms associated with account credential lures: {', '.join(matched_keywords[:5])}.",
                technical_proof=f"Keywords matched: {', '.join(matched_keywords)}",
                why_this_matters=(
                    "Social engineering campaigns construct URLs around account maintenance, urgent validation, or security alerts "
                    "to induce psychological compliance."
                ),
            )
        )
    elif len(matched_keywords) == 1 and detected_brands:
        findings.append(
            EvidenceItem(
                category=EvidenceCategory.CONTENT,
                severity=EvidenceSeverity.HIGH,
                title="Brand Paired with Credential Lure Keyword",
                description=f"Impersonated brand '{detected_brands[0]}' is directly paired with credential keyword '{matched_keywords[0]}'.",
                technical_proof=f"Brand: {detected_brands[0]} | Keyword: {matched_keywords[0]}",
                why_this_matters="Direct combination of brand name and verification keyword is a signature phishing lure structure.",
            )
        )

    # 8. Excessive Subdomain Depth
    subdomain_parts = [p for p in subdomain.split(".") if p]
    if len(subdomain_parts) >= 3:
        findings.append(
            EvidenceItem(
                category=EvidenceCategory.INFRASTRUCTURE,
                severity=EvidenceSeverity.MEDIUM,
                title=f"Excessive Subdomain Depth ({len(subdomain_parts)} levels)",
                description=f"Hostname contains {len(subdomain_parts)} nested subdomain levels, typical of deep lure nesting.",
                technical_proof=f"Subdomain: {subdomain}",
                why_this_matters=(
                    "Adversaries build multi-level subdomains to push the actual registered domain off mobile address bar viewports."
                ),
            )
        )

    # 9. Excessive Length
    url_len = len(norm_url.raw_url)
    if url_len > 250:
        findings.append(
            EvidenceItem(
                category=EvidenceCategory.CONTENT,
                severity=EvidenceSeverity.MEDIUM,
                title=f"Excessive URL Length ({url_len} characters)",
                description="URL length exceeds normal ergonomic standards, potentially concealing destination parameters.",
                technical_proof=f"Length: {url_len} chars",
                why_this_matters="Obfuscated and tracking-heavy exploit URLs often exceed 250 characters to hide payload strings.",
            )
        )

    # 10. Unusual Network Port
    if norm_url.port and norm_url.port not in COMMON_PORTS:
        findings.append(
            EvidenceItem(
                category=EvidenceCategory.INFRASTRUCTURE,
                severity=EvidenceSeverity.MEDIUM,
                title=f"Non-Standard Web Port (Port {norm_url.port})",
                description=f"URL specifies custom port {norm_url.port} instead of standard web ports 80/443.",
                technical_proof=f"Port: {norm_url.port}",
                why_this_matters=(
                    "Adversaries frequently run ad-hoc phishing services or C2 proxies on arbitrary high-numbered ports."
                ),
            )
        )

    # 11. Deceptive Hyphenation (Lookalike tricks)
    hyphen_count = domain.count("-")
    if hyphen_count >= 3:
        findings.append(
            EvidenceItem(
                category=EvidenceCategory.IDENTITY,
                severity=EvidenceSeverity.LOW,
                title=f"Excessive Hyphenation in Domain ({hyphen_count} hyphens)",
                description=f"Domain '{domain}' contains multiple hyphens, often used to string together disparate brand keywords.",
                technical_proof=f"Hyphens: {hyphen_count} in '{domain}'",
                why_this_matters="Typosquatters use hyphenated keyword combos to approximate legitimate company service names.",
            )
        )

    # 12. Shannon Entropy (Randomized / DGA Domain)
    if entropy >= 3.8 and len(domain) >= 10:
        findings.append(
            EvidenceItem(
                category=EvidenceCategory.INFRASTRUCTURE,
                severity=EvidenceSeverity.MEDIUM,
                title=f"High Domain Shannon Entropy ({entropy})",
                description="Domain name exhibits high randomness, consistent with Domain Generation Algorithms (DGA).",
                technical_proof=f"Domain: {domain} | Entropy: {entropy} (threshold: 3.8)",
                why_this_matters=(
                    "DGAs dynamically generate random domain names to maintain resilient command-and-control communication "
                    "against static blocklists."
                ),
            )
        )

    # 13. Internationalized Domain Names (IDN / Punycode)
    if norm_url.is_idn:
        findings.append(
            EvidenceItem(
                category=EvidenceCategory.IDENTITY,
                severity=EvidenceSeverity.MEDIUM,
                title="Internationalized Domain / Punycode (IDN)",
                description="Domain uses Punycode/IDN encoding, which can facilitate visual homograph spoofing.",
                technical_proof=f"Punycode Host: {norm_url.ascii_host}",
                why_this_matters=(
                    "Homograph attacks substitute Cyrillic, Greek, or Unicode glyphs that render identically to Latin characters "
                    "in browsers to spoof trusted domains."
                ),
            )
        )

    # 14. Dangerous File Attachment / Download Target
    path_lower = norm_url.path.lower()
    for ext_candidate in DANGEROUS_EXTENSIONS:
        if path_lower.endswith(ext_candidate) or f"{ext_candidate}?" in path_lower:
            findings.append(
                EvidenceItem(
                    category=EvidenceCategory.CONTENT,
                    severity=EvidenceSeverity.HIGH,
                    title=f"Direct Executable/Archive Download Target ({ext_candidate})",
                    description=f"URL terminates in a direct download of a potential malware file extension ({ext_candidate}).",
                    technical_proof=f"File extension: {ext_candidate} in path '{norm_url.path}'",
                    why_this_matters=(
                        "Links designed to immediately initiate binary or script downloads upon visit are standard malware delivery vectors."
                    ),
                )
            )
            break

    # 15. Open Redirect Parameters
    if norm_url.query:
        query_lower = norm_url.query.lower()
        for param in OPEN_REDIRECT_PARAMS:
            if f"{param}=" in query_lower:
                findings.append(
                    EvidenceItem(
                        category=EvidenceCategory.INFRASTRUCTURE,
                        severity=EvidenceSeverity.LOW,
                        title=f"Potential Open Redirect Parameter ('{param}')",
                        description=f"Query string contains redirect parameter '{param}', often abused to bounce victims to hostile targets.",
                        technical_proof=f"Parameter matched: {param}",
                        why_this_matters="Open redirects allow attackers to use legitimate domains as initial lures before redirecting to malicious servers.",
                    )
                )
                break

    metadata = TechnicalMetadata(
        domain=norm_url.host,
        subdomain=subdomain,
        registered_domain=registered_domain,
        tld=suffix,
        ip_addresses=[],
        entropy=entropy,
        detected_brands=detected_brands,
        extracted_urls=[norm_url.normalized_url],
        social_engineering_flags=matched_keywords,
    )

    return HeuristicAnalysisResult(
        normalized_url=norm_url,
        metadata=metadata,
        findings=findings,
        detected_brands=detected_brands,
        is_private_network=is_private_network,
    )
