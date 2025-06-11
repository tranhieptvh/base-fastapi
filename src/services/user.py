from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from src.db.models import User, Role
from src.schemas.user import UserCreate, UserUpdate
from src.core.security import get_password_hash, verify_password
from datetime import datetime, timedelta, timezone
from jose import jwt
from src.core.config import settings
from src.core.enums import RoleEnum
from src.services.email import send_welcome_email
from src.core.exceptions import DuplicateEntryException, ValidationException

def get_user(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()

def get_user_by_username(db: Session, username: str) -> Optional[User]:
    return db.query(User).filter(User.username == username).first()

def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    return db.query(User).offset(skip).limit(limit).all()

def get_default_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    return db.query(User).filter(
        User.role_id == RoleEnum.USER.value,
        User.is_active == True
    ).offset(skip).limit(limit).all()

async def create_user(db: Session, obj_in: UserCreate) -> User:
    # Get default user role if role_id is not provided
    if obj_in.role_id is None:
        user_role = Role.get_default_role(db)
        if not user_role:
            raise ValidationException(message="Default user role not found")
        role_id = user_role.id
    else:
        role_id = obj_in.role_id

    try:
        db_obj = User(
            email=obj_in.email,
            username=obj_in.username,
            password=get_password_hash(obj_in.password),
            full_name=obj_in.full_name,
            role_id=role_id,
            is_active=True,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

        # Send welcome email
        # await send_welcome_email(email_to=db_obj.email, username=db_obj.username)
        
        return db_obj
    except SQLAlchemyError as e:
        db.rollback()
        raise ValidationException(message="Database error occurred")
    except Exception as e:
        db.rollback()
        raise ValidationException(message=str(e))

def update_user(
    db: Session, *, db_obj: User, obj_in: UserUpdate
) -> User:
    update_data = obj_in.model_dump(exclude_unset=True)
    if "password" in update_data:
        update_data["password"] = get_password_hash(update_data["password"])
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def delete_user(db: Session, user_id: int) -> bool:
    db_user = get_user(db, user_id)
    if not db_user:
        return False
    
    db.delete(db_user)
    db.commit()
    return True

def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    user = get_user_by_email(db, email=email)
    if not user:
        return None
    if not verify_password(password, user.password):
        return None
    return user

def update_password(
    db: Session, *, user: User, current_password: str, new_password: str
) -> bool:
    if not verify_password(current_password, user.password):
        return False
    user.password = get_password_hash(new_password)
    db.add(user)
    db.commit()
    return True

def create_password_reset_token(email: str) -> str:
    """Create a password reset token for the given email."""
    delta = timedelta(hours=settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS)
    now = datetime.now(timezone.utc)
    expires = now + delta
    exp = expires.timestamp()
    encoded_jwt = jwt.encode(
        {"exp": exp, "nbf": now, "sub": email},
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )
    return encoded_jwt

def verify_password_reset_token(token: str) -> Optional[str]:
    """Verify the password reset token and return the email if valid."""
    try:
        decoded_token = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        return decoded_token["sub"]
    except jwt.JWTError:
        return None 