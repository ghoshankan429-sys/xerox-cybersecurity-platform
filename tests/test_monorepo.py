import os
from pathlib import Path


def test_monorepo_structure():
    """Verify monorepo directories and configuration files exist."""
    root = Path(__file__).parent.parent
    assert (root / "frontend").is_dir(), "frontend directory missing"
    assert (root / "backend").is_dir(), "backend directory missing"
    assert (root / "docs").is_dir(), "docs directory missing"
    assert (root / "tests").is_dir(), "tests directory missing"
    assert (root / ".github").is_dir(), ".github directory missing"
    assert (root / ".env.example").is_file(), ".env.example missing"
    assert (root / "README.md").is_file(), "README.md missing"


def test_backend_structure():
    """Verify backend modules specified in roadmap exist."""
    app = Path(__file__).parent.parent / "backend" / "app"
    required_backend_dirs = [
        "api",
        "core",
        "models",
        "schemas",
        "services",
        "security",
        "analyzers",
        "threat_intel",
        "ai",
        "cache",
        "database",
        "workers",
    ]
    for d in required_backend_dirs:
        assert (app / d).is_dir(), f"backend/app/{d} directory missing"


def test_frontend_structure():
    """Verify frontend feature modules specified in roadmap exist."""
    src = Path(__file__).parent.parent / "frontend" / "src"
    required_frontend_dirs = [
        "components",
        "pages",
        "layouts",
        "features",
        "services",
        "hooks",
        "types",
        "lib",
    ]
    for d in required_frontend_dirs:
        assert (src / d).is_dir(), f"frontend/src/{d} directory missing"

    required_features = [
        "auth",
        "dashboard",
        "analysis",
        "history",
        "reports",
        "settings",
    ]
    for feat in required_features:
        assert (src / "features" / feat).is_dir(), f"frontend/src/features/{feat} missing"
