from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class ThreatIntelStatus(str, Enum):
    CLEAN = "CLEAN"
    SUSPICIOUS = "SUSPICIOUS"
    MALICIOUS = "MALICIOUS"
    UNKNOWN = "UNKNOWN"
    UNAVAILABLE = "UNAVAILABLE"
    RATE_LIMITED = "RATE_LIMITED"
    NOT_CONFIGURED = "NOT_CONFIGURED"


class ThreatIntelResult(BaseModel):
    provider_name: str = "VirusTotal"
    status: ThreatIntelStatus = ThreatIntelStatus.UNKNOWN
    malicious_count: int = 0
    suspicious_count: int = 0
    harmless_count: int = 0
    undetected_count: int = 0
    total_engines: int = 0
    permalink: Optional[str] = None
    categories: List[str] = Field(default_factory=list)
    cached: bool = False
    raw_summary: Optional[str] = None
