# Users API

This module provides API endpoints for user management in the system.

## Endpoints

### 1. Create User
- **URL**: `/api/v1/users/`
- **Method**: `POST`
- **Description**: Create a new user
- **Request Body**:
  ```json
  {
    "email": "user@example.com",
    "username": "username",
    "password": "password123"
  }
  ```
- **Validation Rules**:
  - Email must be a valid email address
  - Email must be unique
  - Username must be unique
  - Password must be at least 6 characters long
- **Response**: 
  ```json
  {
    "id": 1,
    "email": "user@example.com",
    "username": "username",
    "is_active": true,
    "created_at": "2024-03-20T10:00:00",
    "updated_at": "2024-03-20T10:00:00"
  }
  ```

### 2. Get Users
- **URL**: `/api/v1/users/`
- **Method**: `GET`
- **Description**: Get a list of users
- **Query Parameters**:
  - `skip`: Number of records to skip (default: 0)
  - `limit`: Maximum number of records to return (default: 100)
- **Response**:
  ```json
  [
    {
      "id": 1,
      "email": "user@example.com",
      "username": "username",
      "is_active": true,
      "created_at": "2024-03-20T10:00:00",
      "updated_at": "2024-03-20T10:00:00"
    }
  ]
  ```

### 3. Get User
- **URL**: `/api/v1/users/{user_id}`
- **Method**: `GET`
- **Description**: Get detailed information about a specific user
- **Path Parameters**:
  - `user_id`: ID of the user
- **Response**:
  ```json
  {
    "id": 1,
    "email": "user@example.com",
    "username": "username",
    "is_active": true,
    "created_at": "2024-03-20T10:00:00",
    "updated_at": "2024-03-20T10:00:00"
  }
  ```

### 4. Update User
- **URL**: `/api/v1/users/{user_id}`
- **Method**: `PUT`
- **Description**: Update user information
- **Path Parameters**:
  - `user_id`: ID of the user
- **Request Body**:
  ```json
  {
    "email": "newemail@example.com",
    "username": "newusername",
    "password": "newpassword123",
    "is_active": true
  }
  ```
- **Validation Rules**:
  - Email must be a valid email address
  - Email must be unique (if changed)
  - Username must be unique (if changed)
  - Password must be at least 6 characters long (if changed)
- **Response**:
  ```json
  {
    "id": 1,
    "email": "newemail@example.com",
    "username": "newusername",
    "is_active": true,
    "created_at": "2024-03-20T10:00:00",
    "updated_at": "2024-03-20T10:00:00"
  }
  ```

### 5. Delete User
- **URL**: `/api/v1/users/{user_id}`
- **Method**: `DELETE`
- **Description**: Delete a user
- **Path Parameters**:
  - `user_id`: ID of the user
- **Response**: `true` if deletion is successful

## Error Responses

### Validation Error
```json
{
  "status": "error",
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Validation error",
    "details": [
      {
        "field": "email",
        "message": "Email already registered"
      }
    ]
  }
}
```

### Not Found Error
```json
{
  "status": "error",
  "error": {
    "code": "NOT_FOUND",
    "message": "User not found"
  }
}
``` 