# app/routers/services.py

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

import schemas, crud, database, models
from auth import get_current_user, require_role

router = APIRouter(
    prefix="/services",
    tags=["services"],
)

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post(
    "/",
    response_model=schemas.ServiceRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role(schemas.UserRole.portal_admin))]
)
def create_service(
    service_in: schemas.ServiceCreate,
    db: Session = Depends(get_db)
):
    # Проверка на уникальность по имени
    existing = crud.get_service_by_name(db, service_in.name) if hasattr(crud, "get_service_by_name") else crud.get_service(db, service_in.name)
    if existing:
        raise HTTPException(status_code=400, detail="Сервис с таким именем уже существует")
    return crud.create_service(db, service_in)

@router.get(
    "/",
    response_model=List[schemas.ServiceRead],
    dependencies=[Depends(get_current_user)]
)
def list_services(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return crud.get_services(db, skip=skip, limit=limit)

@router.get(
    "/{service_id}",
    response_model=schemas.ServiceRead,
    dependencies=[Depends(get_current_user)]
)
def read_service(
    service_id: int,
    db: Session = Depends(get_db)
):
    service = crud.get_service(db, service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Сервис не найден")
    return service

@router.put(
    "/{service_id}",
    response_model=schemas.ServiceRead,
    dependencies=[Depends(require_role(schemas.UserRole.portal_admin))]
)
def update_service(
    service_id: int,
    service_in: schemas.ServiceCreate,
    db: Session = Depends(get_db)
):
    service = crud.get_service(db, service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Сервис не найден")
    service.name = service_in.name
    service.description = service_in.description
    db.commit()
    db.refresh(service)
    return service

@router.delete(
    "/{service_id}",
    response_model=schemas.ServiceRead,
    dependencies=[Depends(require_role(schemas.UserRole.portal_admin))]
)
def delete_service(
    service_id: int,
    db: Session = Depends(get_db)
):
    service = crud.get_service(db, service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Сервис не найден")
    crud.delete_service(db, service_id)
    return service
