from fastapi import APIRouter, Depends, HTTPException
from ..database import get_db
from ..models import UserModel
from datetime import datetime, timedelta, timezone
from jose import jwt
from ..config import settings
import secrets

router = APIRouter()

def generate_referral_code():
    return secrets.token_urlsafe(6).upper()

@router.post("/register")
async def register(
    telegram_id: int,
    username: str = None,
    first_name: str = None,
    last_name: str = None,
    referrer_id: int = None,
    db=Depends(get_db)
):
    existing = await db.users.find_one({"telegram_id": telegram_id})
    if existing:
        raise HTTPException(status_code=400, detail="User already registered")

    referral_code = generate_referral_code()
    while await db.users.find_one({"referral_code": referral_code}):
        referral_code = generate_referral_code()

    user = UserModel(
        telegram_id=telegram_id,
        username=username,
        first_name=first_name,
        last_name=last_name,
        referrer_id=referrer_id,
        referral_code=referral_code
    )

    result = await db.users.insert_one(user.model_dump(by_alias=True))
    created_user = await db.users.find_one({"_id": result.inserted_id})

    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = jwt.encode(
        {"sub": str(telegram_id), "exp": expire},
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": UserModel.model_validate(created_user).model_dump()
    }

@router.post("/login")
async def login(telegram_id: int, db=Depends(get_db)):
    user = await db.users.find_one({"telegram_id": telegram_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = jwt.encode(
        {"sub": str(telegram_id), "exp": expire},
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

    return {"access_token": token, "token_type": "bearer"}
