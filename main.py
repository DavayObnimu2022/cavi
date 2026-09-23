import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

# Импортируем модели ДО роутера — чтобы SQLAlchemy знал о всех таблицах
from db.session import get_db, engine, async_session_maker

from api.handlers import router

app = FastAPI(title="CAVI Мониторинг")
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)