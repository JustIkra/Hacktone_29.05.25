# app/routers/usage.py

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

import crud, schemas, database, models
from auth import get_current_user
from schemas import UserRole

router = APIRouter(
    prefix="/usage",
    tags=["usage"],
)

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get(
    "/client/{client_id}",
    response_model=List[schemas.UsageRead]
)
def usage_by_client(
    client_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # portal_admin видит всё, client_admin только по своему client_id
    if current_user.role == UserRole.client_admin and current_user.client_id != client_id:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    # проверим, что клиент существует
    client = crud.get_client(db, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Клиент не найден")
    return crud.get_usage_for_client(db, client_id)

@router.get(
    "/user/{user_id}",
    response_model=List[schemas.UsageRead]
)
def usage_by_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # user видит только свои логи, client_admin — только своего пользователя
    if current_user.role == UserRole.user and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    if current_user.role == UserRole.client_admin:
        # убедимся, что запрошенный user принадлежит тому же client
        target = crud.get_user(db, user_id)
        if not target or target.client_id != current_user.client_id:
            raise HTTPException(status_code=403, detail="Недостаточно прав")
    # проверим, что пользователь существует
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return crud.get_usage_for_user(db, user_id)

@router.get(
    "/service/{service_id}",
    response_model=List[schemas.UsageRead]
)
def usage_by_service(
    service_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Проверяем, что сервис существует
    service = crud.get_service(db, service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Сервис не найден")
    
    # portal_admin — видит всё
    if current_user.role == UserRole.portal_admin:
        return db.query(models.Usage).join(models.ClientService).filter(
            models.ClientService.service_id == service_id
        ).all()
    
    # client_admin — видит usage только по своим клиентам (service должен быть у клиента)
    if current_user.role == UserRole.client_admin:
        client_id = current_user.client_id
        # Проверяем, что этот сервис действительно подключён клиенту client_admin
        client_service = db.query(models.ClientService).filter_by(
            client_id=client_id, service_id=service_id
        ).first()
        if not client_service:
            raise HTTPException(status_code=403, detail="Сервис не подключён вашему клиенту")
        return db.query(models.Usage).join(models.ClientService).filter(
            models.ClientService.client_id == client_id,
            models.ClientService.service_id == service_id
        ).all()
    
    # Обычный пользователь не имеет доступа
    raise HTTPException(status_code=403, detail="Недостаточно прав")
