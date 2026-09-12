"""Initial database schema for users, scans, findings, audit_logs, and feedback.

Revision ID: 0001_initial_schema
Revises: 
Create Date: 2026-09-12 21:55:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. users table
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_users")),
    )
    op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)

    # 2. scans table
    op.create_table(
        "scans",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("input_type", sa.String(length=32), nullable=False),
        sa.Column("input_hash", sa.String(length=64), nullable=False),
        sa.Column("risk_score", sa.Integer(), nullable=False),
        sa.Column("verdict", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name=op.f("fk_scans_user_id_users"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_scans")),
    )
    op.create_index(op.f("ix_scans_id"), "scans", ["id"], unique=False)
    op.create_index(op.f("ix_scans_user_id"), "scans", ["user_id"], unique=False)
    op.create_index(op.f("ix_scans_input_hash"), "scans", ["input_hash"], unique=False)
    op.create_index(op.f("ix_scans_created_at"), "scans", ["created_at"], unique=False)

    # 3. findings table
    op.create_table(
        "findings",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("scan_id", sa.Uuid(), nullable=False),
        sa.Column("indicator_type", sa.String(length=64), nullable=False),
        sa.Column("indicator", sa.String(length=512), nullable=False),
        sa.Column("severity", sa.String(length=32), nullable=False),
        sa.Column("source", sa.String(length=64), nullable=False),
        sa.Column("explanation", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.ForeignKeyConstraint(["scan_id"], ["scans.id"], name=op.f("fk_findings_scan_id_scans"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_findings")),
    )
    op.create_index(op.f("ix_findings_id"), "findings", ["id"], unique=False)
    op.create_index(op.f("ix_findings_scan_id"), "findings", ["scan_id"], unique=False)

    # 4. audit_logs table
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=True),
        sa.Column("scan_id", sa.Uuid(), nullable=True),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("details", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name=op.f("fk_audit_logs_user_id_users"), ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["scan_id"], ["scans.id"], name=op.f("fk_audit_logs_scan_id_scans"), ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_audit_logs")),
    )
    op.create_index(op.f("ix_audit_logs_id"), "audit_logs", ["id"], unique=False)
    op.create_index(op.f("ix_audit_logs_user_id"), "audit_logs", ["user_id"], unique=False)
    op.create_index(op.f("ix_audit_logs_scan_id"), "audit_logs", ["scan_id"], unique=False)

    # 5. feedback table
    op.create_table(
        "feedback",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("scan_id", sa.Uuid(), nullable=False),
        sa.Column("feedback", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name=op.f("fk_feedback_user_id_users"), ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["scan_id"], ["scans.id"], name=op.f("fk_feedback_scan_id_scans"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_feedback")),
    )
    op.create_index(op.f("ix_feedback_id"), "feedback", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_feedback_id"), table_name="feedback")
    op.drop_table("feedback")

    op.drop_index(op.f("ix_audit_logs_scan_id"), table_name="audit_logs")
    op.drop_index(op.f("ix_audit_logs_user_id"), table_name="audit_logs")
    op.drop_index(op.f("ix_audit_logs_id"), table_name="audit_logs")
    op.drop_table("audit_logs")

    op.drop_index(op.f("ix_findings_scan_id"), table_name="findings")
    op.drop_index(op.f("ix_findings_id"), table_name="findings")
    op.drop_table("findings")

    op.drop_index(op.f("ix_scans_created_at"), table_name="scans")
    op.drop_index(op.f("ix_scans_input_hash"), table_name="scans")
    op.drop_index(op.f("ix_scans_user_id"), table_name="scans")
    op.drop_index(op.f("ix_scans_id"), table_name="scans")
    op.drop_table("scans")

    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_index(op.f("ix_users_id"), table_name="users")
    op.drop_table("users")
