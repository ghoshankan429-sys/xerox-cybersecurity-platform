import uuid
from typing import List, TYPE_CHECKING
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base
from app.models.base import UUIDMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.scan import Scan
    from app.models.audit_log import AuditLog
    from app.models.feedback import Feedback


class User(Base, UUIDMixin, TimestampMixin):
    """User account model for authentication and tenant isolation."""

    __tablename__ = "users"

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    # Relationships
    scans: Mapped[List["Scan"]] = relationship(
        "Scan",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    audit_logs: Mapped[List["AuditLog"]] = relationship(
        "AuditLog",
        back_populates="user",
        lazy="selectin",
    )

    feedback: Mapped[List["Feedback"]] = relationship(
        "Feedback",
        back_populates="user",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email}>"
