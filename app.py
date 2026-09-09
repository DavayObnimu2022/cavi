from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn

app = FastAPI(title="CAVI Мониторинг")

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

templates = Jinja2Templates(directory="templates")

# КОЛЛЕКЦИЯ УСЛУГ
services = [
    {
        "id": 1,
        "title": "Пациент: 40-50 лет",
        "age_group": "40-50 лет",
        "hypertension": "Да",
        "diabetes": "Нет",
        "likes": 64,
        "status": "published",
        "image": "http://localhost:9000/img/patient1.jpg",
        "video": "http://localhost:9000/img/patient1.mp4",
        "subtitle": "Возрастная группа 40-50 лет",
        "description": "с артериальной гипертензией. Рекомендуется регулярный мониторинг АД и прием гипотензивных препаратов."
    },
    {
        "id": 2,
        "title": "Пациент: 50-60 лет",
        "age_group": "50-60 лет",
        "hypertension": "Нет",
        "diabetes": "Нет",
        "likes": 89,
        "status": "published",
        "image": "http://localhost:9000/img/patient2.jpg",
        "video": "http://localhost:9000/img/patient2.mp4",
        "subtitle": "Возрастная группа 50-60 лет",
        "description": "без сахарного диабета. Требуется контроль уровня холестерина и профилактика сердечно-сосудистых заболеваний."
    },
    {
        "id": 3,
        "title": "Группа риска 60+",
        "age_group": "60+ лет",
        "hypertension": "Да",
        "diabetes": "Да",
        "likes": 112,
        "status": "published",
        "image": "http://localhost:9000/img/patient3.jpg",
        "video": "http://localhost:9000/img/patient3.mp4",
        "subtitle": "Возрастная группа 60+ лет",
        "description": "с гипертензией и диабетом. Высокий риск сердечно-сосудистых осложнений. Необходим комплексный подход к лечению."
    },
    {
        "id": 4,
        "title": "Атипичные случаи 30-40",
        "age_group": "30-40 лет",
        "hypertension": "Нет",
        "diabetes": "Да",
        "likes": 43,
        "status": "published",
        "image": "http://localhost:9000/img/patient4.jpg",
        "video": "http://localhost:9000/img/patient4.mp4",
        "subtitle": "Возрастная группа 30-40 лет",
        "description": "с сахарным диабетом. Раннее выявление и коррекция образа жизни для предотвращения осложнений."
    },
    {
        "id": 5,
        "title": "Спортсмены 20-30 лет",
        "age_group": "20-30 лет",
        "hypertension": "Нет",
        "diabetes": "Нет",
        "likes": 28,
        "status": "published",
        "image": "http://localhost:9000/img/patient5.jpg",
        "video": "http://localhost:9000/img/patient5.mp4",
        "subtitle": "Возрастная группа 20-30 лет",
        "description": "Контрольная группа, занимающиеся спортом. Низкий риск сердечно-сосудистых заболеваний. Рекомендуется продолжать активный образ жизни."
    },
    {
        "id": 6,
        "title": "Диабет 45-55 лет",
        "age_group": "45-55 лет",
        "hypertension": "Нет",
        "diabetes": "Да",
        "likes": 51,
        "status": "published",
        "image": "http://localhost:9000/img/patient6.jpg",
        "video": "http://localhost:9000/img/patient6.mp4",
        "subtitle": "Возрастная группа 45-55 лет",
        "description": "с сахарным диабетом. Требуется регулярный контроль гликемии и профилактика сосудистых осложнений."
    },
    {
        "id": 7,
        "title": "Гипертония 55-65 лет",
        "age_group": "55-65 лет",
        "hypertension": "Да",
        "diabetes": "Нет",
        "likes": 97,
        "status": "published",
        "image": "http://localhost:9000/img/patient7.jpg",
        "video": "http://localhost:9000/img/patient7.mp4",
        "subtitle": "Возрастная группа 55-65 лет",
        "description": "с гипертензией. Риск инсульта и инфаркта. Необходим строгий контроль АД и регулярные обследования."
    },
    {
        "id": 8,
        "title": "Контроль 35-45 лет",
        "age_group": "35-45 лет",
        "hypertension": "Нет",
        "diabetes": "Нет",
        "likes": 34,
        "status": "published",
        "image": "http://localhost:9000/img/patient8.jpg",
        "video": "http://localhost:9000/img/patient8.mp4",
        "subtitle": "Возрастная группа 35-45 лет",
        "description": "Контрольная группа без хронических заболеваний. Профилактические мероприятия для сохранения здоровья."
    },
    # ЧЕРНОВИК
    {
        "id": 9,
        "title": "Новый пациент (расчет CAVI)",
        "age_group": "40-50 лет",
        "hypertension": "Да",
        "diabetes": "Нет",
        "likes": 0,
        "status": "draft",
        "image": "http://localhost:9000/img/draft_patient.jpg",
        "video": "http://localhost:9000/img/draft_patient.mp4",
        "subtitle": "Возрастная группа 40-50 лет",
        "description": "Новый пациент для расчета CAVI. Требуется сбор дополнительных данных и первичный осмотр."
    }
]

def get_published():
    return [s for s in services if s["status"] == "published"]

def get_service_by_id(service_id):
    for s in services:
        if s["id"] == service_id:
            return s
    return None

def get_next_service(current_id):
    published = get_published()
    for i, s in enumerate(published):
        if s["id"] == current_id:
            if i + 1 < len(published):
                return published[i + 1]
            return published[0]
    return published[0] if published else None

@app.get("/", response_class=HTMLResponse)
async def feed_page(request: Request, id: int = None, next: bool = False):
    service = None
    if id is not None:
        service = get_service_by_id(id)
        if next and service:
            service = get_next_service(id)
    else:
        published = get_published()
        service = published[0] if published else None
    return templates.TemplateResponse("feed.html", {"request": request, "service": service})

@app.get("/add", response_class=HTMLResponse)
async def add_page(request: Request):
    draft = None
    for s in services:
        if s["status"] == "draft":
            draft = s
            break
    return templates.TemplateResponse("add.html", {"request": request, "service": draft})

@app.get("/grid", response_class=HTMLResponse)
async def grid_page(request: Request, filter_age: str = ""):
    published = get_published()
    if filter_age:
        filtered = []
        for s in published:
            if filter_age in s["age_group"]:
                filtered.append(s)
        published = filtered
    return templates.TemplateResponse("grid.html", {
        "request": request,
        "services": published,
        "filter_age": filter_age
    })

if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)