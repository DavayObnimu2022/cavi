from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from db.base import Base

class PatientGroup(Base):
    __tablename__ = "patient_groups"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    description = Column(String(500), nullable=False)
    status = Column(String(20), nullable=False, default="draft")
    image_url = Column(String(255), nullable=True)
    video_url = Column(String(255), nullable=True)
    age = Column(Integer, nullable=True)
    pressure = Column(Integer, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())