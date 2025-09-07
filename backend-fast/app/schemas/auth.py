from pydantic import BaseModel, EmailStr
from typing import Optional


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    accessToken: str
    refreshToken: str
    tokenType: str = "bearer"


class RefreshTokenRequest(BaseModel):
    refreshToken: str

class RefreshTokenResponse(BaseModel):
    accessToken: str
    tokenType: str = "bearer"


class UserPreferencesUpdate(BaseModel):
    theme: Optional[str] = None


class PasswordResetRequest(BaseModel):
    email: EmailStr


class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    role: str
    preferences: dict

    class Config:
        from_attributes = True