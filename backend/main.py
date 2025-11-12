from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from bson import ObjectId

from schemas import PropertyCreate, Property
from database import create_document, get_documents, collection

app = FastAPI(title="Real Estate API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class PropertyQuery(BaseModel):
    q: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    bedrooms: Optional[int] = None


@app.get("/test")
async def test():
    return {"status": "ok"}


@app.post("/properties", response_model=Property)
async def create_property(payload: PropertyCreate):
    data = payload.dict()
    created = await create_document("property", data)
    # normalize id field
    return Property(
        id=str(created.get("_id")),
        title=created["title"],
        description=created["description"],
        price=created["price"],
        lat=created["lat"],
        lng=created["lng"],
        address=created["address"],
        bedrooms=created["bedrooms"],
        bathrooms=created["bathrooms"],
        area=created["area"],
        images=created.get("images", []),
        features=created.get("features", []),
        created_at=created.get("created_at"),
    )


@app.get("/properties", response_model=List[Property])
async def list_properties(q: Optional[str] = None, min_price: Optional[float] = None, max_price: Optional[float] = None, bedrooms: Optional[int] = None, limit: int = 50):
    filter_dict = {}
    if min_price is not None or max_price is not None:
        price_filter = {}
        if min_price is not None:
            price_filter["$gte"] = min_price
        if max_price is not None:
            price_filter["$lte"] = max_price
        filter_dict["price"] = price_filter
    if bedrooms is not None:
        filter_dict["bedrooms"] = {"$gte": bedrooms}
    # Simple text search over title/description
    if q:
        filter_dict["$or"] = [
            {"title": {"$regex": q, "$options": "i"}},
            {"description": {"$regex": q, "$options": "i"}},
            {"address": {"$regex": q, "$options": "i"}},
        ]

    docs = await get_documents("property", filter_dict, limit)
    results: List[Property] = []
    for d in docs:
        results.append(
            Property(
                id=str(d.get("_id")),
                title=d["title"],
                description=d["description"],
                price=d["price"],
                lat=d["lat"],
                lng=d["lng"],
                address=d["address"],
                bedrooms=d["bedrooms"],
                bathrooms=d["bathrooms"],
                area=d["area"],
                images=d.get("images", []),
                features=d.get("features", []),
                created_at=d.get("created_at"),
            )
        )
    return results
