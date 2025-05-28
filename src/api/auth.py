from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session

from src.db.session import get_db
from src.core.config import settings
from src.schemas.token import Token, TokenRefresh
from src.schemas.user import (
    UserCreate,
    UserResponse,
)
from src.schemas.auth import (
    LoginRequest,
    LogoutRequest,
)
from src.services import user as user_service
from src.core.response import SuccessResponse, ErrorResponse
from src.core.security import (
    create_access_token,
    create_and_store_refresh_token,
    revoke_refresh_token,
    verify_refresh_token,
    verify_token
)

router = APIRouter()

@router.post("/register", response_model=UserResponse)
async def register(
    user_in: UserCreate,
    db: Session = Depends(get_db)
) -> Any:
    """
    Register new user
    """
    user = user_service.get_user_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorResponse(error={"message": "The user with this email already exists in the system."})
        )
    user = await user_service.create_user(db, obj_in=user_in)
    return user

@router.post("/login", response_model=Token)
async def login(
    response: Response,
    request: LoginRequest,
    db: Session = Depends(get_db)
) -> Any:
    """
    Login with email and password using JSON
    """
    user = user_service.authenticate_user(db, request.email, request.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    
    # Create tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_and_store_refresh_token(db, user.id)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/refresh-token", response_model=Token)
async def refresh_token(
    response: Response,
    refresh_data: TokenRefresh,
    db: Session = Depends(get_db)
) -> Any:
    """
    Refresh access token using refresh token
    """
    # Verify refresh token
    db_token = verify_refresh_token(db, refresh_data.refresh_token)
    
    # Create new access token
    access_token = create_access_token(data={"sub": str(db_token.user_id)})
    
    # Set cookie
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_data.refresh_token,
        "token_type": "bearer"
    }

@router.post("/logout", response_model=SuccessResponse)
async def logout(
    request: LogoutRequest,
    db: Session = Depends(get_db)
) -> Any:
    """
    Logout user by revoking refresh token
    """
    try:
        payload = verify_token(request.refresh_token)
        user_id = payload.get("sub")
        if user_id:
            revoke_refresh_token(db, request.refresh_token)
            
        return SuccessResponse(message="Successfully logged out")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorResponse(error={"message": str(e)})
        )