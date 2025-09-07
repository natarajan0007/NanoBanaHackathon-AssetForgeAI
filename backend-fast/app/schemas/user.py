from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
import uuid
from .organization import OrganizationSchema


class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserBase):
    password: str
    role: Optional[str] = "user"
    organizationName: Optional[str] = None


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    preferences: Optional[dict] = None


class User(UserBase):
    id: uuid.UUID
    role: str
    is_active: bool
    preferences: dict
    created_at: datetime
    updated_at: datetime
    organization: OrganizationSchema

    class Config:
        from_attributes = True
