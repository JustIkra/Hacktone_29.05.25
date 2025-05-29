from fastapi import FastAPI
from app.routers import users, clients, services, reports
from app.database import Base, engine

app = FastAPI(title="Gendalf Portal")

# Создание таблиц при первом запуске (для прототипа)
Base.metadata.create_all(bind=engine)

app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(clients.router, prefix="/clients", tags=["clients"])
app.include_router(services.router, prefix="/services", tags=["services"])
app.include_router(reports.router, prefix="/reports", tags=["reports"])

@app.get("/")
def root():
    return {"message": "Gendalf Portal API works!"}
