import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn

os.makedirs("static", exist_ok=True)
os.makedirs("templates", exist_ok=True)

app = FastAPI(title="CAVI Мониторинг")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# ============================================
# КОЛЛЕКЦИЯ: patient_groups
# Поля: age (возраст), pressure (давление)
# Лайки = длина вложенного массива
# ============================================
patient_groups = [
    {
        "id": 1,
        "title": "Пациент: 40-50 лет",
        "age": 45,
        "pressure": 140,
        "likes": list(range(1, 65)),
        "status": "published",
        "image": "http://localhost:9000/img/patient1.jpg",
        "video": "http://localhost:9000/img/patient1.mp4",
        "subtitle": "Возрастная группа 40-50 лет",
        "description": "с артериальной гипертензией. Рекомендуется регулярный мониторинг АД и прием гипотензивных препаратов."
    },
    {
        "id": 2,
        "title": "Пациент: 50-60 лет",
        "age": 55,
        "pressure": 130,
        "likes": list(range(1, 90)),
        "status": "published",
        "image": "http://localhost:9000/img/patient2.jpg",
        "video": "http://localhost:9000/img/patient2.mp4",
        "subtitle": "Возрастная группа 50-60 лет",
        "description": "без сахарного диабета. Требуется контроль уровня холестерина и профилактика ССЗ."
    },
    {
        "id": 3,
        "title": "Группа риска 60+",
        "age": 65,
        "pressure": 150,
        "likes": list(range(1, 113)),
        "status": "published",
        "image": "http://localhost:9000/img/patient3.jpg",
        "video": "http://localhost:9000/img/patient3.mp4",
        "subtitle": "Возрастная группа 60+ лет",
        "description": "с гипертензией и диабетом. Высокий риск ССЗ. Необходим комплексный подход."
    },
    {
        "id": 4,
        "title": "Атипичные случаи 30-40",
        "age": 35,
        "pressure": 125,
        "likes": list(range(1, 44)),
        "status": "published",
        "image": "http://localhost:9000/img/patient4.jpg",
        "video": "http://localhost:9000/img/patient4.mp4",
        "subtitle": "Возрастная группа 30-40 лет",
        "description": "с сахарным диабетом. Раннее выявление и коррекция образа жизни."
    },
    {
        "id": 5,
        "title": "Спортсмены 20-30 лет",
        "age": 25,
        "pressure": 120,
        "likes": list(range(1, 29)),
        "status": "published",
        "image": "http://localhost:9000/img/patient5.jpg",
        "video": "http://localhost:9000/img/patient5.mp4",
        "subtitle": "Возрастная группа 20-30 лет",
        "description": "Контрольная группа, занимающиеся спортом. Низкий риск ССЗ."
    },
    {
        "id": 6,
        "title": "Диабет 45-55 лет",
        "age": 50,
        "pressure": 135,
        "likes": list(range(1, 52)),
        "status": "published",
        "image": "http://localhost:9000/img/patient6.jpg",
        "video": "http://localhost:9000/img/patient6.mp4",
        "subtitle": "Возрастная группа 45-55 лет",
        "description": "с сахарным диабетом. Требуется контроль гликемии."
    },
    {
        "id": 7,
        "title": "Гипертония 55-65 лет",
        "age": 60,
        "pressure": 160,
        "likes": list(range(1, 98)),
        "status": "published",
        "image": "http://localhost:9000/img/patient7.jpg",
        "video": "http://localhost:9000/img/patient7.mp4",
        "subtitle": "Возрастная группа 55-65 лет",
        "description": "с гипертензией. Риск инсульта и инфаркта."
    },
    {
        "id": 8,
        "title": "Контроль 35-45 лет",
        "age": 40,
        "pressure": 128,
        "likes": list(range(1, 35)),
        "status": "published",
        "image": "http://localhost:9000/img/patient8.jpg",
        "video": "http://localhost:9000/img/patient8.mp4",
        "subtitle": "Возрастная группа 35-45 лет",
        "description": "Контрольная группа без хронических заболеваний."
    },
    # ЧЕРНОВИК
    {
        "id": 9,
        "title": "Новый пациент (расчет CAVI)",
        "age": 45,
        "pressure": 135,
        "likes": [],
        "status": "draft",
        "image": "http://localhost:9000/img/draft_patient.jpg",
        "video": "http://localhost:9000/img/draft_patient.mp4",
        "subtitle": "Возрастная группа 40-50 лет",
        "description": "Новый пациент для расчета CAVI. Требуется сбор дополнительных данных."
    }
]

def get_published():
    return [s for s in patient_groups if s["status"] == "published"]

def get_service_by_id(service_id):
    for s in patient_groups:
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

# ============================================
# 3 GET ЗАПРОСА
# ============================================

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
    for s in patient_groups:
        if s["status"] == "draft":
            draft = s
            break
    return templates.TemplateResponse("add.html", {"request": request, "service": draft})

@app.get("/grid", response_class=HTMLResponse)
async def grid_page(request: Request, filter_age_min: int = 0, filter_age_max: int = 100):
    published = get_published()
    filtered = [s for s in published if filter_age_min <= s["age"] <= filter_age_max]
    return templates.TemplateResponse("grid.html", {
        "request": request,
        "services": filtered,
        "filter_age_min": filter_age_min,
        "filter_age_max": filter_age_max
    })

if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)