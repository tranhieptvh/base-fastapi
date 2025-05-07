from typing import List, Optional
from sqlalchemy.orm import Session
from app.db.models import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password
from datetime import datetime, timedelta
from jose import jwt
from app.core.config import settings

def get_user(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()

def get_user_by_username(db: Session, username: str) -> Optional[User]:
    return db.query(User).filter(User.username == username).first()

def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    return db.query(User).offset(skip).limit(limit).all()

def create_user(db: Session, obj_in: UserCreate) -> User:
    db_obj = User(
        email=obj_in.email,
        username=obj_in.username,
        password=get_password_hash(obj_in.password),
        full_name=obj_in.full_name,
        is_active=True,
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def update_user(
    db: Session, *, db_obj: User, obj_in: UserUpdate
) -> User:
    update_data = obj_in.dict(exclude_unset=True)
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
    now = datetime.utcnow()
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