# Authentication API

## Overview
The authentication system provides secure user management using JWT-based authentication. It handles user registration, login via email and password, token refreshing, and logout.

## Endpoints

### User Registration
- **Endpoint**: `POST /api/auth/register`
- **Description**: Creates a new user account.
- **Request Body**:
  ```json
  {
      "email": "user@example.com",
      "password": "password123",
      "full_name": "Full Name"
  }
  ```
- **Response**: User data (without the password) upon successful registration.

### User Login
- **Endpoint**: `POST /api/auth/login`
- **Description**: Authenticates a user and returns access and refresh tokens.
- **Request Body**:
  ```json
  {
      "email": "user@example.com",
      "password": "password123"
  }
  ```
- **Response**:
  ```json
  {
      "access_token": "string",
      "refresh_token": "string",
      "token_type": "bearer"
  }
  ```

### Refresh Access Token
- **Endpoint**: `POST /api/auth/refresh-token`
- **Description**: Issues a new access token using a valid refresh token.
- **Request Body**:
  ```json
  {
      "refresh_token": "your_refresh_token"
  }
  ```
- **Response**: Returns a new `access_token` and the original `refresh_token`. The new access token is also set as an `httponly` cookie.

### Logout
- **Endpoint**: `POST /api/auth/logout`
- **Description**: Logs out the user by revoking their refresh token. The request requires a valid refresh token to identify and revoke the correct token.
- **Request Body**:
  ```json
  {
    "refresh_token": "your_refresh_token"
  }
  ```
- **Response**: A success message upon successful logout.

## Security Features

### Password Security
- Passwords are securely hashed using `bcrypt` before being stored.
- The hashing is handled by `passlib`.

### Token Security
- **JWT**: The system uses JSON Web Tokens (JWT) for creating secure access tokens.
- **Access Token**: Short-lived token used to authenticate API requests.
- **Refresh Token**: Long-lived token stored in the database, used to obtain a new access token without requiring the user to log in again. It is revoked upon logout.
- **Token Handling**: The `python-jose` library is used for JWT operations.

## Dependencies
- `fastapi`: Web framework.
- `sqlalchemy`: Database ORM.
- `python-jose`: For JWT creation and validation.
- `passlib[bcrypt]`: For password hashing.
- `pydantic`: For data validation in request and response models.

## Configuration
Key settings are managed in `src/core/config.py` via environment variables:
- `SECRET_KEY`: The secret key for signing JWTs.
- `ACCESS_TOKEN_EXPIRE_MINUTES`: The lifetime of an access token.
- `ALGORITHM`: The algorithm used for JWT signing (e.g., HS256). 