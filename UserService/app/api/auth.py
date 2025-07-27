from fastapi import APIRouter

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/")
async def create_user():
    return []

@router.post("/")
async def login(user_id: int):
    return { "status": f"User {user_id} logged in" }