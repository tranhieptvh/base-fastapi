from sqlalchemy.orm import Session
from src.db.models import User
from src.core.enums import RoleEnum
from src.core.config import settings


def test_create_user_by_admin(client, db_session: Session, admin_auth_header, normal_user_role):
    # Arrange
    user_data = {
        "email": "newuser@example.com",
        "username": "newuser",
        "full_name": "New User",
        "password": "newpassword",
        "role_id": normal_user_role.id,
    }
    
    # Act
    response = client.post(f"{settings.API_STR}/users/", headers=admin_auth_header, json=user_data)

    # Assert
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "success"
    data = data["data"]
    assert data["email"] == user_data["email"]
    assert data["username"] == user_data["username"]
    assert "id" in data
    assert "password" not in data

    user_in_db = db_session.query(User).filter(User.id == data["id"]).first()
    assert user_in_db is not None
    assert user_in_db.email == user_data["email"]


def test_create_user_by_normal_user(client, normal_user_auth_header, normal_user_role):
    # Arrange
    user_data = {
        "email": "anotheruser@example.com",
        "username": "anotheruser",
        "full_name": "Another User",
        "password": "anotherpassword",
        "role_id": normal_user_role.id,
    }

    # Act
    response = client.post(f"{settings.API_STR}/users/", headers=normal_user_auth_header, json=user_data)

    # Assert
    assert response.status_code == 401
    data = response.json()
    assert data["status"] == "error"
    assert data["message"] == "You are not authorized to create a user"


def test_create_duplicate_email_user(client, admin_auth_header, normal_user, normal_user_role):
    # Arrange
    user_data = {
        "email": normal_user.email,  # Existing email
        "username": "newusernamefordupemail",
        "full_name": "Full Name",
        "password": "password",
        "role_id": normal_user_role.id,
    }

    # Act
    response = client.post(f"{settings.API_STR}/users/", headers=admin_auth_header, json=user_data)

    # Assert
    assert response.status_code == 422
    data = response.json()
    assert data["status"] == "error"
    assert data["message"] == "email already exists"


def test_create_duplicate_username_user(client, admin_auth_header, normal_user, normal_user_role):
    # Arrange
    user_data = {
        "email": "newemailfordupusername@example.com",
        "username": normal_user.username,  # Existing username
        "full_name": "Full Name",
        "password": "password",
        "role_id": normal_user_role.id,
    }

    # Act
    response = client.post(f"{settings.API_STR}/users/", headers=admin_auth_header, json=user_data)

    # Assert
    assert response.status_code == 422
    data = response.json()
    assert data["status"] == "error"
    assert data["message"] == "username already exists"


def test_get_users_by_admin(client, admin_auth_header):
    # Arrange (no setup needed for this test besides fixtures)

    # Act
    response = client.get(f"{settings.API_STR}/users/", headers=admin_auth_header)

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["data"], list)
    # At least the admin and the initial normal_user should be present
    assert len(data["data"]) >= 2
    assert data["status"] == "success"


def test_get_users_by_normal_user(client, normal_user_auth_header):
    # Arrange (no setup needed)

    # Act
    response = client.get(f"{settings.API_STR}/users/", headers=normal_user_auth_header)

    # Assert
    assert response.status_code == 401
    data = response.json()
    assert data["status"] == "error"
    assert data["message"] == "You are not authorized to get users"


def test_get_user_by_id_by_admin(client, admin_auth_header, normal_user):
    # Arrange (no setup needed)

    # Act
    response = client.get(f"{settings.API_STR}/users/{normal_user.id}", headers=admin_auth_header)

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["data"]["id"] == normal_user.id
    assert data["data"]["email"] == normal_user.email
    assert data["data"]["username"] == normal_user.username


def test_get_user_by_id_by_normal_user_success(client, normal_user_auth_header, normal_user):
    # Arrange (no setup needed)

    # Act
    response = client.get(f"{settings.API_STR}/users/{normal_user.id}", headers=normal_user_auth_header)

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["data"]["id"] == normal_user.id
    assert data["data"]["email"] == normal_user.email
    assert data["data"]["username"] == normal_user.username
    

