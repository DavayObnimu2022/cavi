from pydantic import BaseModel


class LikeRequest(BaseModel):
    value: int


class LikeResponse(BaseModel):
    success: bool
    likes_count: int
    is_liked: int