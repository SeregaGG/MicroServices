from fastapi import APIRouter

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/")
async def create_user():
    return []

@router.get("/{user_id}")
async def read_user(user_id: int):
    return { "user_id": user_id }