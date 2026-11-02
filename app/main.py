import os
import redis
from redis.exceptions import RedisError

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

app = FastAPI(
    title="Cloud Portfolio Inventory API",
    description="A container-ready inventory API built with FastAPI.",
    version="1.0.0"
)


redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "redis"),
    port=int(os.getenv("REDIS_PORT", "6379")),
    decode_responses=True,
    socket_connect_timeout=2,
    socket_timeout=2,
)



# Define the expected structure of a new item
class ItemCreate(BaseModel):
    name: str = Field(min_length=1)
    quantity: int = Field(ge=0)
    price: float = Field(ge=0)


# Temporary in-memory inventory
items = {
    1: {
        "id": 1,
        "name": "Laptop",
        "quantity": 5,
        "price": 850.00
    },
    2: {
        "id": 2,
        "name": "Keyboard",
        "quantity": 12,
        "price": 45.00
    }
}


@app.get("/")
def read_root():
    return {
        "message": "Welcome to my Cloud Portfolio API",
        "version": "1.0.0"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "cloud-portfolio-api",
        "version": "1.0.0"
    }


@app.get("/items")
def get_items():
    return list(items.values())


@app.get("/items/{item_id}")
def get_item(item_id: int):
    if item_id not in items:
        raise HTTPException(
            status_code=404,
            detail="Item not found"
        )

    return items[item_id]


@app.post("/items", status_code=status.HTTP_201_CREATED)
def create_item(item: ItemCreate):
    new_id = max(items.keys(), default=0) + 1

    new_item = {
        "id": new_id,
        **item.model_dump()
    }

    items[new_id] = new_item

    return new_item


@app.get("/visits")
def get_visits():
    try:
        total_visits = redis_client.incr("portfolio:visits")

        return {
            "message": "Visit counter stored in Redis",
            "visits": total_visits
        }

    except RedisError:
        raise HTTPException(
            status_code=503,
            detail="Redis service unavailable"
        )

