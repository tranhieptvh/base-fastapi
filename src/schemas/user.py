from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict
from datetime import datetime
from src.db.session import SessionLocal
from src.db.models import User as UserModel, Role
from src.core.enums import RoleEnum
from src.core.exceptions import DuplicateEntryException, ValidationException

class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: Optional[str] = None
    role_id: Optional[int] = None

    @field_validator('role_id')
    def validate_role_id(cls, v):
        if v is not None:
            db = SessionLocal()
            try:
                role = db.query(Role).filter(Role.id == v).first()
                if not role:
                    raise ValidationException(message="Role not found")
                if v not in [r.value for r in RoleEnum]:
                    raise ValidationException(message="Invalid role")
            finally:
                db.close()
        return v

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)

    @field_validator('email')
    def email_must_be_unique(cls, v):
        db = SessionLocal()
        try:
            if db.query(UserModel).filter(UserModel.email == v).first():
                raise DuplicateEntryException(field="email", value=v)
        finally:
            db.close()
        return v

    @field_validator('username')
    def username_must_be_unique(cls, v):
        db = SessionLocal()
        try:
            if db.query(UserModel).filter(UserModel.username == v).first():
                raise DuplicateEntryException(field="username", value=v)
        finally:
            db.close()
        return v

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    full_name: Optional[str] = None
    password: Optional[str] = Field(None, min_length=6)

    @field_validator('email')
    def email_must_be_unique(cls, v):
        if v is None:
            return v
        db = SessionLocal()
        try:
            if db.query(UserModel).filter(UserModel.email == v).first():
                raise DuplicateEntryException(field="email", value=v)
        finally:
            db.close()
        return v

    @field_validator('username')
    def username_must_be_unique(cls, v):
        if v is None:
            return v
        db = SessionLocal()
        try:
            if db.query(UserModel).filter(UserModel.username == v).first():
                raise DuplicateEntryException(field="username", value=v)
        finally:
            db.close()
        return v

class UserInDBBase(UserBase):
    id: int
    is_active: bool
    is_admin: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class UserResponse(UserInDBBase):
    pass

class UserSchema(UserInDBBase):
    pass

class UserInDB(UserInDBBase):
    password: str