"""XEROX Scans API Router.

Re-exports the production PostgreSQL-backed analysis router from `app.api.v1.analyze`.
All scan operations persist to PostgreSQL with strict authenticated tenant isolation.
"""
from app.api.v1.analyze import router

__all__ = ["router"]
