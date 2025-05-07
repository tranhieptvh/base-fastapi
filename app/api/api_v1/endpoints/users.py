from typing import Any, List
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.dependencies import get_db, get_current_user, get_current_active_user
from app.db.models import User
from app.schemas.user import User as UserSchema, UserCreate, UserUpdate
from app.services import user as user_service
from app.core.exceptions import NotFoundException, ValidationException
from app.core.response import ResponseModel, success_response

router = APIRouter()

@router.post("/", response_model=ResponseModel[UserSchema], status_code=status.HTTP_201_CREATED)
def create_user(
    *,
    db: Session = Depends(get_db),
    user_in: UserCreate,
    current_user: User = Depends(get_current_user),
):
    """
    Create new user.
    """
    user = user_service.get_user_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
    db_user = user_service.create_user(db, obj_in=user_in)
    return success_response(data=db_user, message="User created successfully")

@router.get("/", response_model=ResponseModel[List[UserSchema]])
def read_users(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve users.
    """
    users = user_service.get_users(db, skip=skip, limit=limit)
    return success_response(data=users)

@router.get("/me", response_model=ResponseModel[UserSchema])
def read_user_me(
    current_user: User = Depends(get_current_user),
):
    """
    Get current user.
    """
    return success_response(data=current_user)

@router.get("/{user_id}", response_model=ResponseModel[UserSchema])
def read_user_by_id(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get a specific user by id.
    """
    user = user_service.get_user(db, user_id=user_id)
    if user == current_user:
        return success_response(data=user)
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    return success_response(data=user)

@router.put("/{user_id}", response_model=ResponseModel[UserSchema])
def update_user(
    *,
    db: Session = Depends(get_db),
    user_id: int,
    user_in: UserUpdate,
    current_user: User = Depends(get_current_user),
):
    """
    Update a user.
    """
    user = user_service.get_user(db, user_id=user_id)
    if not user:
        raise NotFoundException("User not found")
    db_user = user_service.update_user(db, db_obj=user, obj_in=user_in)
    return success_response(data=db_user, message="User updated successfully")

@router.delete("/{user_id}", response_model=ResponseModel)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    success = user_service.delete_user(db, user_id=user_id)
    if not success:
        raise NotFoundException("User not found")
    return success_response(message="User deleted successfully")

@router.put("/me", response_model=ResponseModel[UserSchema])
def update_user_me(
    *,
    db: Session = Depends(get_db),
    user_in: UserUpdate,
    current_user: User = Depends(get_current_user),
):
    """
    Update own user.
    """
    user = user_service.update_user(db, db_obj=current_user, obj_in=user_in)
    return success_response(data=user, message="User updated successfully") 