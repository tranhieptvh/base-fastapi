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
from app.core.response import SuccessResponse, ErrorResponse

router = APIRouter()

@router.post("/register", response_model=SuccessResponse[UserSchema])
async def register_user(
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
            detail=ErrorResponse(error={"message": "The user with this email already exists in the system."}).dict()
        )
    user = await user_service.create_user(db, obj_in=user_in)
    return SuccessResponse(data=user, message="User registered successfully")

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
            detail=ErrorResponse(error={"message": "Incorrect email or password"}).dict(),
            headers={"WWW-Authenticate": "Bearer"},
        )
    elif not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorResponse(error={"message": "Inactive user"}).dict()
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
            "is_active": user.is_active,
            "role": {
                "id": user.role.id,
                "name": user.role.name
            } if user.role else None
        }
    }

@router.post("/password-reset", response_model=SuccessResponse)
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
        return SuccessResponse(message="Password reset email sent")
    return SuccessResponse(message="If the email exists, a password reset email has been sent")

@router.post("/password-reset/confirm", response_model=SuccessResponse)
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
        raise HTTPException(
            status_code=400,
            detail=ErrorResponse(error={"message": "Invalid token"}).dict()
        )
    user = user_service.get_user_by_email(db, email=email)
    if not user:
        raise HTTPException(
            status_code=404,
            detail=ErrorResponse(error={"message": "User not found"}).dict()
        )
    user_service.update_password(db, user=user, new_password=new_password)
    return SuccessResponse(message="Password updated successfully")

@router.post("/password/update", response_model=SuccessResponse)
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
        raise HTTPException(
            status_code=400,
            detail=ErrorResponse(error={"message": "Incorrect password"}).dict()
        )
    user_service.update_password(db, user=current_user, new_password=new_password)
    return SuccessResponse(message="Password updated successfully")

@router.post("/logout", response_model=SuccessResponse)
def logout(
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Logout user.
    """
    # TODO: Implement token blacklist
    print(f"Logout user: {current_user}")
    return SuccessResponse(message="Successfully logged out") 