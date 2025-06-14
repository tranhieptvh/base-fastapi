import os
import sys
from pathlib import Path

# Add the project root directory to Python path
project_root = str(Path(__file__).parent.parent)
sys.path.insert(0, project_root)

# Load test environment variables BEFORE importing any other modules
from dotenv import load_dotenv
# Only load .env.test if not in a CI environment (like GitHub Actions)
if not os.getenv('CI'):
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

# The single source of truth for the database URL
TEST_DATABASE_URL = settings.DATABASE_URL

@pytest.fixture(scope="session")
def engine():
    # Use the unified DATABASE_URL from settings
    test_engine = create_engine(TEST_DATABASE_URL, poolclass=StaticPool)

    # Create test database if not exists - MORE ROBUST WAY
    db_name = test_engine.url.database
    # Manually construct the base URL without the database name
    base_url = (
        f"{test_engine.url.drivername}://{test_engine.url.username}:{test_engine.url.password}"
        f"@{test_engine.url.host}:{test_engine.url.port}"
    )

    with create_engine(base_url).connect() as conn:
        conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {db_name}"))
        conn.commit()
    
    # Connect to the specific test database to create tables
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
    db_name = engine.url.database
    with engine.connect() as conn:
        conn.execute(text(f"DROP DATABASE IF EXISTS {db_name}"))
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

# region Roles & Users Fixtures

# --- Admin Fixtures ---

@pytest.fixture(scope="session")
def admin_role(engine):
    """Create admin role if not exists"""
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        role = session.query(Role).filter(Role.id == RoleEnum.ADMIN.value).first()
        if not role:
            role = Role(id=RoleEnum.ADMIN.value, name="admin")
            session.add(role)
            session.commit()
            session.refresh(role)
        return role
    finally:
        session.close()

@pytest.fixture(scope="session")
def admin_user(engine, admin_role):
    """Create test admin user"""
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        user = session.query(User).filter(User.email == "admin@example.com").first()
        if not user:
            user = User(
                email="admin@example.com",
                username="testadmin",
                full_name="Test Admin",
                password=get_password_hash("adminpassword"),
                role_id=admin_role.id,
                is_active=True,
            )
            session.add(user)
            session.commit()
            session.refresh(user)
        return user
    finally:
        session.close()

# --- Normal User Fixtures ---

@pytest.fixture(scope="session")
def normal_user_role(engine):
    """Create test 'user' role if not exists"""
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        role = session.query(Role).filter(Role.id == RoleEnum.USER.value).first()
        if not role:
            role = Role(id=RoleEnum.USER.value, name="user")
            session.add(role)
            session.commit()
            session.refresh(role)
        return role
    finally:
        session.close()

@pytest.fixture(scope="session")
def normal_user(engine, normal_user_role):
    """Create a standard test user."""
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        user = session.query(User).filter(User.email == "test@example.com").first()
        if not user:
            user = User(
                email="test@example.com",
                username="testuser",
                full_name="Test User",
                password=get_password_hash("password"),
                role_id=normal_user_role.id,
                is_active=True,
            )
            session.add(user)
            session.commit()
            session.refresh(user)
        return user
    finally:
        session.close()

@pytest.fixture(scope="session")
def normal_inactive_user(engine, normal_user_role):
    """Create an inactive test user."""
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        user = session.query(User).filter(User.email == "inactive@example.com").first()
        if not user:
            user = User(
                email="inactive@example.com",
                username="inactiveuser",
                full_name="Inactive User",
                password=get_password_hash("password"),
                role_id=normal_user_role.id,
                is_active=False,
            )
            session.add(user)
            session.commit()
            session.refresh(user)
        return user
    finally:
        session.close()

# endregion

# region Authentication Fixtures

# --- Admin Auth ---

@pytest.fixture(scope="function")
def admin_auth_header(admin_user):
    """Create authentication headers for an admin user."""
    token = create_access_token(
        data={"sub": str(admin_user.id)},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return {"Authorization": f"Bearer {token}"}

# --- Normal User Auth ---

@pytest.fixture(scope="function")
def normal_user_auth_header(normal_user):
    """Create authentication headers for a normal user."""
    token = create_access_token(
        data={"sub": str(normal_user.id)},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return {"Authorization": f"Bearer {token}"}

# --- Other Auth States ---

@pytest.fixture(scope="function")
def expired_normal_user_token_header(normal_user):
    """Create expired authentication headers."""
    token = create_access_token(
        data={"sub": str(normal_user.id)}, expires_delta=timedelta(microseconds=1)
    )
    return {"Authorization": f"Bearer {token}"}

# endregion 