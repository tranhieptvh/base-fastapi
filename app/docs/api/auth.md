# Authentication API

## Overview
The authentication system provides secure user management with JWT-based authentication, password hashing, and role-based access control.

## Endpoints

### User Registration
- **Endpoint**: `POST /api/v1/auth/register`
- **Description**: Creates new user account
- **Features**:
  - Validates unique email and username
  - Hashes password using bcrypt
  - Returns user data without password
- **Request Body**:
  ```json
  {
      "email": "user@example.com",
      "username": "username",
      "password": "password123",
      "full_name": "Full Name"
  }
  ```
- **Response**: User data without password

### User Login
- **Endpoint**: `POST /api/v1/auth/login`
- **Description**: Authenticates user and returns JWT token
- **Features**:
  - Authenticates with email/password
  - Returns JWT access token
  - Validates user is active
  - Token expires after configured time
- **Request Body**:
  ```json
  {
      "email": "user@example.com",
      "password": "password123"
  }
  ```
- **Response**: JWT access token

### Password Management

#### Update Password
- **Endpoint**: `POST /api/v1/auth/password/update`
- **Description**: Updates user's password
- **Features**:
  - Requires current password verification
  - Updates to new password
  - Requires authentication
- **Request Body**:
  ```json
  {
      "current_password": "oldpassword",
      "new_password": "newpassword123"
  }
  ```
- **Response**: Success message

#### Password Reset Flow

##### Request Reset
- **Endpoint**: `POST /api/v1/auth/password-reset`
- **Description**: Initiates password reset process
- **Features**:
  - Sends reset token via email
  - Token valid for 24 hours
- **Request Body**:
  ```json
  {
      "email": "user@example.com"
  }
  ```
- **Response**: Success message

##### Confirm Reset
- **Endpoint**: `POST /api/v1/auth/password-reset/confirm`
- **Description**: Completes password reset process
- **Features**:
  - Validates reset token
  - Updates password
  - No authentication required
- **Request Body**:
  ```json
  {
      "token": "reset_token",
      "new_password": "newpassword123"
  }
  ```
- **Response**: Success message

### Logout
- **Endpoint**: `POST /api/v1/auth/logout`
- **Description**: Logs out user
- **Features**:
  - TODO: Implement token blacklist/revocation
- **Response**: Success message

## Security Features

### Password Security
- Bcrypt hashing
- Minimum length requirements
- Current password verification for updates

### Token Security
- JWT-based authentication
- Configurable expiration
- TODO: Token blacklist for logout

### Input Validation
- Email format validation
- Username length requirements
- Password strength requirements

## Dependencies
- `python-jose`: JWT token handling
- `passlib`: Password hashing
- `bcrypt`: Password hashing algorithm
- `pydantic`: Data validation

## Configuration
Key settings in `app/core/config.py`:
- `SECRET_KEY`: JWT signing key
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time
- `ALGORITHM`: JWT signing algorithm (HS256) 