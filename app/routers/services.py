# app/routers/services.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app import crud, schemas, database
from app.auth import require_role, get_current_user

router = APIRouter()

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=schemas.ServiceRead,
             dependencies=[Depends(require_role(schemas.UserRole.portal_admin))])
def create_service(service: schemas.ServiceCreate, db: Session = Depends(get_db)):
    return crud.create_service(db, service)

@router.get("/", response_model=List[schemas.ServiceRead])
def list_services(db: Session = Depends(get_db), user = Depends(get_current_user)):
    return crud.get_services(db)

# PUT и DELETE аналогично
