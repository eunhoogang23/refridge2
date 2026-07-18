from fastapi import APIRouter
router = APIRouter(prefix="/items", tags=["Items"])
# 향후 여기에 DB CRUD 로직 (추가, 삭제, 조회)을 작성하세요.