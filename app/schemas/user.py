from typing import Optional
from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime
from app.dependencies.db import SessionLocal
from app.db.models import User as UserModel, Role
from app.core.enums import RoleEnum

class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: Optional[str] = None
    role_id: Optional[int] = None

    @validator('role_id')
    def validate_role_id(cls, v):
        if v is not None:
            db = SessionLocal()
            try:
                role = db.query(Role).filter(Role.id == v).first()
                if not role:
                    raise ValueError('Role not found')
                if v not in [r.value for r in RoleEnum]:
                    raise ValueError('Invalid role')
            finally:
                db.close()
        return v

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)

    @validator('email')
    def email_must_be_unique(cls, v):
        db = SessionLocal()
        try:
            if db.query(UserModel).filter(UserModel.email == v).first():
                raise ValueError('Email already registered')
        finally:
            db.close()
        return v

    @validator('username')
    def username_must_be_unique(cls, v):
        db = SessionLocal()
        try:
            if db.query(UserModel).filter(UserModel.username == v).first():
                raise ValueError('Username already registered')
        finally:
            db.close()
        return v

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    full_name: Optional[str] = None
    password: Optional[str] = Field(None, min_length=6)

    @validator('email')
    def email_must_be_unique(cls, v):
        if v is None:
            return v
        db = SessionLocal()
        try:
            if db.query(UserModel).filter(UserModel.email == v).first():
                raise ValueError('Email already registered')
        finally:
            db.close()
        return v

    @validator('username')
    def username_must_be_unique(cls, v):
        if v is None:
            return v
        db = SessionLocal()
        try:
            if db.query(UserModel).filter(UserModel.username == v).first():
                raise ValueError('Username already registered')
        finally:
            db.close()
        return v

class UserInDBBase(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class UserResponse(UserInDBBase):
    pass

class User(UserInDBBase):
    pass

class UserInDB(UserInDBBase):
    password: str

class PasswordReset(BaseModel):
    email: EmailStr

class PasswordUpdate(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=6)

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str = Field(..., min_length=6) 