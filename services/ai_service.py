import base64
import json
import re
from typing import Optional, Type

from google import genai
from google.genai import types
from openai import AsyncOpenAI
from pydantic import BaseModel

from config import settings

openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


def _parse_ai_json(text: str) -> dict:
    """
    AI가 반환한 텍스트에서 JSON을 최대한 견고하게 파싱한다.
    - 앞뒤에 ```json ... ``` 코드블록이 붙어 있으면 벗겨낸다.
    - 그래도 실패하면, 첫 번째로 완결되는 JSON 객체만 추출한다
      (뒤에 설명 텍스트 등 "Extra data"가 붙어 있는 경우 대비).
    * 참고: response_schema를 지정하면 Gemini/OpenAI 모두 문법 자체가
      강제되므로 이 함수까지 올 일이 거의 없어지지만, 혹시 모를 경우를
      대비한 안전망으로 남겨둔다.
    """
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
        snippet = cleaned[:300]
        raise ValueError(f"AI 응답을 JSON으로 해석할 수 없습니다: {e}. 응답 일부: {snippet!r}") from e


async def call_ai_vision(
    prompt: str,
    base64_image: str,
    mime_type: str,
    provider: str = "gemini",
    schema: Optional[Type[BaseModel]] = None,
):
    """사진(영수증/포장지)을 보고 JSON을 반환하는 비전 AI.
    schema를 넘기면 그 Pydantic 모델 형태로 출력이 강제된다 (권장)."""
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
        # 기본값: Gemini (신규 google-genai SDK)
        client = genai.Client(api_key=settings.GEMINI_KEY_SCAN)
        image_part = types.Part.from_bytes(
            data=base64.b64decode(base64_image),
            mime_type=mime_type,
        )
        config_kwargs = {"response_mime_type": "application/json"}
        if schema:
            config_kwargs["response_schema"] = schema
        response = client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=[prompt, image_part],
            config=types.GenerateContentConfig(**config_kwargs),
        )
        return _parse_ai_json(response.text)


async def call_ai_text(
    prompt: str,
    provider: str = "gemini",
    schema: Optional[Type[BaseModel]] = None,
):
    """텍스트 기반 레시피 추천 AI.
    schema를 넘기면 그 Pydantic 모델 형태로 출력이 강제된다 (권장)."""
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
        client = genai.Client(api_key=settings.GEMINI_KEY_RECIPE)
        config_kwargs = {"response_mime_type": "application/json"}
        if schema:
            config_kwargs["response_schema"] = schema
        response = client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(**config_kwargs),
        )
        return _parse_ai_json(response.text)
