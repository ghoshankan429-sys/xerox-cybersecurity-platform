import uuid
from datetime import datetime
from typing import Any, Dict, Optional, TYPE_CHECKING
from sqlalchemy import DateTime, ForeignKey, JSON, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base
from app.models.base import UUIDMixin

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.scan import Scan


class AuditLog(Base, UUIDMixin):
    """Immutable audit trail for security events, scan actions, and administrative activity."""

    __tablename__ = "audit_logs"

    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )

    scan_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("scans.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )

    event_type: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )

    details: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    user: Mapped[Optional["User"]] = relationship(
        "User",
        back_populates="audit_logs",
        lazy="selectin",
    )

    scan: Mapped[Optional["Scan"]] = relationship(
        "Scan",
        back_populates="audit_logs",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<AuditLog id={self.id} event={self.event_type} user_id={self.user_id} scan_id={self.scan_id}>"
