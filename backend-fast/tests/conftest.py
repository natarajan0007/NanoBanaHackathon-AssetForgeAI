import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
import sys

# Add project root to the path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.main import app
from app.core.database import get_db, Base
from app.models import User, Organization
from app.core.security import get_password_hash
from app.models.user import UserRole

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables for all tests
Base.metadata.create_all(bind=engine)

@pytest.fixture(scope="session", autouse=True)
def db_setup_and_teardown():
    # Setup: create the database file and tables
    Base.metadata.create_all(bind=engine)
    yield
    # Teardown: remove the database file after tests are done
    os.remove("test.db")

@pytest.fixture(scope="function")
def db_session():
    """Fixture for a clean database session for each test function."""
    connection = engine.connect()
    transaction = connection.begin()
    db = TestingSessionLocal(bind=connection)

    yield db

    db.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope="function")
def client(db_session):
    """Fixture for the FastAPI TestClient."""
    def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    del app.dependency_overrides[get_db]

@pytest.fixture(scope="function")
def test_organization(db_session):
    """Fixture to create a test organization."""
    org = Organization(name="Test Corp")
    db_session.add(org)
    db_session.commit()
    db_session.refresh(org)
    return org

@pytest.fixture(scope="function")
def admin_user(db_session, test_organization):
    """Fixture to create an admin user."""
    user = User(
        username="testadmin",
        email="testadmin@example.com",
        hashed_password=get_password_hash("adminpass"),
        role=UserRole.ADMIN,
        organization_id=test_organization.id
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture(scope="function")
def regular_user(db_session, test_organization):
    """Fixture to create a regular user."""
    user = User(
        username="testuser",
        email="testuser@example.com",
        hashed_password=get_password_hash("userpass"),
        role=UserRole.USER,
        organization_id=test_organization.id
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture(scope="function")
def admin_token(client, admin_user):
    """Fixture to get an admin user's auth token."""
    response = client.post(
        "/api/v1/auth/login",
        json={"username": admin_user.username, "password": "adminpass"}
    )
    return response.json()["accessToken"]

@pytest.fixture(scope="function")
def regular_user_token(client, regular_user):
    """Fixture to get a regular user's auth token."""
    response = client.post(
        "/api/v1/auth/login",
        json={"username": regular_user.username, "password": "userpass"}
    )
    return response.json()["accessToken"]
