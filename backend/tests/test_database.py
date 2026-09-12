import os
from pathlib import Path
import uuid
import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from alembic import command
from alembic.config import Config

from app.database.session import AsyncSessionLocal, check_db_health
from app.models.user import User
from app.models.scan import Scan
from app.models.finding import Finding
from app.models.audit_log import AuditLog
from app.models.feedback import Feedback


@pytest.mark.asyncio
async def test_database_health_check():
    """Verify that check_db_health successfully executes SELECT 1 and returns connected."""
    res = await check_db_health()
    assert res["status"] == "connected"
    assert "details" in res


@pytest.mark.asyncio
async def test_user_creation_and_constraints():
    """Verify User model creation, UUID generation, timestamps, and unique email constraint."""
    unique_email = f"analyst_{uuid.uuid4().hex[:8]}@xerox.sec"

    async with AsyncSessionLocal() as session:
        user = User(
            email=unique_email,
            password_hash="$argon2id$fake_hash_for_testing",
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)

        assert isinstance(user.id, uuid.UUID)
        assert user.email == unique_email
        assert user.created_at is not None
        assert user.updated_at is not None

    # Test unique constraint on email
    async with AsyncSessionLocal() as session:
        dup_user = User(
            email=unique_email,
            password_hash="$argon2id$another_hash",
        )
        session.add(dup_user)
        with pytest.raises(IntegrityError):
            await session.commit()


@pytest.mark.asyncio
async def test_model_relationships_and_cascades():
    """Verify complete relationship graph: User -> Scan -> Finding/Feedback/AuditLog."""
    user_email = f"tenant_{uuid.uuid4().hex[:8]}@xerox.sec"

    async with AsyncSessionLocal() as session:
        user = User(
            email=user_email,
            password_hash="test_secret_hash",
        )
        session.add(user)
        await session.flush()

        # 1. Create Scan
        scan = Scan(
            user_id=user.id,
            input_type="url",
            input_hash="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            risk_score=92,
            verdict="CRITICAL",
        )
        session.add(scan)
        await session.flush()

        # 2. Create Finding
        finding = Finding(
            scan_id=scan.id,
            indicator_type="brand_impersonation",
            indicator="apple-id-verify.support-secure.live",
            severity="CRITICAL",
            source="heuristic_domain_engine",
            explanation="Unregistered domain attempting credential harvest against Apple ID.",
        )
        session.add(finding)

        # 3. Create Feedback
        feedback = Feedback(
            user_id=user.id,
            scan_id=scan.id,
            feedback="Accurately flagged active phishing infrastructure.",
        )
        session.add(feedback)

        # 4. Create AuditLog
        audit_log = AuditLog(
            user_id=user.id,
            scan_id=scan.id,
            event_type="scan_completed",
            details={"risk_score": 92, "verdict": "CRITICAL", "duration_ms": 142.5},
        )
        session.add(audit_log)

        await session.commit()

    # Re-query and verify relationships
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User).where(User.email == user_email)
        )
        fetched_user = result.scalar_one()

        assert len(fetched_user.scans) == 1
        assert fetched_user.scans[0].risk_score == 92
        assert len(fetched_user.scans[0].findings) == 1
        assert fetched_user.scans[0].findings[0].severity == "CRITICAL"
        assert len(fetched_user.scans[0].feedback) == 1
        assert len(fetched_user.audit_logs) == 1
        assert fetched_user.audit_logs[0].event_type == "scan_completed"


@pytest.mark.asyncio
async def test_per_user_scan_isolation():
    """Verify that scan queries strictly scoped to user_id isolate data between tenants."""
    user_a_email = f"user_a_{uuid.uuid4().hex[:8]}@xerox.sec"
    user_b_email = f"user_b_{uuid.uuid4().hex[:8]}@xerox.sec"

    async with AsyncSessionLocal() as session:
        user_a = User(email=user_a_email, password_hash="hash_a")
        user_b = User(email=user_b_email, password_hash="hash_b")
        session.add_all([user_a, user_b])
        await session.flush()

        scan_a1 = Scan(
            user_id=user_a.id,
            input_type="url",
            input_hash="hash_a1",
            risk_score=10,
            verdict="BENIGN",
        )
        scan_a2 = Scan(
            user_id=user_a.id,
            input_type="message",
            input_hash="hash_a2",
            risk_score=85,
            verdict="HIGH RISK",
        )
        scan_b1 = Scan(
            user_id=user_b.id,
            input_type="url",
            input_hash="hash_b1",
            risk_score=50,
            verdict="SUSPICIOUS",
        )
        session.add_all([scan_a1, scan_a2, scan_b1])
        await session.commit()

        user_a_id = user_a.id
        user_b_id = user_b.id

    # Query with strict user_id scoping
    async with AsyncSessionLocal() as session:
        scans_user_a = (
            await session.execute(select(Scan).where(Scan.user_id == user_a_id))
        ).scalars().all()
        scans_user_b = (
            await session.execute(select(Scan).where(Scan.user_id == user_b_id))
        ).scalars().all()

        assert len(scans_user_a) == 2
        assert all(s.user_id == user_a_id for s in scans_user_a)
        assert not any(s.input_hash == "hash_b1" for s in scans_user_a)

        assert len(scans_user_b) == 1
        assert scans_user_b[0].input_hash == "hash_b1"
        assert scans_user_b[0].user_id == user_b_id


def test_alembic_migration_lifecycle(tmp_path):
    """Verify that Alembic can migrate head, downgrade base, and re-upgrade cleanly in an isolated database."""
    test_db_file = tmp_path / "test_migration.db"
    test_db_url = f"sqlite+aiosqlite:///{test_db_file}"

    ini_path = Path("backend/alembic.ini") if Path("backend/alembic.ini").exists() else Path("alembic.ini")
    alembic_cfg = Config(str(ini_path))
    alembic_cfg.set_main_option("sqlalchemy.url", test_db_url)

    # 1. Fresh database migration to head
    command.upgrade(alembic_cfg, "head")

    # 2. Downgrade back to base
    command.downgrade(alembic_cfg, "base")

    # 3. Reapply migration to head
    command.upgrade(alembic_cfg, "head")


@pytest.mark.asyncio
async def test_health_endpoint_db_status(async_client):
    """Verify that the FastAPI health endpoint checks and reports database status."""
    res = await async_client.get("/api/v1/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"

    alias_res = await async_client.get("/api/health")
    assert alias_res.status_code == 200
    assert alias_res.json()["database"] == "connected"
