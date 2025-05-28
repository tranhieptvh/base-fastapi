from datetime import datetime, timedelta
from typing import Any, Union, Optional

import bcrypt
from jose import jwt, JWTError
from fastapi import HTTPException, Request, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from src.core.config import settings
from src.db.models.user import User
from src.db.models.token import RefreshToken

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a new access token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def create_and_store_refresh_token(db: Session, user_id: int) -> str:
    """
    Create a new refresh token and store it in the database
    """
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = {
        "sub": str(user_id),
        "exp": expire,
        "type": "refresh"
    }
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
    # Store the refresh token in the database
    db_token = RefreshToken(
        user_id=user_id,
        token=encoded_jwt,
        expires_at=expire
    )
    db.add(db_token)
    db.commit()
    
    return encoded_jwt

def revoke_refresh_token(db: Session, refresh_token: str):
    """
    Revoke a refresh token
    """
    db.query(RefreshToken).filter(
        RefreshToken.token == refresh_token,
        RefreshToken.is_revoked == False
    ).update({
        RefreshToken.is_revoked: True
    })
    db.commit()

def verify_token(token: str) -> dict:
    """
    Verify a token and return its payload
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_token_from_request(request: Request) -> Optional[str]:
    """
    Get token from request header or cookie
    """
    # Try to get token from Authorization header
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header.split(" ")[1]
    
    # Try to get token from cookie
    return request.cookies.get("access_token")

def get_current_user(
    db: Session,
    token: str = Depends(oauth2_scheme)
) -> User:
    """
    Get current user from token
    """
    try:
        payload = verify_token(token)
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def verify_refresh_token(
    db: Session,
    token: str
) -> RefreshToken:
    """
    Verify refresh token and return the token object
    """
    try:
        payload = verify_token(token)
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")
        
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Check if token exists and is not revoked
        db_token = db.query(RefreshToken).filter(
            RefreshToken.token == token,
            RefreshToken.user_id == user_id,
            RefreshToken.is_revoked == False,
            RefreshToken.expires_at > datetime.utcnow()
        ).first()
        
        if not db_token:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        
        return db_token
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode('utf-8'),
        hashed_password.encode('utf-8')
    )

def get_password_hash(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8') 