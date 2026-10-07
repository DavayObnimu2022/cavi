import uvicorn
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from api.handlers import router as frontend_router
from api.api_v1 import router as api_router

app = FastAPI(title="CAVI Мониторинг")

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def root():
    return RedirectResponse(url="/feed_patient_groups")


app.include_router(frontend_router)
app.include_router(api_router)


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)