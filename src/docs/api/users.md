# Users API

This module provides basic CRUD API endpoints for user management. Access to these endpoints requires authentication, and some operations are restricted to admins.

## Endpoints

### 1. Create User
- **URL**: `/api/users/`
- **Method**: `POST`
- **Description**: Create a new user. This endpoint is only accessible to admins.
- **Request Body**:
  ```json
  {
    "email": "newuser@example.com",
    "password": "strongpassword123",
    "full_name": "New User"
  }
  ```
- **Response**: The newly created user object, wrapped in a success response.
  ```json
  {
    "data": {
      "id": 2,
      "email": "newuser@example.com",
      "full_name": "New User",
      "is_active": true,
      "is_admin": true
    },
    "message": "User created successfully"
  }
  ```

### 2. Get All Users
- **URL**: `/api/users/`
- **Method**: `GET`
- **Description**: Get a list of all users. This endpoint is only accessible to admins.
- **Query Parameters**:
  - `skip`: Number of records to skip (default: 0).
  - `limit`: Maximum number of records to return (default: 100).
- **Response**: A list of user objects, wrapped in a success response.

### 3. Get a Specific User
- **URL**: `/api/users/{user_id}`
- **Method**: `GET`
- **Description**: Get detailed information about a specific user. A user can retrieve their own data. An admin can retrieve any user's data.
- **Path Parameters**:
  - `user_id`: The ID of the user to retrieve.
- **Response**: A single user object, wrapped in a success response.

### 4. Update User
- **URL**: `/api/users/{user_id}`
- **Method**: `PUT`
- **Description**: Update a user's information. A user can update their own data. An admin can update any user's data.
- **Path Parameters**:
  - `user_id`: The ID of the user to update.
- **Request Body** (only include fields to be updated):
  ```json
  {
    "full_name": "Updated Full Name",
    "email": "updated@example.com"
  }
  ```
- **Response**: The updated user object, wrapped in a success response.

### 5. Delete User
- **URL**: `/api/users/{user_id}`
- **Method**: `DELETE`
- **Description**: Delete a user. This endpoint is only accessible to admins.
- **Path Parameters**:
  - `user_id`: The ID of the user to delete.
- **Response**:
  ```json
  {
    "data": null,
    "message": "User deleted successfully"
  }
  ```

## Error Responses

### 400 Bad Request
- **Message**: "Admins cannot delete themselves"
- **Trigger**: An admin attempts to delete their own account.

### 401 Unauthorized
- **Message**: "You are not authorized to..."
- **Trigger**: A non-admin user tries to access an admin-only endpoint or another user's data.

### 404 Not Found
- **Message**: "User not found"
- **Trigger**: The user with the specified `user_id` does not exist. 