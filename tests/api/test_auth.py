import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from src.main import app
from src.db.models import User
from src.core.security import create_access_token, get_password_hash
from src.schemas.user import UserCreate
from src.services import user as user_service
from src.core.config import settings

client = TestClient(app)

@pytest.fixture
def test_user(db_session: Session):
    user = User(
        email="test@example.com",
        username="testuser",
        full_name="Test User",
        password=get_password_hash("password"),
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def test_user_token(test_user):
    return create_access_token(subject=test_user.id)

@pytest.fixture
def auth_headers(test_user_token):
    return {"Authorization": f"Bearer {test_user_token}"}

def test_register_success(db_session: Session):
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "Test123!@#",
        "full_name": "Test User"
    }
    response = client.post(f"{settings.API_STR}/auth/register", json=user_data)
    print(response)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["full_name"] == user_data["full_name"]
    assert "id" in data

# def test_register_duplicate_email(db_session: Session):
#     # Create first user
#     user_data = {
#         "email": "test@example.com",
#         "password": "Test123!@#",
#         "full_name": "Test User"
#     }
#     client.post(f"{settings.API_STR}/auth/register", json=user_data)
    
#     # Try to create second user with same email
#     response = client.post(f"{settings.API_STR}/auth/register", json=user_data)
#     assert response.status_code == 400
#     assert "already exists" in response.json()["error"]["message"]

# def test_login_success(db_session: Session):
#     # Create user first
#     user_data = {
#         "email": "test@example.com",
#         "password": "Test123!@#",
#         "full_name": "Test User"
#     }
#     client.post(f"{settings.API_STR}/auth/register", json=user_data)
    
#     # Login
#     login_data = {
#         "email": "test@example.com",
#         "password": "Test123!@#"
#     }
#     response = client.post(f"{settings.API_STR}/auth/login", json=login_data)
#     assert response.status_code == 200
#     data = response.json()
#     assert "access_token" in data
#     assert "refresh_token" in data
#     assert data["token_type"] == "bearer"

# def test_login_wrong_password(db_session: Session):
#     # Create user first
#     user_data = {
#         "email": "test@example.com",
#         "password": "Test123!@#",
#         "full_name": "Test User"
#     }
#     client.post(f"{settings.API_STR}/auth/register", json=user_data)
    
#     # Login with wrong password
#     login_data = {
#         "email": "test@example.com",
#         "password": "WrongPassword123"
#     }
#     response = client.post(f"{settings.API_STR}/auth/login", json=login_data)
#     assert response.status_code == 401
#     assert "Incorrect email or password" in response.text

# def test_login_inactive_user(client, db_session, test_user):
#     # Arrange
#     test_user.is_active = False
#     db_session.commit()
    
#     login_data = {
#         "email": test_user.email,
#         "password": "password"
#     }
    
#     # Act
#     response = client.post(f"{settings.API_STR}/auth/login", json=login_data)
    
#     # Assert
#     assert response.status_code == 400
#     assert "Inactive user" in response.json()["error"]["message"]

# def test_password_reset_request(client, test_user):
#     # Arrange
#     reset_data = {
#         "email": test_user.email
#     }
    
#     # Act
#     response = client.post(f"{settings.API_STR}/auth/password-reset", json=reset_data)
    
#     # Assert
#     assert response.status_code == 200
#     assert "Password reset email sent" in response.json()["message"]

# def test_password_reset_request_nonexistent_email(client):
#     # Arrange
#     reset_data = {
#         "email": "nonexistent@example.com"
#     }
    
#     # Act
#     response = client.post(f"{settings.API_STR}/auth/password-reset", json=reset_data)
    
#     # Assert
#     assert response.status_code == 200
#     assert "If the email exists" in response.json()["message"]

# def test_password_update_success(client, auth_headers):
#     # Arrange
#     update_data = {
#         "current_password": "password",
#         "new_password": "newpassword123"
#     }
    
#     # Act
#     response = client.post(f"{settings.API_STR}/auth/password/update", json=update_data, headers=auth_headers)
    
#     # Assert
#     assert response.status_code == 200
#     assert "Password updated successfully" in response.json()["message"]

# def test_password_update_wrong_current_password(client, auth_headers):
#     # Arrange
#     update_data = {
#         "current_password": "wrongpassword",
#         "new_password": "newpassword123"
#     }
    
#     # Act
#     response = client.post(f"{settings.API_STR}/auth/password/update", json=update_data, headers=auth_headers)
    
#     # Assert
#     assert response.status_code == 400
#     assert "Incorrect password" in response.json()["error"]["message"]

# def test_logout_success(db_session: Session):
#     # Create user and login first
#     user_data = {
#         "email": "test@example.com",
#         "password": "Test123!@#",
#         "full_name": "Test User"
#     }
#     client.post(f"{settings.API_STR}/auth/register", json=user_data)
    
