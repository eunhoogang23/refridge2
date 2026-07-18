import httpx
from config import settings

BASE_URL = "http://openapi.foodsafetykorea.go.kr/api"

# 서비스 코드
SVC_DISTRIBUTION_BARCODE = "I2570"  # 유통바코드 (2018년 이후 갱신 중단)
SVC_LINKED_PRODUCT_INFO = "C005"    # 바코드연계제품정보 (보조용, 마찬가지로 2018년 이후 갱신 중단)


async def _fetch(service_code: str, barcode: str) -> dict:
    """식품안전나라 API 호출 공통 함수"""
    url = f"{BASE_URL}/{settings.FOOD_SAFETY_API_KEY}/{service_code}/json/1/5/BRCD_NO={barcode}"
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.json()


def _extract_rows(raw: dict, service_code: str) -> list:
    """서비스별 응답 JSON에서 실제 데이터 행을 꺼낸다"""
    body = raw.get(service_code, {})
    header = body.get("RESULT", {})
    code = header.get("CODE", "")
    # INFO-000이 아니면 정상 데이터가 아님 (INFO-200: 결과 없음 등)
    if code and code != "INFO-000":
        return []
    return body.get("row", [])


async def lookup_barcode(barcode: str) -> dict:
    """
    바코드 번호로 제품 정보를 조회한다.
    * 주의: 정확한 응답 필드명(제품명/회사명이 어떤 키로 오는지)을
      문서에서 확인하지 못해, 지금은 원본 row를 그대로 반환한다.
      실제로 한 번 호출해본 뒤 나온 키 이름을 보고 필요한 필드만
      뽑아 쓰도록 다듬는 게 안전하다.
    """
    raw_i2570 = await _fetch(SVC_DISTRIBUTION_BARCODE, barcode)
    rows_i2570 = _extract_rows(raw_i2570, SVC_DISTRIBUTION_BARCODE)
    if rows_i2570:
        return {
            "found": True,
            "source": "유통바코드(I2570)",
            "raw": rows_i2570[0],
        }

    raw_c005 = await _fetch(SVC_LINKED_PRODUCT_INFO, barcode)
    rows_c005 = _extract_rows(raw_c005, SVC_LINKED_PRODUCT_INFO)
    if rows_c005:
        return {
            "found": True,
            "source": "바코드연계제품정보(C005, 2018년 이후 미갱신)",
            "raw": rows_c005[0],
        }

    return {"found": False, "barcode": barcode}
