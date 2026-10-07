from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from db.session import get_db
from models.patient_group import PatientGroup
from models.user import User
from models.like import Like
from core.singleton import get_current_user
from services.minio_service import minio_service
from schemas.patient_group import (
    PatientGroupResponse,
    PatientGroupListResponse,
    PatientGroupFeedResponse,
)
from schemas.user import (
    UserRegister, UserLogin, UserAuthResponse, UserResponse,
)
from schemas.like import LikeRequest, LikeResponse

router = APIRouter(prefix="/api", tags=["API"])


# 1. GET /api/patient_groups — список с фильтрацией
@router.get("/patient_groups", response_model=list[PatientGroupListResponse])
async def api_list_patient_groups(
    age_min: int = Query(0, ge=0),
    age_max: int = Query(150, le=200),
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    current = get_current_user()
    stmt = select(PatientGroup).where(PatientGroup.status == "published")
    if search:
        stmt = stmt.where(PatientGroup.title.ilike(f"%{search}%"))
    result = await db.execute(stmt)
    services = result.scalars().all()

    items = []
    for s in services:
        if s.age is None or age_min <= s.age <= age_max:
            items.append(PatientGroupListResponse(
                id=s.id, title=s.title, description=s.description,
                status=s.status, image_url=s.image_url, video_url=s.video_url,
                age=s.age, pressure=s.pressure, created_at=s.created_at,
                updated_at=s.updated_at, creator_id=s.creator_id,
                is_creator=1 if s.creator_id == current.id else 0,
            ))
    return items


# 2. GET /api/patient_groups/feed — лента
@router.get("/patient_groups/feed", response_model=list[PatientGroupFeedResponse])
async def api_feed(
    id: Optional[int] = None,
    next: bool = False,
    db: AsyncSession = Depends(get_db)
):
    current = get_current_user()

    if id is not None:
        stmt = select(PatientGroup).where(
            PatientGroup.id == id, PatientGroup.status != "deleted"
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

        if not service:
            raise HTTPException(status_code=404, detail="Service not found")
        services = [service]
    else:
        stmt = select(PatientGroup).where(
            PatientGroup.status == "published"
        ).order_by(PatientGroup.id).limit(1)
        result = await db.execute(stmt)
        service = result.scalar_one_or_none()
        services = [service] if service else []

    items = []
    for s in services:
        likes_stmt = select(func.count()).select_from(Like).where(
            Like.patient_group_id == s.id
        )
        likes_result = await db.execute(likes_stmt)
        likes_count = likes_result.scalar() or 0

        liked_stmt = select(Like).where(
            Like.patient_group_id == s.id, Like.user_id == current.id
        )
        liked_result = await db.execute(liked_stmt)
        is_liked = 1 if liked_result.scalar_one_or_none() else 0

        items.append(PatientGroupFeedResponse(
            id=s.id, title=s.title, description=s.description,
            status=s.status, image_url=s.image_url, video_url=s.video_url,
            age=s.age, pressure=s.pressure, created_at=s.created_at,
            updated_at=s.updated_at, creator_id=s.creator_id,
            is_liked=is_liked, likes_count=likes_count,
        ))
    return items


# 3. GET /api/patient_groups/draft — черновик
@router.get("/patient_groups/draft", response_model=PatientGroupResponse)
async def api_get_draft(db: AsyncSession = Depends(get_db)):
    current = get_current_user()
    stmt = select(PatientGroup).where(
        PatientGroup.creator_id == current.id,
        PatientGroup.status == "draft"
    ).limit(1)
    result = await db.execute(stmt)
    draft = result.scalar_one_or_none()
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")
    return PatientGroupResponse.model_validate(draft)


# 4. POST /api/patient_groups — добавление с файлами
@router.post("/patient_groups", response_model=PatientGroupResponse, status_code=201)
async def api_create_patient_group(
    title: str = Form(...),
    description: str = Form(""),
    age: Optional[int] = Form(None),
    pressure: Optional[int] = Form(None),
    image: Optional[UploadFile] = File(None),
    video: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db)
):
    current = get_current_user()

    stmt = select(PatientGroup).where(
        PatientGroup.creator_id == current.id,
        PatientGroup.status == "draft"
    ).limit(1)
    result = await db.execute(stmt)
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Draft already exists")

    image_filename = None
    video_filename = None
    if image:
        image_filename = await minio_service.upload_file(image, prefix="patient_img")
    if video:
        video_filename = await minio_service.upload_file(video, prefix="patient_vid")

    new_service = PatientGroup(
        title=title, description=description, status="draft",
        image_url=minio_service.get_url(image_filename) if image_filename else None,
        video_url=minio_service.get_url(video_filename) if video_filename else None,
        age=age, pressure=pressure, creator_id=current.id
    )
    db.add(new_service)
    await db.commit()
    await db.refresh(new_service)
    return PatientGroupResponse.model_validate(new_service)


# 5. PUT /api/patient_groups/{id}/publish
@router.put("/patient_groups/{service_id}/publish", response_model=PatientGroupResponse)
async def api_publish(service_id: int, db: AsyncSession = Depends(get_db)):
    current = get_current_user()
    stmt = select(PatientGroup).where(
        PatientGroup.id == service_id,
        PatientGroup.creator_id == current.id,
        PatientGroup.status == "draft"
    )
    result = await db.execute(stmt)
    service = result.scalar_one_or_none()
    if not service:
        raise HTTPException(status_code=404, detail="Draft not found")

    service.status = "published"
    await db.commit()
    await db.refresh(service)
    return PatientGroupResponse.model_validate(service)


# 6. DELETE /api/patient_groups/{id} — soft delete
@router.delete("/patient_groups/{service_id}", response_model=PatientGroupResponse)
async def api_delete(service_id: int, db: AsyncSession = Depends(get_db)):
    current = get_current_user()
    stmt = select(PatientGroup).where(
        PatientGroup.id == service_id,
        PatientGroup.creator_id == current.id,
        PatientGroup.status != "deleted"
    )
    result = await db.execute(stmt)
    service = result.scalar_one_or_none()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    service.status = "deleted"
    await db.commit()
    await db.refresh(service)
    return PatientGroupResponse.model_validate(service)


# 7. POST /api/patient_groups/{id}/like
@router.post("/patient_groups/{service_id}/like", response_model=LikeResponse)
async def api_like(service_id: int, data: LikeRequest, db: AsyncSession = Depends(get_db)):
    current = get_current_user()

    stmt = select(PatientGroup).where(
        PatientGroup.id == service_id,
        PatientGroup.status == "published"
    )
    result = await db.execute(stmt)
    service = result.scalar_one_or_none()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    if data.value not in (0, 1):
        raise HTTPException(status_code=400, detail="Value must be 0 or 1")

    like_stmt = select(Like).where(
        Like.patient_group_id == service_id, Like.user_id == current.id
    )
    like_result = await db.execute(like_stmt)
    existing_like = like_result.scalar_one_or_none()

    if data.value == 1:
        if not existing_like:
            db.add(Like(user_id=current.id, patient_group_id=service_id))
    else:
        if existing_like:
            await db.delete(existing_like)

    await db.commit()

    count_stmt = select(func.count()).select_from(Like).where(
        Like.patient_group_id == service_id
    )
    count_result = await db.execute(count_stmt)
    likes_count = count_result.scalar() or 0

    check_stmt = select(Like).where(
        Like.patient_group_id == service_id, Like.user_id == current.id
    )
    check_result = await db.execute(check_stmt)
    is_liked = 1 if check_result.scalar_one_or_none() else 0

    return LikeResponse(success=True, likes_count=likes_count, is_liked=is_liked)


# 8. POST /api/auth/register
@router.post("/auth/register", response_model=UserAuthResponse)
async def api_register(data: UserRegister, db: AsyncSession = Depends(get_db)):
    stmt = select(User).where(User.username == data.username)
    result = await db.execute(stmt)
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")

    new_user = User(username=data.username, password=data.password)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return UserAuthResponse(
        success=True, message="User registered successfully",
        user=UserResponse.model_validate(new_user)
    )


# 9. POST /api/auth/login
@router.post("/auth/login", response_model=UserAuthResponse)
async def api_login(data: UserLogin, db: AsyncSession = Depends(get_db)):
    stmt = select(User).where(User.username == data.username)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user or user.password != data.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return UserAuthResponse(
        success=True, message="Login successful (stub for LR-4)",
        user=UserResponse.model_validate(user)
    )


# 10. POST /api/auth/logout
@router.post("/auth/logout", response_model=UserAuthResponse)
async def api_logout():
    return UserAuthResponse(
        success=True, message="Logout successful (stub for LR-4)", user=None
    )