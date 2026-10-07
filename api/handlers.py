from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_db
from models.patient_group import PatientGroup
from models.user import User
from models.like import Like

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# Дефолтные — локальные
DEFAULT_IMAGE = "/static/img/default.jpg"
DEFAULT_VIDEO = "/static/img/default.mp4"

# GET 1: Лента
@router.get("/feed_patient_groups")
async def feed_page(request: Request, id: int = None, next: bool = False, db: AsyncSession = Depends(get_db)):
    if id is not None:
        stmt = select(PatientGroup).where(
            PatientGroup.id == id,
            PatientGroup.status != "deleted"
        )
        result = await db.execute(stmt)
        service = result.scalar_one_or_none()

        if next and service:
            stmt_next = select(PatientGroup).where(
                PatientGroup.id > service.id,
                PatientGroup.status == "published"
            ).order_by(PatientGroup.id).limit(1)
            result_next = await db.execute(stmt_next)
            next_service = result_next.scalar_one_or_none()

            if not next_service:
                stmt_first = select(PatientGroup).where(
                    PatientGroup.status == "published"
                ).order_by(PatientGroup.id).limit(1)
                result_first = await db.execute(stmt_first)
                next_service = result_first.scalar_one_or_none()

            if next_service:
                service = next_service
    else:
        stmt = select(PatientGroup).where(
            PatientGroup.status == "published"
        ).order_by(PatientGroup.id).limit(1)
        result = await db.execute(stmt)
        service = result.scalar_one_or_none()

    likes_count = 0
    if service:
        likes_stmt = select(Like).where(Like.patient_group_id == service.id)
        likes_result = await db.execute(likes_stmt)
        likes_count = len(likes_result.scalars().all())

    return templates.TemplateResponse("feed_patient_groups.html", {
        "request": request,
        "service": service,
        "likes_count": likes_count,
        "default_image": DEFAULT_IMAGE,
        "default_video": DEFAULT_VIDEO
    })

# GET 2: Добавление
@router.get("/add_patient_groups")
async def add_page(request: Request, db: AsyncSession = Depends(get_db)):
    stmt = select(PatientGroup).where(PatientGroup.status == "draft").limit(1)
    result = await db.execute(stmt)
    draft = result.scalar_one_or_none()

    return templates.TemplateResponse("add_patient_groups.html", {
        "request": request,
        "service": draft,
        "default_image": DEFAULT_IMAGE,
        "default_video": DEFAULT_VIDEO
    })

# GET 3: Плитка
@router.get("/grid_patient_groups")
async def grid_page(
    request: Request,
    filter_age_min: int = 0,
    filter_age_max: int = 100,
    db: AsyncSession = Depends(get_db)
):
    stmt = select(PatientGroup).where(PatientGroup.status == "published")
    result = await db.execute(stmt)
    services = result.scalars().all()

    items = []
    for s in services:
        if s.age is None:
            show = True
        else:
            show = filter_age_min <= s.age <= filter_age_max

        if show:
            likes_stmt = select(Like).where(Like.patient_group_id == s.id)
            likes_result = await db.execute(likes_stmt)
            likes_count = len(likes_result.scalars().all())

            items.append({
                "id": s.id,
                "title": s.title,
                "age": s.age,
                "image_url": s.image_url or DEFAULT_IMAGE,
                "likes": likes_count
            })

    return templates.TemplateResponse("grid_patient_groups.html", {
        "request": request,
        "items": items,
        "filter_age_min": filter_age_min,
        "filter_age_max": filter_age_max,
        "default_image": DEFAULT_IMAGE
    })

# POST 1: Создание черновика
@router.post("/add_patient_groups/draft")
async def create_draft(
    request: Request,
    title: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(PatientGroup).where(PatientGroup.status == "draft").limit(1)
    result = await db.execute(stmt)
    existing = result.scalar_one_or_none()

    if not existing:
        new_draft = PatientGroup(
            title=title,
            description="",
            status="draft",
            image_url=DEFAULT_IMAGE,
            video_url=DEFAULT_VIDEO,
            age=None,
            pressure=None,
            creator_id=1
        )
        db.add(new_draft)
        await db.commit()

    return RedirectResponse(url="/add_patient_groups", status_code=303)

# POST 2: Публикация
@router.post("/add_patient_groups/publish")
async def publish_draft(
    request: Request,
    description: str = Form(...),
    age: int = Form(...),
    pressure: int = Form(...),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(PatientGroup).where(PatientGroup.status == "draft").limit(1)
    result = await db.execute(stmt)
    draft = result.scalar_one_or_none()

    if draft:
        draft.description = description
        draft.age = age
        draft.pressure = pressure
        draft.status = "published"
        await db.commit()

    return RedirectResponse(url="/feed_patient_groups", status_code=303)

# POST 3: Удаление
@router.post("/grid_patient_groups/{service_id}/delete")
async def delete_service(service_id: int, db: AsyncSession = Depends(get_db)):
    update_query = "UPDATE patient_groups SET status = 'deleted' WHERE id = :id"
    await db.execute(text(update_query), {"id": service_id})
    await db.commit()
    return RedirectResponse(url="/grid_patient_groups", status_code=303)