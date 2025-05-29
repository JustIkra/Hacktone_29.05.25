# app/auth.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from app import crud, schemas, database

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")
SECRET = "ваш_секрет"
ALGORITHM = "HS256"

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.SessionLocal)):
    credentials_exception = HTTPException(status_code=401, detail="Невалидный токен")
    try:
        payload = jwt.decode(token, SECRET, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = crud.get_user_by_username(db, username)
    if user is None:
        raise credentials_exception
    return user

def require_role(role: schemas.UserRole):
    def checker(user: models.User = Depends(get_current_user)):
        if user.role != role:
            raise HTTPException(status_code=403, detail="Недостаточно прав")
        return user
    return checker
