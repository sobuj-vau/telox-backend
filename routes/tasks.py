from fastapi import APIRouter, Depends, HTTPException
from ..dependencies import get_current_user
from ..database import get_db
from datetime import datetime, timezone
from bson import ObjectId

router = APIRouter()

@router.get("/")
async def get_tasks(db=Depends(get_db)):
    tasks = await db.tasks.find({"is_active": True}).to_list(length=100)
    return tasks

@router.post("/{task_id}/complete")
async def complete_task(
    task_id: str,
    user=Depends(get_current_user),
    db=Depends(get_db)
):
    if not ObjectId.is_valid(task_id):
        raise HTTPException(status_code=400, detail="Invalid task ID")
    
    task = await db.tasks.find_one({"_id": ObjectId(task_id), "is_active": True})
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    already_done = await db.completed_tasks.find_one({
        "user_id": user["telegram_id"],
        "task_id": task_id
    })
    if already_done:
        raise HTTPException(status_code=400, detail="Task already completed")
    
    await db.completed_tasks.insert_one({
        "user_id": user["telegram_id"],
        "task_id": task_id,
        "completed_at": datetime.now(timezone.utc)
    })
    
    await db.users.update_one(
        {"_id": user["_id"]},
        {"$inc": {"balance": task["reward"]}, "$set": {"updated_at": datetime.now(timezone.utc)}}
    )
    
    return {"success": True, "reward": task["reward"]}