#     login_data = {
#         "email": "test@example.com",
#         "password": "Test123!@#"
#     }
#     login_response = client.post(f"{settings.API_STR}/auth/login", json=login_data)
#     refresh_token = login_response.json()["refresh_token"]
    
#     # Logout
#     logout_data = {
#         "refresh_token": refresh_token
#     }
#     response = client.post(f"{settings.API_STR}/auth/logout", json=logout_data)
#     assert response.status_code == 200
#     assert response.json()["message"] == "Successfully logged out"

# def test_logout_invalid_token(db_session: Session):
#     logout_data = {
#         "refresh_token": "invalid_token"
#     }
#     response = client.post(f"{settings.API_STR}/auth/logout", json=logout_data)
#     assert response.status_code == 400

# def test_register_user_invalid_email(client):
#     # Arrange
#     user_data = {
#         "email": "invalid-email",
#         "username": "newuser",
#         "full_name": "New User",
#         "password": "newpassword123"
#     }
    
#     # Act
#     response = client.post(f"{settings.API_STR}/auth/register", json=user_data)
    
#     # Assert
#     assert response.status_code == 422
#     assert "email" in response.json()["detail"][0]["msg"]

# def test_register_user_short_password(client):
#     # Arrange
#     user_data = {
#         "email": "new@example.com",
#         "username": "newuser",
#         "full_name": "New User",
#         "password": "short"
#     }
    
#     # Act
#     response = client.post(f"{settings.API_STR}/auth/register", json=user_data)
    
#     # Assert
#     assert response.status_code == 422
#     assert "password" in response.json()["detail"][0]["msg"]

# def test_register_user_duplicate_username(client, db_session, test_user):
#     # Arrange
#     user_data = {
#         "email": "new@example.com",
#         "username": test_user.username,
#         "full_name": "New User",
#         "password": "newpassword123"
#     }
    
#     # Act
#     response = client.post(f"{settings.API_STR}/auth/register", json=user_data)
    
#     # Assert
#     assert response.status_code == 400
#     assert "already exists" in response.json()["error"]["message"]

# def test_login_invalid_token(client):
#     # Arrange
#     headers = {"Authorization": "Bearer invalid_token"}
    
#     # Act
#     response = client.get(f"{settings.API_STR}/users/me", headers=headers)
    
#     # Assert
#     assert response.status_code == 401
#     assert "Invalid authentication credentials" in response.json()["detail"]

# def test_login_expired_token(client, db_session, test_user):
#     # Arrange
#     expired_token = create_access_token(subject=test_user.id, expires_delta=timedelta(microseconds=1))
#     headers = {"Authorization": f"Bearer {expired_token}"}
    
#     # Act
#     response = client.get(f"{settings.API_STR}/users/me", headers=headers)
    
#     # Assert
#     assert response.status_code == 401
#     assert "Token has expired" in response.json()["detail"]

# def test_password_update_weak_password(client, auth_headers):
#     # Arrange
#     update_data = {
#         "current_password": "password",
#         "new_password": "weak"
#     }
    
#     # Act
#     response = client.post(f"{settings.API_STR}/auth/password/update", json=update_data, headers=auth_headers)
    
#     # Assert
#     assert response.status_code == 422
#     assert "password" in response.json()["detail"][0]["msg"]

# def test_login_rate_limit(client, test_user):
#     # Arrange
#     login_data = {
#         "email": test_user.email,
#         "password": "wrongpassword"
#     }
    
#     # Act - Try multiple login attempts
#     for _ in range(5):
#         response = client.post(f"{settings.API_STR}/auth/login", json=login_data)
    
#     # Assert
#     assert response.status_code == 429
#     assert "Too many requests" in response.json()["detail"]

# def test_refresh_token_success(db_session: Session):
#     # Create user and login first
#     user_data = {
#         "email": "test@example.com",
#         "password": "Test123!@#",
#         "full_name": "Test User"
#     }
#     client.post(f"{settings.API_STR}/auth/register", json=user_data)
    
#     login_data = {
#         "email": "test@example.com",
#         "password": "Test123!@#"
#     }
#     login_response = client.post(f"{settings.API_STR}/auth/login", json=login_data)
#     refresh_token = login_response.json()["refresh_token"]
    
#     # Refresh token
#     refresh_data = {
#         "refresh_token": refresh_token
#     }
#     response = client.post(f"{settings.API_STR}/auth/refresh-token", json=refresh_data)
#     assert response.status_code == 200
#     data = response.json()
#     assert "access_token" in data
#     assert "refresh_token" in data
#     assert data["token_type"] == "bearer"

# def test_refresh_token_invalid(db_session: Session):
#     refresh_data = {
#         "refresh_token": "invalid_token"
#     }
#     response = client.post(f"{settings.API_STR}/auth/refresh-token", json=refresh_data)
#     assert response.status_code == 400 