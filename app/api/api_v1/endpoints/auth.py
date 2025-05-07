from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_current_user
from app.core import security
from app.core.config import settings
from app.db.models import User
from app.schemas.token import Token
from app.schemas.user import User as UserSchema
from app.schemas.user import (
    UserCreate,
    UserResponse,
    PasswordReset,
    PasswordUpdate,
    PasswordResetConfirm,
)
from app.services import user as user_service
from app.core.response import ResponseModel, success_response

router = APIRouter()

@router.post("/register", response_model=ResponseModel[UserSchema])
def register_user(
    *,
    db: Session = Depends(get_db),
    user_in: UserCreate,
) -> Any:
    """
    Register new user.
    """
    user = user_service.get_user_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user with this email already exists in the system.",
        )
    user = user_service.create_user(db, obj_in=user_in)
    return success_response(data=user, message="User registered successfully")

@router.post("/login", response_model=Token)
def login(
    *,
    db: Session = Depends(get_db),
    email: str = Body(...),
    password: str = Body(...),
) -> Any:
    """
    Login with email and password to get access token
    """
    user = user_service.authenticate_user(
        db, email=email, password=password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    elif not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )
        
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        subject=user.id, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "full_name": user.full_name,
            "is_active": user.is_active
        }
    }

@router.post("/password-reset", response_model=ResponseModel)
def request_password_reset(
    *,
    db: Session = Depends(get_db),
    email: str = Body(...),
) -> Any:
    """
    Request password reset.
    """
    user = user_service.get_user_by_email(db, email=email)
    if user:
        token = user_service.create_password_reset_token(email)
        # TODO: Send email with token
        return success_response(message="Password reset email sent")
    return success_response(message="If the email exists, a password reset email has been sent")

@router.post("/password-reset/confirm", response_model=ResponseModel)
def reset_password(
    *,
    db: Session = Depends(get_db),
    token: str = Body(...),
    new_password: str = Body(...),
) -> Any:
    """
    Reset password.
    """
    email = user_service.verify_password_reset_token(token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid token")
    user = user_service.get_user_by_email(db, email=email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user_service.update_password(db, user=user, new_password=new_password)
    return success_response(message="Password updated successfully")

@router.post("/password/update", response_model=ResponseModel)
def update_password(
    *,
    db: Session = Depends(get_db),
    current_password: str = Body(...),
    new_password: str = Body(...),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Update password.
    """
    if not user_service.verify_password(current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect password")
    user_service.update_password(db, user=current_user, new_password=new_password)
    return success_response(message="Password updated successfully")

@router.post("/logout", response_model=ResponseModel)
def logout(
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Logout user.
    """
    # TODO: Implement token blacklist
    print(f"Logout user: {current_user}")
    return success_response(message="Successfully logged out") 