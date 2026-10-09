"""Test setup.

* Detection tests need no database.
* API tests run against MySQL. Set TEST_DATABASE_URL to a separate, empty test
  database, e.g. (PowerShell):

      $env:TEST_DATABASE_URL="mysql+pymysql://root:YOUR_PASSWORD@localhost:3306/scamlens_test"

  The test database is created if missing and its tables are emptied after every test.
  If TEST_DATABASE_URL is not set, the API tests are skipped (detection tests still run).
"""
import os
import sys
from pathlib import Path

import pytest

BACKEND = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(BACKEND))

# Never touch the real scamlens_db during tests.
os.environ["SCAMLENS_SKIP_DB_INIT"] = "1"
os.environ["DATABASE_URL"] = os.getenv("TEST_DATABASE_URL",
                                       "mysql+pymysql://root:unused@localhost:3306/scamlens_test")
for optional in ("ANTHROPIC_API_KEY", "GOOGLE_SAFE_BROWSING_API_KEY"):
    os.environ[optional] = ""
os.environ["ENABLE_URL_FETCH"] = "false"

TEST_DB = os.getenv("TEST_DATABASE_URL")


@pytest.fixture()
def client():
    if not TEST_DB:
        pytest.skip("TEST_DATABASE_URL is not set — skipping API tests that need MySQL")
    from fastapi.testclient import TestClient
    from sqlalchemy import create_engine, text
    from sqlalchemy.engine import URL, make_url
    from sqlalchemy.orm import sessionmaker

    from app import models  # noqa: F401
    from app.database import Base, get_db
    from app.main import app

    url = make_url(TEST_DB)
    server = create_engine(URL.create(url.drivername, username=url.username, password=url.password,
                                      host=url.host, port=url.port, query=url.query))
    with server.connect() as conn:
        conn.execute(text(f"CREATE DATABASE IF NOT EXISTS `{url.database}` CHARACTER SET utf8mb4"))
    server.dispose()

    engine = create_engine(TEST_DB, pool_pre_ping=True)
    Base.metadata.create_all(engine)
    TestSession = sessionmaker(bind=engine, expire_on_commit=False)

    def override_db():
        db = TestSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    with engine.begin() as conn:
        conn.execute(text("SET FOREIGN_KEY_CHECKS=0"))
        for table in ("reports", "findings", "scans"):
            conn.execute(text(f"TRUNCATE TABLE {table}"))
        conn.execute(text("SET FOREIGN_KEY_CHECKS=1"))
    engine.dispose()
