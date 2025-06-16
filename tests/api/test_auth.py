from sqlalchemy.orm import Session
from unittest.mock import patch

from src.db.models import User
from src.core.config import settings
from src.services.user import create_password_reset_token

def test_register_success(client, db_session: Session, normal_user_role):
    # Arrange
    print(f"Test role in test: {normal_user_role.id} - {normal_user_role.name}")  # Debug print
    input_data = {
        "email": "newuser@example.com",
        "username": "newuser",
        "full_name": "New User",
        "password": "Test123!@#",
        "role_id": normal_user_role.id
    }
    print(f"Input data: {input_data}")  # Debug print
    
    # Act
    response = client.post(f"{settings.API_STR}/auth/register", json=input_data)
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    
    user_data = data["data"]
    assert user_data["email"] == input_data["email"]
    assert user_data["username"] == input_data["username"]
    assert user_data["full_name"] == input_data["full_name"]
    assert "id" in user_data
    assert "created_at" in user_data
    assert "updated_at" in user_data
    assert "is_active" in user_data
    assert "role_id" in user_data
    assert "password" not in user_data

    # Verify user was created in database
    db_user = db_session.query(User).filter(User.email == input_data["email"]).first()
    assert db_user is not None
    assert db_user.email == input_data["email"]
    assert db_user.username == input_data["username"]
    assert db_user.full_name == input_data["full_name"]
    assert db_user.is_active is True
    assert db_user.role_id == input_data["role_id"]

def test_register_duplicate_email(client, db_session: Session, normal_user):
    # Try to create user with existing email
    input_data = {
        "email": normal_user.email,
        "username": "newuser",  # Different username to avoid multiple errors
        "password": "Test123!@#",
        "full_name": "New User",
        "role_id": normal_user.role_id
    }
    
    # Act
    response = client.post(f"{settings.API_STR}/auth/register", json=input_data)
    
    # Assert
    assert response.status_code == 422  # Unprocessable Entity for validation error
    data = response.json()
    
    # Check error response format
    assert data["status"] == "error"
    assert data["message"] == "email already exists"
    assert "fields" in data["errors"]
    
    email_error = data["errors"]["fields"][0]
    assert email_error["field"] == "email"
    assert email_error["type"] == "duplicate_entry"
    
    # Verify no new user was created
    db_users = db_session.query(User).filter(User.email == input_data["email"]).all()
    assert len(db_users) == 1  # Only the original normal_user should exist
    
def test_register_user_duplicate_username(client, db_session: Session, normal_user):
    # Arrange
    input_data = {
        "email": "new@example.com",
        "username": normal_user.username,
        "full_name": "New User",
        "password": "newpassword123",
        "role_id": normal_user.role_id
    }
    
    # Act
    response = client.post(f"{settings.API_STR}/auth/register", json=input_data)
    
    # Assert
    assert response.status_code == 422  # Unprocessable Entity for validation error
    data = response.json()
    
    # Check error response format
    assert data["status"] == "error"
    assert data["message"] == "username already exists"
    assert "fields" in data["errors"]
    
    username_error = data["errors"]["fields"][0]
    assert username_error["field"] == "username"
    assert username_error["type"] == "duplicate_entry"
    
    # Verify no new user was created
    db_users = db_session.query(User).filter(User.username == input_data["username"]).all()
    assert len(db_users) == 1  # Only the original normal_user should exist
    
def test_register_user_invalid_email(client, normal_user_role):
    # Arrange
    input_data = {
        "email": "invalid-email",
        "username": "newuser",
        "full_name": "New User",
        "password": "newpassword123",
        "role_id": normal_user_role.id
    }
    
    # Act
    response = client.post(f"{settings.API_STR}/auth/register", json=input_data)
    
    # Assert
    assert response.status_code == 422
    data = response.json()
    assert data["status"] == "error"
    assert data["message"] == "Validation error"
    assert "fields" in data["errors"]
    
    email_error = data["errors"]["fields"][0]
    assert email_error["field"] == "email"
    assert email_error["type"] == "value_error"

