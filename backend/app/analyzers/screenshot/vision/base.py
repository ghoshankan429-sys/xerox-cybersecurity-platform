from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Any


@dataclass(frozen=True)
class VisionExtractionResult:
    """Structured evidence extracted from a screenshot image via OCR/vision analysis."""
    raw_text: str = ""
    visible_urls: List[str] = field(default_factory=list)
    visible_domains: List[str] = field(default_factory=list)
    visible_emails: List[str] = field(default_factory=list)
    detected_brands: List[str] = field(default_factory=list)
    visual_elements: List[str] = field(default_factory=list)
    confidence_score: float = 0.0
    provider_name: str = "unknown"
    is_available: bool = False
    status_message: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


class VisionProvider(ABC):
    """Abstract interface for OCR and visual analysis providers."""

    @abstractmethod
    async def extract(self, image_bytes: bytes, mime_type: str) -> VisionExtractionResult:
        """Extracts structured text, IOCs, and visual elements from untrusted image bytes."""
        pass
