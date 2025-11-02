from pydantic import BaseModel, EmailStr
from typing import Optional

# Auth schemas
class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_admin: bool

    class Config:
        from_attributes = True

# Sweet schemas
class SweetCreate(BaseModel):
    name: str
    category: str
    price: float
    quantity: int = 0

class SweetUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    price: Optional[float] = None
    quantity: Optional[int] = None

class SweetResponse(BaseModel):
    id: int
    name: str
    category: str
    price: float
    quantity: int

    class Config:
        from_attributes = True

# Inventory schemas
class PurchaseRequest(BaseModel):
    quantity: int = 1

class RestockRequest(BaseModel):
    quantity: int