def test_register_user_short_password(client, normal_user_role):
    # Arrange
    input_data = {
        "email": "new@example.com",
        "username": "newuser",
        "full_name": "New User",
        "password": "short",
        "role_id": normal_user_role.id
    }
    
    # Act
    response = client.post(f"{settings.API_STR}/auth/register", json=input_data)
    
    # Assert
    assert response.status_code == 422
    data = response.json()
    assert data["status"] == "error"
    assert data["message"] == "Validation error"
    assert "fields" in data["errors"]
    
    password_error = data["errors"]["fields"][0]
    assert password_error["field"] == "password"
    assert password_error["type"] == "string_too_short"

def test_login_success(client, normal_user):
    # Login with test user
    login_data = {
        "email": normal_user.email,
        "password": "password"
    }
    response = client.post(f"{settings.API_STR}/auth/login", json=login_data)
    assert response.status_code == 200
    data = response.json()['data']
    
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

def test_login_wrong_password(client, normal_user):
    # Login with wrong password
    login_data = {
        "email": normal_user.email,
        "password": "wrongpassword"
    }
    response = client.post(f"{settings.API_STR}/auth/login", json=login_data)
    assert response.status_code == 401
    data = response.json()
    assert data["status"] == "error"
    assert data["message"] == "Incorrect email or password"
    assert data["errors"]["type"] == "unauthorized"

def test_login_inactive_user(client, normal_inactive_user):
    # Arrange
    login_data = {
        "email": normal_inactive_user.email,
        "password": "password"
    }
    
    # Act
    response = client.post(f"{settings.API_STR}/auth/login", json=login_data)
    
    # Assert
    assert response.status_code == 401
    data = response.json()
    assert data["status"] == "error"
    assert data["message"] == "Inactive user"
    assert data["errors"]["type"] == "unauthorized"

def test_logout_success(client, normal_user):
    # Login with test user
    login_data = {
        "email": normal_user.email,
        "password": "password"
    }
    login_response = client.post(f"{settings.API_STR}/auth/login", json=login_data)
    print(f"Login response: {login_response.json()}")
    refresh_token = login_response.json()["data"]["refresh_token"]
    
    # Logout
    logout_data = {
        "refresh_token": refresh_token
    }
    response = client.post(f"{settings.API_STR}/auth/logout", json=logout_data)
    print(f"Logout response: {response.json()}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["message"] == "Successfully logged out"

def test_logout_invalid_token(client):
    logout_data = {
        "refresh_token": "invalid_token"
    }
    response = client.post(f"{settings.API_STR}/auth/logout", json=logout_data)
    assert response.status_code == 401
    data = response.json()
    assert data["status"] == "error"
    assert data["message"] == "Invalid token"
    assert data["errors"]["type"] == "unauthorized"

@patch("src.api.auth.user_service.request_password_reset")
def test_forgot_password_success(mock_request_password_reset, client, normal_user):
    # Arrange
    mock_request_password_reset.return_value = True
    forgot_password_data = {"email": normal_user.email}
    
    # Act
    response = client.post(f"{settings.API_STR}/auth/forgot-password", json=forgot_password_data)
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["message"] == "Password reset email sent"
    mock_request_password_reset.assert_called_once()

def test_reset_password_success(client, normal_user):
    # Arrange
    token = create_password_reset_token(email=normal_user.email)
    new_password = "new_strong_password"
    reset_data = {"token": token, "new_password": new_password}
    
    # Act
    response = client.post(f"{settings.API_STR}/auth/reset-password", json=reset_data)
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["message"] == "Password has been reset successfully"

    # Verify new password
    login_data = {"email": normal_user.email, "password": new_password}
    login_response = client.post(f"{settings.API_STR}/auth/login", json=login_data)
    assert login_response.status_code == 200

def test_reset_password_invalid_token(client):
    # Arrange
    reset_data = {"token": "invalid-token", "new_password": "some_password"}
    
    # Act
    response = client.post(f"{settings.API_STR}/auth/reset-password", json=reset_data)
    
    # Assert
    assert response.status_code == 400
    data = response.json()
    assert data["status"] == "error"
    assert data["message"] == "Invalid token or user does not exist"