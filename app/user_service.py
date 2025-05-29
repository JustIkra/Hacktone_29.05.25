# app/routers/user_service.py

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

import crud, schemas, database, models
from auth import get_current_user
from schemas import UserRole

router = APIRouter(
    prefix="/user_service",
    tags=["user_service"],
)

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post(
    "/",
    response_model=schemas.UserServiceRead,
    status_code=status.HTTP_201_CREATED
)
def assign_service_to_user(
    payload: schemas.UserServiceCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Только админ клиента может назначать сервисы
    if current_user.role != UserRole.client_admin:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    # Проверяем, что пользователь и client_service существуют
    user = crud.get_user(db, payload.user_id)
    if not user or user.client_id != current_user.client_id:
        raise HTTPException(status_code=404, detail="Target user not found or outside your client")
    cs = crud.get_client_service(db, payload.client_service_id)
    if not cs or cs.client_id != current_user.client_id:
        raise HTTPException(status_code=404, detail="ClientService not found or outside your client")
    # Проверяем лимит по тарифу (max_users_per_service)
    client = crud.get_client(db, current_user.client_id)
    assigned = crud.get_user_service_count(db, cs.id)
    if assigned >= int(client.tariff_limits.get("max_users_per_service", assigned + 1)):
        raise HTTPException(status_code=400, detail="Service user-limit exceeded")
    return crud.create_user_service(db, payload.user_id, payload.client_service_id)

@router.get(
    "/user/{user_id}",
    response_model=List[schemas.UserServiceRead]
)
def list_user_services(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Пользователь видит только свои, админ клиента — своих пользователей
    if current_user.role == UserRole.user and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    if current_user.role == UserRole.client_admin and user_id != current_user.client_id:
        # user_id не совпадает с клиентом — сначала убедимся, что user принадлежит клиенту
        target = crud.get_user(db, user_id)
        if not target or target.client_id != current_user.client_id:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
    return crud.get_user_services(db, user_id)

@router.delete(
    "/{user_service_id}",
    response_model=schemas.UserServiceRead
)
def revoke_user_service(
    user_service_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    us = crud.get_user_service(db, user_service_id)
    if not us:
        raise HTTPException(status_code=404, detail="UserService not found")
    # Только админ клиента своего клиента может отзывать
    if current_user.role != UserRole.client_admin or us.user.client_id != current_user.client_id:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    return crud.delete_user_service(db, user_service_id)
