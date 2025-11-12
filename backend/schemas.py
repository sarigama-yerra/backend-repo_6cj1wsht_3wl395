from typing import List, Optional
from pydantic import BaseModel, Field, validator


class PropertyBase(BaseModel):
    title: str = Field(..., min_length=2, max_length=140)
    description: str = Field(..., min_length=10, max_length=2000)
    price: float = Field(..., gt=0)
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)
    address: str
    bedrooms: int = Field(..., ge=0)
    bathrooms: float = Field(..., ge=0)
    area: float = Field(..., ge=0, description="Area in square meters")
    images: List[str] = []
    features: List[str] = []

    @validator("images", pre=True)
    def default_images(cls, v):
        return v or []

    @validator("features", pre=True)
    def default_features(cls, v):
        return v or []


class PropertyCreate(PropertyBase):
    pass


class Property(PropertyBase):
    id: str
    created_at: Optional[str] = None

    class Config:
        orm_mode = True
