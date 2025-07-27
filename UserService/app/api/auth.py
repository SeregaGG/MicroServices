from fastapi import APIRouter

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/")
async def login(user_id: int):
    return { "status": f"User {user_id} logged in" }