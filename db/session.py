from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from core.config import settings
from db.base import Base

# ВАЖНО: импортируем ВСЕ модели, чтобы SQLAlchemy знал о таблицах
from models.user import User
from models.patient_group import PatientGroup
from models.like import Like

engine = create_async_engine(settings.DATABASE_URL, echo=False)
async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db():
    async with async_session_maker() as session:
        yield session