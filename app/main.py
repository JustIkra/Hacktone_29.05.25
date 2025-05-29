from fastapi import FastAPI
from init_db import init_db

# Импорт роутеров из текущей папки
import auth
import users
import clients
import services
import clientservices
import tariffs
import user_service
import usage
import uvicorn


# Инициализация БД (создаёт таблицы)
init_db()

# Инициализация приложения
app = FastAPI(
    title="Gendalf Services Portal",
    description="API для управления клиентами, сервисами и тарифами",
    version="0.1.0",
)

# Подключение роутеров
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(clients.router)
app.include_router(services.router)
app.include_router(clientservices.router)
app.include_router(tariffs.router)
app.include_router(user_service.router)
app.include_router(usage.router)

if __name__ == "__main__":
    init_db()
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
