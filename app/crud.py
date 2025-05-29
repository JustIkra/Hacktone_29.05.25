from sqlalchemy.orm import Session
from typing import List, Optional
from app import models, schemas, utils

# -------------------------
# USERS
# -------------------------

def get_user(db: Session, user_id: int) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_username(db: Session, username: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.username == username).first()

def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[models.User]:
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    hashed_password = utils.hash_password(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        password_hash=hashed_password,
        role=user.role,
        client_id=user.client_id
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user_role(db: Session, user_id: int, new_role: str) -> Optional[models.User]:
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user:
        user.role = new_role
        db.commit()
        db.refresh(user)
    return user

def delete_user(db: Session, user_id: int) -> Optional[models.User]:
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user:
        db.delete(user)
        db.commit()
    return user

# -------------------------
# CLIENTS
# -------------------------

def get_client(db: Session, client_id: int) -> Optional[models.Client]:
    return db.query(models.Client).filter(models.Client.id == client_id).first()

def get_clients(db: Session, skip: int = 0, limit: int = 100) -> List[models.Client]:
    return db.query(models.Client).offset(skip).limit(limit).all()

def create_client(db: Session, client: schemas.ClientCreate) -> models.Client:
    db_client = models.Client(
        name=client.name,
        tariff=client.tariff
    )
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client

def delete_client(db: Session, client_id: int) -> Optional[models.Client]:
    client = db.query(models.Client).filter(models.Client.id == client_id).first()
    if client:
        db.delete(client)
        db.commit()
    return client

# -------------------------
# SERVICES
# -------------------------

def get_service(db: Session, service_id: int) -> Optional[models.Service]:
    return db.query(models.Service).filter(models.Service.id == service_id).first()

def get_services(db: Session, skip: int = 0, limit: int = 100) -> List[models.Service]:
    return db.query(models.Service).offset(skip).limit(limit).all()

def create_service(db: Session, service: schemas.ServiceCreate) -> models.Service:
    db_service = models.Service(
        name=service.name,
        description=service.description
    )
    db.add(db_service)
    db.commit()
    db.refresh(db_service)
    return db_service

def delete_service(db: Session, service_id: int) -> Optional[models.Service]:
    service = db.query(models.Service).filter(models.Service.id == service_id).first()
    if service:
        db.delete(service)
        db.commit()
    return service

# -------------------------
# CLIENT SERVICES (Подключение сервисов клиентам)
# -------------------------

def connect_service_to_client(db: Session, client_id: int, service_id: int) -> models.ClientService:
    db_cs = models.ClientService(client_id=client_id, service_id=service_id)
    db.add(db_cs)
    db.commit()
    db.refresh(db_cs)
    return db_cs

def get_client_services(db: Session, client_id: int) -> List[models.ClientService]:
    return db.query(models.ClientService).filter(models.ClientService.client_id == client_id).all()

def disconnect_service_from_client(db: Session, client_id: int, service_id: int) -> Optional[models.ClientService]:
    cs = db.query(models.ClientService).filter(
        models.ClientService.client_id == client_id,
        models.ClientService.service_id == service_id
    ).first()
    if cs:
        db.delete(cs)
        db.commit()
    return cs

# -------------------------
# USAGE (Отчётность)
# -------------------------

def create_usage(db: Session, client_service_id: int, user_id: int, usage_amount: int) -> models.Usage:
    usage = models.Usage(
        client_service_id=client_service_id,
        user_id=user_id,
        usage_amount=usage_amount
    )
    db.add(usage)
    db.commit()
    db.refresh(usage)
    return usage

def get_usage_for_client(db: Session, client_id: int) -> List[models.Usage]:
    return db.query(models.Usage).join(models.ClientService).filter(
        models.ClientService.client_id == client_id
    ).all()

def get_usage_for_user(db: Session, user_id: int) -> List[models.Usage]:
    return db.query(models.Usage).filter(models.Usage.user_id == user_id).all()
