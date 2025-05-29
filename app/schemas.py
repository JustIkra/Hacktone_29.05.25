# app/schemas.py

from pydantic import BaseModel, EmailStr
from typing import Optional
from enum import Enum
import datetime

# Повторяем enum ролей из models.py
class UserRole(str, Enum):
    portal_admin = "portal_admin"
    client_admin = "client_admin"
    user = "user"

# ---------------------
# Client
# ---------------------
class ClientBase(BaseModel):
    name: str
    tariff: str

class ClientCreate(ClientBase):
    ...

class ClientRead(ClientBase):
    id: int
    created_at: datetime.datetime

    class Config:
        orm_mode = True

# ---------------------
# User
# ---------------------
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

# ---------------------
# Service
# ---------------------
class ServiceBase(BaseModel):
    name: str
    description: Optional[str] = None

class ServiceCreate(ServiceBase):
    ...

class ServiceRead(ServiceBase):
    id: int

    class Config:
        orm_mode = True

# ---------------------
# ClientService (подключённый сервис клиента)
# ---------------------
class ClientServiceBase(BaseModel):
    client_id: int
    service_id: int
    expires_at: Optional[datetime.datetime] = None

class ClientServiceCreate(ClientServiceBase):
    ...

class ClientServiceRead(ClientServiceBase):
    id: int
    connected_at: datetime.datetime

    class Config:
        orm_mode = True

# ---------------------
# Usage (отчётность)
# ---------------------
class UsageBase(BaseModel):
    client_service_id: int
    user_id: int
    usage_amount: int

class UsageCreate(UsageBase):
    ...

class UsageRead(UsageBase):
    id: int
    usage_date: datetime.datetime

    class Config:
        orm_mode = True

# ---------------------
# Auth (JWT)
# ---------------------
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[UserRole] = None

# ---------------------
# Tariff
# ---------------------
class TariffBase(BaseModel):
    name: str
    max_users: int
    max_services: int
    period_days: int
    price: float

class TariffCreate(TariffBase):
    ...

class TariffRead(TariffBase):
    id: int

    class Config:
        orm_mode = True

# ---------------------
# UserService (назначение пользователю сервиса)
# ---------------------
class UserServiceBase(BaseModel):
    user_id: int
    client_service_id: int

class UserServiceCreate(UserServiceBase):
    ...

class UserServiceRead(UserServiceBase):
    id: int

    class Config:
        orm_mode = True
