"""
냉장고 파먹기 도우미 - FastAPI 백엔드
실행: uvicorn main:app --host 0.0.0.0 --port $PORT
"""
from contextlib import asynccontextmanager
from datetime import date
from pathlib import Path

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text

from database import Base, engine, SessionLocal
from config import settings
from models import FridgeItem
from routers import items, scan, recipe

scheduler = AsyncIOScheduler()
BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR / "frontend"


def daily_expiry_check():
    db = SessionLocal()
    try:
        expired = (
            db.query(FridgeItem)
            .filter(FridgeItem.expiry_date < date.today())
            .all()
        )
        if expired:
            names = ", ".join(f"{it.name}({it.expiry_date})" for it in expired)
            print(f"[만료 체크] {date.today()} 기준 만료 재료 {len(expired)}개: {names}")
        else:
            print(f"[만료 체크] {date.today()} — 만료 재료 없음.")
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # DB 테이블 자동 생성
    Base.metadata.create_all(bind=engine)

    # 매일 자정 만료 체크
    scheduler.add_job(daily_expiry_check, "cron", hour=0, minute=0)
    scheduler.start()
    print("스케줄러 시작 — 매일 자정 유통기한 체크.")
    yield
    scheduler.shutdown()


app = FastAPI(title="냉장고 파먹기 API", version="1.0.0", lifespan=lifespan)

# CORS — Render 배포 시 프론트 도메인으로 좁혀주면 더 안전
origins = [o.strip() for o in settings.ALLOWED_ORIGINS.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(items.router)
app.include_router(scan.router)
app.include_router(recipe.router)


@app.get("/", tags=["health"])
def root():
    return {"status": "ok", "message": "냉장고 파먹기 도우미 API 🥦"}


@app.get("/health", tags=["health"])
def health():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "ok", "db": "connected"}
    except Exception as e:
        return {"status": "error", "db": str(e)}


# 프론트엔드 정적 파일 서빙 (/app 경로)
if FRONTEND_DIR.exists():
    app.mount("/app", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")
