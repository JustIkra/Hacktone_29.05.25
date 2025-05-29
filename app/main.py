# app/main.py

from fastapi import FastAPI
from app.database import init_db
from app.routers import (
    auth,
    users,
    clients,
    services,
    clientservices,
    tariffs,
    user_service,
    usage,
)

# Инициализация базы (создание таблиц) – для прототипа
init_db()

app = FastAPI(
    title="Гendalf Services Portal",
    description="API для управления клиентами, сервисами и тарифами",
    version="0.1.0",
)

# Роутеры
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(clients.router)
app.include_router(services.router)
app.include_router(clientservices.router)
app.include_router(tariffs.router)
app.include_router(user_service.router)
app.include_router(usage.router)
