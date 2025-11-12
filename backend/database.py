from datetime import datetime
from typing import Any, Dict, Optional
import os
import motor.motor_asyncio

MONGO_URL = os.environ.get("DATABASE_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DATABASE_NAME", "appdb")

_client: Optional[motor.motor_asyncio.AsyncIOMotorClient] = None
_db: Optional[motor.motor_asyncio.AsyncIOMotorDatabase] = None


def get_db() -> motor.motor_asyncio.AsyncIOMotorDatabase:
    global _client, _db
    if _db is None:
        _client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)
        _db = _client[DB_NAME]
    return _db


def collection(name: str):
    return get_db()[name]


async def create_document(collection_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
    data = {**data, "created_at": datetime.utcnow().isoformat()}
    col = collection(collection_name)
    res = await col.insert_one(data)
    data["_id"] = str(res.inserted_id)
    return data


async def get_documents(collection_name: str, filter_dict: Dict[str, Any] | None = None, limit: int = 50):
    col = collection(collection_name)
    cursor = col.find(filter_dict or {}).limit(limit)
    items = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        items.append(doc)
    return items
