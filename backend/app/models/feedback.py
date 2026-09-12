import uuid
from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import DateTime, ForeignKey, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base
from app.models.base import UUIDMixin

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.scan import Scan


class Feedback(Base, UUIDMixin):
    """User feedback and analyst tuning submissions on specific investigation results."""

    __tablename__ = "feedback"

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    scan_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("scans.id", ondelete="CASCADE"),
        nullable=False,
    )

    feedback: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="feedback",
        lazy="selectin",
    )

    scan: Mapped["Scan"] = relationship(
        "Scan",
        back_populates="feedback",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Feedback id={self.id} user_id={self.user_id} scan_id={self.scan_id}>"
