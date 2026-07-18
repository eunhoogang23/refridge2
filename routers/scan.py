from fastapi import APIRouter, File, UploadFile, Form, HTTPException
import base64
import httpx
from services.ai_service import call_ai_vision
from services.barcode_service import lookup_barcode
from schemas import PackageScanResult, ReceiptScanResult

router = APIRouter(prefix="/scan", tags=["Scan"])


@router.get("/barcode/{barcode}")
async def scan_barcode(barcode: str):
    """바코드 숫자로 식품안전나라 API를 조회해 제품 정보를 반환한다."""
    try:
        result = await lookup_barcode(barcode)
        return {"status": "success", "data": result}
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=502, detail=f"바코드 API 호출 실패: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/package")
async def scan_package(file: UploadFile = File(...), provider: str = Form("gemini")):
    try:
        base64_img = base64.b64encode(await file.read()).decode('utf-8')
        prompt = """사진을 보고 아래 JSON 형식으로만 답하라.
{"name":"제품명","category":"채소|과일|육류|수산물|유제품|가공식품|냉동식품|기타","expiryDateOnPackage":"YYYY-MM-DD 또는 null","estimatedShelfLifeDays":보관가능일수(정수)}"""
        
        result = await call_ai_vision(prompt, base64_img, file.content_type, provider, schema=PackageScanResult)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/receipt")
async def scan_receipt(file: UploadFile = File(...), provider: str = Form("gemini")):
    try:
        base64_img = base64.b64encode(await file.read()).decode('utf-8')
        prompt = """마트 영수증이다. 식품 항목만 추출해 아래 JSON으로 답하라.
{"purchaseDate":"YYYY-MM-DD 또는 null","items":[{"name":"품목명","category":"카테고리","estimatedShelfLifeDays":보관일수}]}"""
        
        result = await call_ai_vision(prompt, base64_img, file.content_type, provider, schema=ReceiptScanResult)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))