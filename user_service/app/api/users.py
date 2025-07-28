import random
from fastapi import APIRouter

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/")
async def create_user():
    return { "user_id": random.choice((1, 2, 3)) }

@router.get("/{user_id}")
async def read_user(user_id: int):
    return { "user_id": user_id }