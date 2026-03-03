from pydantic import BaseModel, field_validator, Field
from typing import Optional
import re

class UserLogin(BaseModel):
    username: str
    password: str

class UserRegistration(BaseModel):
    full_name: str = Field(min_length=3, max_length=100, description="Full name")
    company_name: str = Field(min_length=3, max_length=150, description="Company name")
    username: str = Field(min_length=3, max_length=50, description="Unique username")
    password: str = Field(min_length=8, description="Password (min 8 chars, must have uppercase, lowercase, digit)")
    contact_number: str = Field(min_length=10, max_length=20, description="Phone number")
    email: str = Field(description="Email address")
    office_address: str = Field(min_length=5, max_length=255, description="Office address")
    website: Optional[str] = Field(None, max_length=255, description="Company website")
    rera_number: Optional[str] = Field(None, max_length=50, description="RERA registration number")

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenRefresh(BaseModel):
    refresh_token: str

class LogoutRequest(BaseModel):
    """Optional refresh_token to revoke alongside access token."""
    refresh_token: Optional[str] = Field(None, description="Optional refresh token to revoke")
