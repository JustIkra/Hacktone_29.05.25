from pydantic import BaseModel, EmailStr
from typing import Optional
from enum import Enum

class UserRole(str, Enum):
    portal_admin = "portal_admin"
    client_admin = "client_admin"
    user = "user"

class UserBase(BaseModel):
    username: str
    email: Optional[EmailStr] = None
    role: UserRole

class UserCreate(UserBase):
    password: str
    client_id: Optional[int] = None

class UserRead(UserBase):
    id: int
    client_id: Optional[int]
    class Config:
        orm_mode = True

class ClientBase(BaseModel):
    name: str
    tariff: str

class ClientCreate(ClientBase):
    pass

class ClientRead(ClientBase):
    id: int
    class Config:
        orm_mode = True

class ServiceBase(BaseModel):
    name: str
    description: str

class ServiceCreate(ServiceBase):
    pass

class ServiceRead(ServiceBase):
    id: int
    class Config:
        orm_mode = True

class ClientServiceRead(BaseModel):
    id: int
    client_id: int
    service_id: int
    class Config:
        orm_mode = True

class UsageRead(BaseModel):
    id: int
    client_service_id: int
    user_id: int
    usage_date: str
    usage_amount: int
    class Config:
        orm_mode = True
