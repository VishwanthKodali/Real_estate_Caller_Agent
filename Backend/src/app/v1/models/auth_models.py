from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserRegister(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    company_name: str
    phone: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserOut(BaseModel):
    id: int
    email: str
    full_name: Optional[str]
    company_name: Optional[str]
    phone: Optional[str]
    rera_number: Optional[str]
    office_address: Optional[str]
    website: Optional[str]
    created_at: datetime
    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    company_name: Optional[str] = None
    phone: Optional[str] = None
    rera_number: Optional[str] = None
    office_address: Optional[str] = None
    website: Optional[str] = None