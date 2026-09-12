from typing import Optional
from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    environment: str
    database: Optional[str] = "not_connected"
    cache: Optional[str] = "not_connected"


class RootResponse(BaseModel):
    brand: str
    product: str
    status: str
    version: str
    docs_url: str
