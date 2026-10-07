from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class PatientGroupBase(BaseModel):
    title: str
    description: str
    age: Optional[int] = None
    pressure: Optional[int] = None


class PatientGroupResponse(PatientGroupBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: str
    image_url: Optional[str] = None
    video_url: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    creator_id: int


class PatientGroupListResponse(PatientGroupResponse):
    is_creator: int = 0


class PatientGroupFeedResponse(PatientGroupResponse):
    is_liked: int = 0
    likes_count: int = 0