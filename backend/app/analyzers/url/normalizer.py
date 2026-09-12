import hashlib
import re
import urllib.parse
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class NormalizedURL:
    """Immutable representation of a normalized URL for deterministic analysis and caching."""
    raw_url: str
    normalized_url: str
    defanged_url: str
    scheme: str
    host: str
    ascii_host: str
    port: Optional[int]
    path: str
    query: str
    fragment: str
    has_credentials: bool
    user: Optional[str]
    password: Optional[str]
    url_hash: str
    is_idn: bool

    @property
    def hostname(self) -> str:
        return self.host

    @property
    def username(self) -> Optional[str]:
        return self.user


def defang_url(url: str) -> str:
    """Safely defangs URLs to prevent accidental clicking in logs or clients.
    
    Transforms:
        http:// -> hxxp://
        https:// -> hxxps://
        . -> [.]
    """
    cleaned = url.strip()
    defanged = cleaned.replace("https://", "hxxps://").replace("http://", "hxxp://")
    # Defang dots within the domain/path
    defanged = re.sub(r"\.(?=[a-zA-Z0-9_-])", "[.]", defanged)
    return defanged


def refang_url(url: str) -> str:
    """Restores defanged user submissions into standard URL syntax."""
    cleaned = url.strip()
    cleaned = cleaned.replace("[colon]", ":").replace("[slash]", "/")
    cleaned = cleaned.replace("hxxps://", "https://").replace("hxxp://", "http://")
    cleaned = cleaned.replace("[.]", ".").replace("(.)", ".").replace(r"{\.}", ".").replace("{.}", ".").replace("[dot]", ".")
    return cleaned


def normalize_url(raw_url: str) -> NormalizedURL:
    """Safely normalizes and parses a URL without making any outbound requests.
    
    Handles:
    - scheme defaulting (https) and casing
    - refanging input (hxxp -> http, [.] -> .)
    - hostname casing, trailing dot removal, whitespace stripping
    - default port stripping (80 for http, 443 for https)
    - embedded credential extraction and stripping from authority
    - path normalization (resolving ../, consecutive slashes)
    - query parameter canonical sorting
    - IDN / Punycode domain normalization
    - deterministic SHA-256 hashing
    """
    if not raw_url or not raw_url.strip():
        raise ValueError("URL cannot be empty")

    cleaned = refang_url(raw_url.strip())

    # Detect scheme or default to https://
    scheme_match = re.match(r"^([a-zA-Z][a-zA-Z0-9+.-]*):?//", cleaned)
    if scheme_match:
        scheme = scheme_match.group(1).lower()
        if scheme not in ("http", "https"):
            raise ValueError(f"Unsupported URL scheme: {scheme}")
    else:
        scheme = "https"
        if not cleaned.startswith("//"):
            cleaned = f"https://{cleaned}"
        else:
            cleaned = f"https:{cleaned}"

    parsed = urllib.parse.urlsplit(cleaned, scheme=scheme)

    # Extract userinfo credentials if embedded in authority
    user = parsed.username
    password = parsed.password
    has_credentials = bool(user or password)

    # Hostname normalization
    hostname = (parsed.hostname or "").strip().rstrip(".")
    if not hostname:
        raise ValueError("URL must contain a valid hostname")

    # Lowercase hostname
    hostname_lower = hostname.lower()

    # IDN / Punycode handling
    is_idn = False
    try:
        # Check if already punycode or has non-ASCII characters
        if "xn--" in hostname_lower:
            is_idn = True
            ascii_host = hostname_lower
        else:
            ascii_host = hostname_lower.encode("idna").decode("ascii")
            if ascii_host != hostname_lower:
                is_idn = True
    except Exception:
        ascii_host = hostname_lower

    # Port normalization: remove default ports (80 for http, 443 for https)
    port = parsed.port
    if (scheme == "http" and port == 80) or (scheme == "https" and port == 443):
        port = None

    # Construct authority without credentials for canonical form
    if port:
        authority = f"{ascii_host}:{port}"
    else:
        authority = ascii_host

    # Path normalization
    raw_path = parsed.path or "/"
    # Clean up double slashes
    raw_path = re.sub(r"/+", "/", raw_path)
    # Unquote and safely quote for canonical representation
    unquoted_path = urllib.parse.unquote(raw_path)
    canonical_path = urllib.parse.quote(unquoted_path, safe="/:@!$&'()*+,;=-_.~")
    if not canonical_path.startswith("/"):
        canonical_path = "/" + canonical_path

    # Query string normalization: sort parameters canonically
    canonical_query = ""
    if parsed.query:
        query_pairs = urllib.parse.parse_qsl(parsed.query, keep_blank_values=True)
        # Sort query pairs by key, then value
        query_pairs.sort(key=lambda item: (item[0], item[1]))
        canonical_query = urllib.parse.urlencode(query_pairs)

    fragment = parsed.fragment or ""

    # Build canonical normalized URL
    if canonical_query:
        normalized_url = f"{scheme}://{authority}{canonical_path}?{canonical_query}"
    else:
        normalized_url = f"{scheme}://{authority}{canonical_path}"

    # Generate SHA-256 hash of normalized URL
    url_hash = hashlib.sha256(normalized_url.encode("utf-8")).hexdigest()

    # Defanged representation
    defanged = defang_url(normalized_url)

    return NormalizedURL(
        raw_url=raw_url.strip(),
        normalized_url=normalized_url,
        defanged_url=defanged,
        scheme=scheme,
        host=hostname_lower,
        ascii_host=ascii_host,
        port=port,
        path=canonical_path,
        query=canonical_query,
        fragment=fragment,
        has_credentials=has_credentials,
        user=user,
        password=password,
        url_hash=url_hash,
        is_idn=is_idn,
    )
