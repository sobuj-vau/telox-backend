import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from contextlib import asynccontextmanager

from database import init_db, close_db
from routes import auth, wallet, referral, admin, tasks
from config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    print("✅ MongoDB connected")
    yield
    await close_db()
    print("🔌 MongoDB disconnected")

app = FastAPI(
    title="Telegram Mini App API",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.get("/")
async def read_root():
    return {
        "message": "Telegram Mini App API is running",
        "docs": "/docs",
        "version": app.version
    }

app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(wallet.router, prefix="/api/wallet", tags=["Wallet"])
app.include_router(referral.router, prefix="/api/referral", tags=["Referral"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["Tasks"])

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=settings.DEBUG
    )
