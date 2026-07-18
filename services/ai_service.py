import json
import re
from typing import Optional, Type

import google.generativeai as genai
from openai import AsyncOpenAI
from pydantic import BaseModel

from config import settings

openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


def _parse_ai_json(text: str) -> dict:
    cleaned = text.strip()
    fence_match = re.match(r"^```(?:json)?\s*(.*?)\s*```$", cleaned, re.DOTALL)
    if fence_match:
        cleaned = fence_match.group(1).strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass
    try:
        obj, _ = json.JSONDecoder().raw_decode(cleaned)
        return obj
    except json.JSONDecodeError as e:
        raise ValueError(f"AI 응답을 JSON으로 해석할 수 없습니다: {e}. 응답: {cleaned[:300]}") from e


async def call_ai_vision(
    prompt: str,
    base64_image: str,
    mime_type: str,
    provider: str = "gemini",
    schema: Optional[Type[BaseModel]] = None,
):
    """사진(영수증/포장지)을 보고 JSON을 반환하는 비전 AI."""
    if provider == "openai":
        response_format = (
            {
                "type": "json_schema",
                "json_schema": {"name": schema.__name__, "schema": schema.model_json_schema()},
            }
            if schema
            else {"type": "json_object"}
        )
        response = await openai_client.chat.completions.create(
            model=settings.OPENAI_MODEL_SCAN,
            response_format=response_format,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{base64_image}"}}
                ],
            }],
        )
        return _parse_ai_json(response.choices[0].message.content)
    else:
        # Gemini (google-generativeai SDK)
        genai.configure(api_key=settings.GEMINI_KEY_SCAN)
        model = genai.GenerativeModel(settings.GEMINI_MODEL)

        import base64 as b64
        image_data = b64.b64decode(base64_image)
        image_part = {"mime_type": mime_type, "data": image_data}

        full_prompt = prompt
        if schema:
            full_prompt += f"\n\n반드시 아래 JSON 스키마 형식으로만 답하라:\n{json.dumps(schema.model_json_schema(), ensure_ascii=False)}"

        response = model.generate_content(
            [full_prompt, image_part],
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json"
            )
        )
        return _parse_ai_json(response.text)


async def call_ai_text(
    prompt: str,
    provider: str = "gemini",
    schema: Optional[Type[BaseModel]] = None,
):
    """텍스트 기반 레시피 추천 AI."""
    if provider == "openai":
        response_format = (
            {
                "type": "json_schema",
                "json_schema": {"name": schema.__name__, "schema": schema.model_json_schema()},
            }
            if schema
            else {"type": "json_object"}
        )
        response = await openai_client.chat.completions.create(
            model=settings.OPENAI_MODEL_RECIPE,
            response_format=response_format,
            messages=[{"role": "user", "content": prompt}]
        )
        return _parse_ai_json(response.choices[0].message.content)
    else:
        # Gemini (google-generativeai SDK)
        genai.configure(api_key=settings.GEMINI_KEY_RECIPE)
        model = genai.GenerativeModel(settings.GEMINI_MODEL)

        full_prompt = prompt
        if schema:
            full_prompt += f"\n\n반드시 아래 JSON 스키마 형식으로만 답하라:\n{json.dumps(schema.model_json_schema(), ensure_ascii=False)}"

        response = model.generate_content(
            full_prompt,
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json"
            )
        )
        return _parse_ai_json(response.text)
