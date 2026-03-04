from fastapi import APIRouter, Depends, HTTPException
from ..dependencies import get_current_user
from ..database import get_db
from ..models import TransactionModel
from datetime import datetime, timezone

router = APIRouter()

@router.get("/balance")
async def get_balance(user=Depends(get_current_user)):
    return {"balance": user["balance"]}

@router.post("/add-funds")
async def add_funds(
    amount: float,
    description: str = None,
    user=Depends(get_current_user),
    db=Depends(get_db)
):
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")

    await db.users.update_one(
        {"_id": user["_id"]},
        {
            "$inc": {"balance": amount},
            "$set": {"updated_at": datetime.now(timezone.utc)}
        }
    )

    transaction = TransactionModel(
        user_id=user["telegram_id"],
        amount=amount,
        type="credit",
        description=description
    )
    await db.transactions.insert_one(transaction.model_dump(by_alias=True))

    updated_user = await db.users.find_one({"_id": user["_id"]})
    return {"new_balance": updated_user["balance"]}
