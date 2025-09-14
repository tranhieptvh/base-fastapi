from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.db.session import get_db
from src.dependencies import get_current_active_user
from src.db.models import User
from src.schemas.user import UserCreate, UserUpdate, UserChangePassword
from src.services import user as user_service
from src.core.exceptions import BadRequestException, NotFoundException, UnauthorizedException
from src.core.response import success_response

router = APIRouter()


@router.post("/")
async def create_user(
    *,
    db: Session = Depends(get_db),
    user_in: UserCreate,
    current_user: User = Depends(get_current_active_user),
):
    """
    Create a new user. Only accessible to admins.
    """
    if not current_user.is_admin:
        raise UnauthorizedException(
            message="You are not authorized to create a user",
        )
    db_user = await user_service.create_user(db, obj_in=user_in)
    return success_response(data=db_user, message="User created successfully")


@router.get("/me")
def get_current_user_info(
    current_user: User = Depends(get_current_active_user),
):
    """
    Get current user information.
    """
    return success_response(data=current_user, message="User information retrieved successfully")


@router.get("/")
def read_users(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
):
    """
    Retrieve users. Only accessible to admins.
    """
    if not current_user.is_admin:
        raise UnauthorizedException(
            message="You are not authorized to get users",
        )
    users = user_service.get_users(db, skip=skip, limit=limit)
    return success_response(data=users)


@router.get("/{user_id}")
def read_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get a specific user by ID. A user can get their own data, admins can get any user.
    """
    user = user_service.get_user(db, user_id=user_id)
    if not user:
        raise NotFoundException("User not found")
    if user.id != current_user.id and not current_user.is_admin:
        raise UnauthorizedException(
            message="You are not authorized to get a user",
        )
    return success_response(data=user)


@router.put("/{user_id}")
def update_user(
    *,
    db: Session = Depends(get_db),
    user_id: int,
    user_in: UserUpdate,
    current_user: User = Depends(get_current_active_user),
):
    """
    Update a user. A user can update their own data, admins can update any user.
    """
    user = user_service.get_user(db, user_id=user_id)
    if not user:
        raise NotFoundException("User not found")
    if user.id != current_user.id and not current_user.is_admin:
        raise UnauthorizedException(
            message="You are not authorized to update a user",
        )
    updated_user = user_service.update_user(db, db_obj=user, obj_in=user_in)
    return success_response(data=updated_user, message="User updated successfully")


@router.delete("/{user_id}")
def delete_user(
    user_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete a user. Only accessible to admins.
    """
    if not current_user.is_admin:
        raise UnauthorizedException(
            message="You are not authorized to delete a user"
        )
    user_to_delete = user_service.get_user(db, user_id=user_id)
    if not user_to_delete:
        raise NotFoundException("User not found")
    if user_to_delete.id == current_user.id:
        raise BadRequestException(
            message="Admins cannot delete themselves"
        )
    success = user_service.delete_user(db, user_id=user_id)
    if not success:
        raise NotFoundException("User not found")
    return success_response(message="User deleted successfully") 


@router.post("/change-password")
def change_current_user_password(
    *,
    db: Session = Depends(get_db),
    password_data: UserChangePassword,
    current_user: User = Depends(get_current_active_user),
):
    """
    Change current user's password.
    """
    user = user_service.change_password(
        db,
        user=current_user,
        current_password=password_data.old_password,
        new_password=password_data.new_password,
    )
    if not user:
        raise BadRequestException("Incorrect password")
    return success_response(message="Password updated successfully")