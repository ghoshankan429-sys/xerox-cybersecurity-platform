import uuid
from datetime import datetime
from typing import List, TYPE_CHECKING
from sqlalchemy import DateTime, ForeignKey, Integer, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base
from app.models.base import UUIDMixin
from app.core.datetime_utils import get_monotonic_utc_now

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.finding import Finding
    from app.models.feedback import Feedback
    from app.models.audit_log import AuditLog


class Scan(Base, UUIDMixin):
    """Investigation scan record strictly scoped to an authenticated user."""

    __tablename__ = "scans"

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    input_type: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
    )

    input_hash: Mapped[str] = mapped_column(
        String(64),
        index=True,
        nullable=False,
    )

    risk_score: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    verdict: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=get_monotonic_utc_now,
        server_default=func.now(),
        index=True,
        nullable=False,
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="scans",
        lazy="selectin",
    )

    findings: Mapped[List["Finding"]] = relationship(
        "Finding",
        back_populates="scan",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    feedback: Mapped[List["Feedback"]] = relationship(
        "Feedback",
        back_populates="scan",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    audit_logs: Mapped[List["AuditLog"]] = relationship(
        "AuditLog",
        back_populates="scan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Scan id={self.id} user_id={self.user_id} score={self.risk_score} verdict={self.verdict}>"
