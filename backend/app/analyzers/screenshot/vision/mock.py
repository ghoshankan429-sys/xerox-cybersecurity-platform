from typing import Optional, List
from app.analyzers.screenshot.vision.base import VisionProvider, VisionExtractionResult


class MockVisionProvider(VisionProvider):
    """Mock vision provider for unit testing and deterministic offline pipelines."""

    def __init__(
        self,
        raw_text: str = "",
        visible_urls: Optional[List[str]] = None,
        visible_domains: Optional[List[str]] = None,
        visible_emails: Optional[List[str]] = None,
        detected_brands: Optional[List[str]] = None,
        visual_elements: Optional[List[str]] = None,
        confidence_score: float = 95.0,
        is_available: bool = True,
        status_message: str = "Mock vision extraction successful.",
    ):
        self.result = VisionExtractionResult(
            raw_text=raw_text,
            visible_urls=visible_urls or [],
            visible_domains=visible_domains or [],
            visible_emails=visible_emails or [],
            detected_brands=detected_brands or [],
            visual_elements=visual_elements or [],
            confidence_score=confidence_score,
            provider_name="mock",
            is_available=is_available,
            status_message=status_message,
        )

    async def extract(self, image_bytes: bytes, mime_type: str) -> VisionExtractionResult:
        return self.result
