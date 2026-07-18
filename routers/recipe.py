from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from services.ai_service import call_ai_text
from schemas import RecipeRecommendation

router = APIRouter(prefix="/recipe", tags=["Recipe"])

class RecipeRequest(BaseModel):
    provider: str = "gemini"
    ingredients: List[dict]

@router.post("/recommend")
async def recommend_recipe(req: RecipeRequest):
    try:
        prompt = f"""냉장고 재료 목록: {req.ingredients}
daysLeft(남은 일수)가 임박한 재료를 최우선으로 사용하는 레시피 2~3개를 아래 JSON으로 추천하라.
{{"recipes":[{{"title":"요리명","usesUrgent":["사용된 임박재료"],"ingredients":["재료명-분량"],"steps":["1단계","2단계"]}}]}}"""
        
        result = await call_ai_text(prompt, req.provider, schema=RecipeRecommendation)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))