def test_get_user_by_id_by_normal_user_failure(client, normal_user_auth_header, normal_user, admin_user):
    # Arrange (no setup needed)

    # Act
    response = client.get(f"{settings.API_STR}/users/{admin_user.id}", headers=normal_user_auth_header)

    # Assert
    assert response.status_code == 401
    data = response.json()
    assert data["status"] == "error"
    assert data["message"] == "You are not authorized to get a user"


def test_get_nonexistent_user(client, admin_auth_header):
    # Arrange
    non_existent_id = 999999

    # Act
    response = client.get(f"{settings.API_STR}/users/{non_existent_id}", headers=admin_auth_header)

    # Assert
    assert response.status_code == 404
    data = response.json()
    assert data["status"] == "error"
    assert data["message"] == "User not found"


def test_update_user_by_admin(client, admin_auth_header, normal_user):
    # Arrange
    update_data = {"full_name": "Updated Test User Name"}

    # Act
    response = client.put(f"{settings.API_STR}/users/{normal_user.id}", headers=admin_auth_header, json=update_data)

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["message"] == "User updated successfully"
    assert data["data"]["full_name"] == update_data["full_name"]
    assert data["data"]["email"] == normal_user.email  # Email should not change


def test_update_user_by_normal_user_success(client, normal_user_auth_header, normal_user):
    # Arrange
    update_data = {"full_name": "Attempted Update"}

    # Act
    response = client.put(f"{settings.API_STR}/users/{normal_user.id}", headers=normal_user_auth_header, json=update_data)

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["message"] == "User updated successfully"
    assert data["data"]["full_name"] == update_data["full_name"]
    assert data["data"]["email"] == normal_user.email  # Email should not change
    

def test_update_user_by_normal_user_failure(client, normal_user_auth_header, normal_user, admin_user):
    # Arrange
    update_data = {"full_name": "Attempted Update"}

    # Act
    response = client.put(f"{settings.API_STR}/users/{admin_user.id}", headers=normal_user_auth_header, json=update_data)


    # Assert
    assert response.status_code == 401
    data = response.json()
    assert data["status"] == "error"
    assert data["message"] == "You are not authorized to update a user"


def test_update_nonexistent_user(client, admin_auth_header):
    # Arrange
    non_existent_id = 999999
    update_data = {"full_name": "This user does not exist"}

    # Act
    response = client.put(f"{settings.API_STR}/users/{non_existent_id}", headers=admin_auth_header, json=update_data)

    # Assert
    assert response.status_code == 404
    data = response.json()
    assert data["status"] == "error"
    assert data["message"] == "User not found"


def test_delete_user_by_admin(client, admin_auth_header, db_session: Session, normal_user_role):
    # Arrange
    user_to_delete = User(
        email="todelete@example.com",
        username="todelete",
        full_name="To Delete",
        password="password",
        role_id=normal_user_role.id,
    )
    db_session.add(user_to_delete)
    db_session.commit()
    db_session.refresh(user_to_delete)
    user_id = user_to_delete.id

    # Act
    response = client.delete(f"{settings.API_STR}/users/{user_id}", headers=admin_auth_header)

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["message"] == "User deleted successfully"
    # Verify user is deleted from DB
    deleted_user = db_session.query(User).filter(User.id == user_id).first()
    assert deleted_user is None


def test_delete_user_by_normal_user(client, normal_user_auth_header, normal_user):
    # Arrange (no setup needed)
    
    # Act
    response = client.delete(f"{settings.API_STR}/users/{normal_user.id}", headers=normal_user_auth_header)
    
    # Assert
    assert response.status_code == 401
    data = response.json()
    assert data["status"] == "error"
    assert data["message"] == "You are not authorized to delete a user"


def test_delete_nonexistent_user(client, admin_auth_header):
    # Arrange
    non_existent_id = 999999
    
    # Act
    response = client.delete(f"{settings.API_STR}/users/{non_existent_id}", headers=admin_auth_header)
    
    # Assert
    assert response.status_code == 404
    data = response.json()
    assert data["status"] == "error"
    assert data["message"] == "User not found"