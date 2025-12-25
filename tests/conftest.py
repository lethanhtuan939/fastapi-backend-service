import os
import pytest

# Setup environment variables before importing app modules
# This ensures that settings.DATABASE_URL is populated when app.core.config is loaded
TEST_DB_PATH = os.path.join(os.path.dirname(__file__), "db_test.db")
DATABASE_URL = f"sqlite:///{TEST_DB_PATH}"

os.environ["DATABASE_URL"] = DATABASE_URL
os.environ["SECRET_KEY"] = "test_secret_key"

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app
from app.models.base import Base
from app.dependencies import get_db

# Create engine for SQLite
# check_same_thread=False is needed for SQLite with multiple threads (like in FastAP)
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """
    Create the test database and tables before tests run.
    Drop them after tests complete.
    """
    # Create tables
    Base.metadata.create_all(bind=engine)
    yield
    # Drop tables/cleanup
    Base.metadata.drop_all(bind=engine)
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)


@pytest.fixture(scope="function")
def db_session():
    """
    Get a new database session for a test.
    Rollback logic is handled by specific test requirements or implicit transaction.
    Here we provide a fresh session.
    """
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="module")
def client():
    """
    Test client with overridden database dependency.
    """
    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
