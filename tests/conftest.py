import os
import sys
from pathlib import Path

# Add the project root directory to Python path
project_root = str(Path(__file__).parent.parent)
sys.path.insert(0, project_root)

# Load test environment variables BEFORE importing any other modules
from dotenv import load_dotenv
load_dotenv('.env.test', override=True)  # Force override existing env vars

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from datetime import datetime, timedelta

from src.db.base import Base
from src.db.session import get_db
from src.main import app
from src.core.config import settings
from src.db.models import User, Role
from src.core.security import create_access_token, get_password_hash
from src.core.enums import RoleEnum

# Test database configuration - use test environment variables
TEST_DB_NAME = settings.MYSQL_DATABASE
TEST_DB_USER = settings.MYSQL_USER
TEST_DB_PASSWORD = settings.MYSQL_PASSWORD
TEST_DB_HOST = settings.MYSQL_HOST
TEST_DB_PORT = settings.MYSQL_PORT

# Test database URL
TEST_DATABASE_URL = f"mysql+pymysql://{TEST_DB_USER}:{TEST_DB_PASSWORD}@{TEST_DB_HOST}:{TEST_DB_PORT}/{TEST_DB_NAME}"

@pytest.fixture(scope="session")
def engine():
    # Create test database if not exists
    base_url = f"mysql+pymysql://{TEST_DB_USER}:{TEST_DB_PASSWORD}@{TEST_DB_HOST}:{TEST_DB_PORT}"
    engine = create_engine(base_url, poolclass=StaticPool)
    with engine.connect() as conn:
        # Create test database if not exists
        conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {TEST_DB_NAME}"))
        conn.execute(text(f"USE {TEST_DB_NAME}"))
        conn.commit()
    
    # Create tables in test database
    test_engine = create_engine(TEST_DATABASE_URL)
    Base.metadata.create_all(bind=test_engine)
    return test_engine

@pytest.fixture(scope="function")
def db_session(engine):
    """Creates a new database session for a test."""
    connection = engine.connect()
    transaction = connection.begin()
    Session = sessionmaker(bind=connection)
    session = Session()

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()

@pytest.fixture(scope="session", autouse=True)
def cleanup_test_db(engine):
    """Cleanup test database after all tests."""
    yield
    # Only drop test database, not the main database
    with engine.connect() as conn:
        conn.execute(text(f"DROP DATABASE IF EXISTS {TEST_DB_NAME}"))
        conn.commit()

@pytest.fixture(scope="function")
def client(db_session):
    # Override the get_db dependency
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture(scope="session")
def test_role(engine):
    """Create test role if not exists"""
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        # Check if role exists
        role = session.query(Role).filter(Role.name == "user").first()
        if not role:
            role = Role(
                id=RoleEnum.USER.value,  # Use USER enum value (2)
                name="user",
            )
            session.add(role)
            session.commit()  # Commit role creation
            session.refresh(role)
        print(f"Test role created/found: {role.id} - {role.name}")
        return role
    finally:
        session.close()

@pytest.fixture(scope="function")
def test_user(db_session, test_role):
    """Create test user"""
    user = User(
        email="test@example.com",
        username="testuser",
        full_name="Test User",
        password=get_password_hash("password"),
        role_id=test_role.id,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture(scope="function")
def test_user_token(test_user):
    """Create access token for test user"""
    return create_access_token(
        data={"sub": str(test_user.id)},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

@pytest.fixture(scope="function")
def auth_headers(test_user_token):
    """Create authentication headers"""
    return {"Authorization": f"Bearer {test_user_token}"}

@pytest.fixture(scope="function")
def expired_token(test_user):
    """Create expired access token"""
    return create_access_token(
        data={"sub": str(test_user.id)},
        expires_delta=timedelta(microseconds=1)
    ) 