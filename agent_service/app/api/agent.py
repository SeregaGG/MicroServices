import random
from fastapi import APIRouter

router = APIRouter(prefix="/vacation_agent", tags=["Actions"])

@router.post("/start")
async def dialog_start():
    return { "message_id": random.choice((1, 2, 3)) }
