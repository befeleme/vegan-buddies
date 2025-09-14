from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreateAdmin(UserBase):
    """Schema for creating admin users - password will be auto-generated"""
    pass

class UserResponse(UserBase):
    id: int
    is_admin: bool
    password_change_required: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class PasswordChange(BaseModel):
    current_password: str
    new_password: str

class UserCreateResponse(BaseModel):
    """Response when creating a user with auto-generated password"""
    user: UserResponse
    generated_password: str
