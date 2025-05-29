# app/routers/users.py

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

import crud, schemas, database, utils, models
from auth import get_current_user, require_role
from schemas import UserRole

router = APIRouter(
    prefix="/users",
    tags=["users"],
)

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# CREATE: только portal_admin
@router.post(
    "/",
    response_model=schemas.UserRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role(UserRole.portal_admin))]
)
def create_user(
    user_in: schemas.UserCreate,
    db: Session = Depends(get_db)
):
    if crud.get_user_by_username(db, user_in.username):
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud.create_user(db, user_in)

# LIST: portal_admin видит всех, client_admin своих, user – только себя
@router.get(
    "/",
    response_model=List[schemas.UserRead],
    dependencies=[Depends(get_current_user)]
)
def list_users(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.role == UserRole.portal_admin:
        return crud.get_users(db)
    elif current_user.role == UserRole.client_admin:
        return db.query(models.User).filter(models.User.client_id == current_user.client_id).all()
    else:  # обычный пользователь
        return [current_user]

# READ: portal_admin любой, client_admin своих, user – только себя
@router.get(
    "/{user_id}",
    response_model=schemas.UserRead,
    dependencies=[Depends(get_current_user)]
)
def read_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if current_user.role == UserRole.portal_admin:
        return user
    if current_user.role == UserRole.client_admin and user.client_id == current_user.client_id:
        return user
    if current_user.role == UserRole.user and user.id == current_user.id:
        return user
    raise HTTPException(status_code=403, detail="Insufficient permissions")

# UPDATE: только portal_admin
@router.put(
    "/{user_id}",
    response_model=schemas.UserRead,
    dependencies=[Depends(require_role(UserRole.portal_admin))]
)
def update_user(
    user_id: int,
    user_in: schemas.UserCreate,
    db: Session = Depends(get_db)
):
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    # Обновляем поля
    user.email = user_in.email
    user.role = user_in.role
    user.client_id = user_in.client_id
    # Если передали пароль — меняем хэш
    if user_in.password:
        user.password_hash = utils.hash_password(user_in.password)
    db.commit()
    db.refresh(user)
    return user

# DELETE: только portal_admin
@router.delete(
    "/{user_id}",
    response_model=schemas.UserRead,
    dependencies=[Depends(require_role(UserRole.portal_admin))]
)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    user = crud.delete_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
