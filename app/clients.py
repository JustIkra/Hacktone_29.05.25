# app/routers/clients.py

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

import crud, schemas, database
from auth import get_current_user, require_role
from models import UserRole, User

router = APIRouter(
    prefix="/clients",
    tags=["clients"],
)

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post(
    "/",
    response_model=schemas.ClientRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role(schemas.UserRole.portal_admin))]
)
def create_client(
    client_in: schemas.ClientCreate,
    db: Session = Depends(get_db)
):
    # Проверка на уникальность
    existing = db.query(database.Base.metadata.tables["clients"]).filter_by(name=client_in.name).first()
    if crud.get_client(db, client_in.name):  # или по id, если придётся
        raise HTTPException(status_code=400, detail="Client with this name already exists")
    return crud.create_client(db, client_in)

@router.get(
    "/",
    response_model=List[schemas.ClientRead]
)
def list_clients(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(schemas.UserRole.portal_admin)),
):
    return crud.get_clients(db, skip=skip, limit=limit)

@router.get(
    "/{client_id}",
    response_model=schemas.ClientRead
)
def read_client(
    client_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    client = crud.get_client(db, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    # Проверка прав: portal_admin видит всех, client_admin/user — только своего
    if current_user.role != UserRole.portal_admin:
        if current_user.client_id != client_id:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
    return client

@router.get(
    "/me",
    response_model=schemas.ClientRead
)
def read_own_client(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.client_id:
        raise HTTPException(status_code=400, detail="User is not bound to any client")
    client = crud.get_client(db, current_user.client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client

@router.put(
    "/{client_id}",
    response_model=schemas.ClientRead,
    dependencies=[Depends(require_role(schemas.UserRole.portal_admin))]
)
def update_client(
    client_id: int,
    client_in: schemas.ClientCreate,
    db: Session = Depends(get_db)
):
    client = crud.get_client(db, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    client.name = client_in.name
    client.tariff = client_in.tariff
    db.commit()
    db.refresh(client)
    return client

@router.delete(
    "/{client_id}",
    response_model=schemas.ClientRead,
    dependencies=[Depends(require_role(schemas.UserRole.portal_admin))]
)
def delete_client(
    client_id: int,
    db: Session = Depends(get_db)
):
    client = crud.get_client(db, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    crud.delete_client(db, client_id)
    return client
