from fastapi import APIRouter, Depends, HTTPException
from ..database import get_db
from ..dependencies import get_current_user
from ..models import TaskModel
from ..config import settings

router = APIRouter()

async def is_admin(user=Depends(get_current_user)):
    if user.get("telegram_id") not in settings.admin_ids_list:
        raise HTTPException(status_code=403, detail="Admin only")
    return user

@router.get("/users")
async def list_users(admin=Depends(is_admin), db=Depends(get_db)):
    users = await db.users.find().to_list(length=1000)
    return users

@router.post("/tasks/create")
async def create_task(
    title: str,
    reward: float,
    description: str = None,
    admin=Depends(is_admin),
    db=Depends(get_db)
):
    task = TaskModel(
        title=title,
        description=description,
        reward=reward
    )
    result = await db.tasks.insert_one(task.model_dump(by_alias=True))
    created = await db.tasks.find_one({"_id": result.inserted_id})
    return created
