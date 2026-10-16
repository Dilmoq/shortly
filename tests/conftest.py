"""Pytest fixtures: isolated test database and API client."""

import os
import tempfile

import pytest
from fastapi.testclient import TestClient

# Point the app at a temporary SQLite file BEFORE importing app modules,
# so create_engine uses the test URL.
_tmpdir = tempfile.mkdtemp(prefix="shortly-tests-")
os.environ["SHORTLY_DATABASE_URL"] = f"sqlite:///{_tmpdir}test.db".replace("\\", "/")
os.environ["SHORTLY_BASE_URL"] = "http://testserver/"


@pytest.fixture()
def client() -> TestClient:
    """A TestClient bound to the app with clean tables per test."""
    from app.database import Base, engine, init_db
    from app.main import create_app

    init_db()
    yield TestClient(create_app())
    Base.metadata.drop_all(bind=engine)
