from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
import os
from database import engine, Base
from routes import router
from dependencies import get_current_user
from init_data import init_test_data


#@asynccontextmanager
async def lifespan(app: FastAPI):
    # Удаляем старую базу данных для пересоздания
    if os.path.exists("auth_system.db"):
       os.remove("auth_system.db")
       print("Старая база данных удалена")
    # Создание таблиц при запуске
    Base.metadata.create_all(bind=engine)
    init_test_data()
    yield


app = FastAPI(
    title="Система аутентификации и авторизации",
    description="Собственная система управления доступом к ресурсам",
    version="1.0.0",
    lifespan=lifespan
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутера
app.include_router(router, prefix="/api")

# Защищенный эндпоинт для проверки
@app.get("/api/protected")
async def protected_route(current_user = Depends(get_current_user)):
    return {"message": "Доступ разрешен", "user": current_user.email}

@app.get("/")
async def root():
    return {"message": "Главная страница"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)