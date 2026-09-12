import uuid
from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import DateTime, ForeignKey, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base
from app.models.base import UUIDMixin

if TYPE_CHECKING:
    from app.models.scan import Scan


class Finding(Base, UUIDMixin):
    """Forensic indicator or heuristic finding associated with a specific scan."""

    __tablename__ = "findings"

    scan_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("scans.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    indicator_type: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )

    indicator: Mapped[str] = mapped_column(
        String(512),
        nullable=False,
    )

    severity: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
    )

    source: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )

    explanation: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    scan: Mapped["Scan"] = relationship(
        "Scan",
        back_populates="findings",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Finding id={self.id} scan_id={self.scan_id} severity={self.severity} type={self.indicator_type}>"
