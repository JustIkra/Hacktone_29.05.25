# app/routers/tariffs.py

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud, schemas, database
from app.auth import get_current_user, require_role

router = APIRouter(
    prefix="/tariffs",
    tags=["tariffs"],
)

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# CREATE
@router.post(
    "/",
    response_model=schemas.TariffRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role(schemas.UserRole.portal_admin))]
)
def create_tariff(
    tariff_in: schemas.TariffCreate,
    db: Session = Depends(get_db)
):
    # Проверка уникальности названия тарифа
    existing = crud.get_tariff_by_name(db, tariff_in.name)
    if existing:
        raise HTTPException(status_code=400, detail="Тариф с таким именем уже существует")
    return crud.create_tariff(db, tariff_in)

# READ ALL
@router.get(
    "/",
    response_model=List[schemas.TariffRead],
    dependencies=[Depends(get_current_user)]
)
def list_tariffs(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return crud.get_tariffs(db, skip=skip, limit=limit)

# READ ONE
@router.get(
    "/{tariff_id}",
    response_model=schemas.TariffRead,
    dependencies=[Depends(get_current_user)]
)
def read_tariff(
    tariff_id: int,
    db: Session = Depends(get_db)
):
    tariff = crud.get_tariff(db, tariff_id)
    if not tariff:
        raise HTTPException(status_code=404, detail="Тариф не найден")
    return tariff

# UPDATE
@router.put(
    "/{tariff_id}",
    response_model=schemas.TariffRead,
    dependencies=[Depends(require_role(schemas.UserRole.portal_admin))]
)
def update_tariff(
    tariff_id: int,
    tariff_in: schemas.TariffCreate,
    db: Session = Depends(get_db)
):
    tariff = crud.get_tariff(db, tariff_id)
    if not tariff:
        raise HTTPException(status_code=404, detail="Тариф не найден")
    # Обновляем поля
    tariff.name = tariff_in.name
    tariff.max_users = tariff_in.max_users
    tariff.max_services = tariff_in.max_services
    tariff.period_days = tariff_in.period_days
    tariff.price = tariff_in.price
    db.commit()
    db.refresh(tariff)
    return tariff

# DELETE
@router.delete(
    "/{tariff_id}",
    response_model=schemas.TariffRead,
    dependencies=[Depends(require_role(schemas.UserRole.portal_admin))]
)
def delete_tariff(
    tariff_id: int,
    db: Session = Depends(get_db)
):
    tariff = crud.get_tariff(db, tariff_id)
    if not tariff:
        raise HTTPException(status_code=404, detail="Тариф не найден")
    crud.delete_tariff(db, tariff_id)
    return tariff
