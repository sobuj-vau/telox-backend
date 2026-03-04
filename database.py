from motor.motor_asyncio import AsyncIOMotorClient
from config import settings

class Database:
    client: AsyncIOMotorClient = None
    db = None

db = Database()

async def init_db():
    db.client = AsyncIOMotorClient(settings.MONGO_URI)
    db.db = db.client[settings.DATABASE_NAME]

async def close_db():
    if db.client:
        db.client.close()

def get_db():
    return db.db
