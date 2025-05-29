# app/routers/clientservices.py

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import schemas, crud, database, models
from app.auth import get_current_user, require_role
from app.schemas import UserRole

router = APIRouter(
    prefix="/clientservices",
    tags=["client_services"]
)

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post(
    "/",
    response_model=schemas.ClientServiceRead,
    status_code=status.HTTP_201_CREATED
)
def connect_service_to_client(
    payload: schemas.ClientServiceCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Только portal_admin или client_admin своего клиента
    if current_user.role == UserRole.client_admin and current_user.client_id != payload.client_id:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    # Проверка существования клиента и сервиса
    client = crud.get_client(db, payload.client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Клиент не найден")
    service = crud.get_service(db, payload.service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Сервис не найден")
    # (Опционально) проверка лимита тарифа:
    # if len(crud.get_client_services(db, payload.client_id)) >= client.max_services: ...
    return crud.connect_service_to_client(db, payload.client_id, payload.service_id)

@router.get(
    "/client/{client_id}",
    response_model=List[schemas.ClientServiceRead]
)
def list_client_services(
    client_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # portal_admin видит все, client_admin и user — только своего клиента
    if current_user.role != UserRole.portal_admin and current_user.client_id != client_id:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    return crud.get_client_services(db, client_id)

@router.delete(
    "/{clientservice_id}",
    response_model=schemas.ClientServiceRead
)
def disconnect_service_from_client(
    clientservice_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Найти запись
    cs = db.query(models.ClientService).filter(models.ClientService.id == clientservice_id).first()
    if not cs:
        raise HTTPException(status_code=404, detail="Подключение не найдено")
    # Права: portal_admin или client_admin своего клиента
    if current_user.role == UserRole.client_admin and current_user.client_id != cs.client_id:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    # Отключить
    deleted = crud.disconnect_service_from_client(db, cs.client_id, cs.service_id)
    return deleted
