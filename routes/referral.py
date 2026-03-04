from fastapi import APIRouter, Depends
from ..dependencies import get_current_user
from ..database import get_db

router = APIRouter()

@router.get("/code")
async def get_referral_code(user=Depends(get_current_user)):
    return {"referral_code": user["referral_code"]}

@router.get("/list")
async def get_referrals(user=Depends(get_current_user), db=Depends(get_db)):
    referrals = await db.users.find(
        {"referrer_id": user["telegram_id"]}
    ).to_list(length=100)
    return {"referrals": referrals, "count": len(referrals)}
