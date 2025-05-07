from typing import Optional
from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime
from app.db.session import SessionLocal
from app.db.models import User as UserModel

class UserBase(BaseModel):
    email: EmailStr
    username: str

class UserCreate(UserBase):
    password: str = Field(..., min_length=6, description="Password must be at least 6 characters long")

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
    username: Optional[str] = None
    password: Optional[str] = Field(None, min_length=6, description="Password must be at least 6 characters long")
    is_active: Optional[bool] = None

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

class User(UserInDBBase):
    pass

class UserInDB(UserInDBBase):
    hashed_password: str 