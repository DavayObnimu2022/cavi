import uvicorn
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from db.session import get_db, engine, async_session_maker
from api.handlers import router

app = FastAPI(title="CAVI Мониторинг")

app.mount("/static", StaticFiles(directory="static"), name="static")

# Редирект с / на /feed_patient_groups
@app.get("/")
async def root():
    return RedirectResponse(url="/feed_patient_groups")

app.include_router(router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)