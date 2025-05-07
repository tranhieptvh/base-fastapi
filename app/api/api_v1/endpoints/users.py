from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.db.session import get_db
from app.schemas.user import User, UserCreate, UserUpdate
from app.services import user as user_service
from app.core.exceptions import NotFoundException, ValidationException
from app.core.response import ResponseModel, success_response

router = APIRouter()

@router.post("/", response_model=ResponseModel[User], status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    try:
        db_user = user_service.create_user(db=db, user=user)
        return success_response(data=db_user, message="User created successfully")
    except IntegrityError:
        db.rollback()
        raise ValidationException("Database constraint violation")

@router.get("/", response_model=ResponseModel[List[User]])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = user_service.get_users(db, skip=skip, limit=limit)
    return success_response(data=users)

@router.get("/{user_id}", response_model=ResponseModel[User])
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = user_service.get_user(db, user_id=user_id)
    if db_user is None:
        raise NotFoundException("User not found")
    return success_response(data=db_user)

@router.put("/{user_id}", response_model=ResponseModel[User])
def update_user(user_id: int, user: UserUpdate, db: Session = Depends(get_db)):
    db_user = user_service.update_user(db, user_id=user_id, user=user)
    if db_user is None:
        raise NotFoundException("User not found")
    return success_response(data=db_user, message="User updated successfully")

@router.delete("/{user_id}", response_model=ResponseModel)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    success = user_service.delete_user(db, user_id=user_id)
    if not success:
        raise NotFoundException("User not found")
    return success_response(message="User deleted successfully") 