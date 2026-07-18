from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # DB 및 서버 설정
    DATABASE_URL: str = "sqlite:///./fridge.db"
    ALLOWED_ORIGINS: str = "*"

    # Gemini API 설정
    GEMINI_KEY_SCAN: str = ""
    GEMINI_KEY_RECIPE: str = ""
    GEMINI_MODEL: str = "gemini-2.5-flash"   # ← 수정: 3.5 → 2.5

    # OpenAI API 설정 (선택)
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL_SCAN: str = "gpt-4o"
    OPENAI_MODEL_RECIPE: str = "gpt-4o-mini"

    # 식품안전나라 바코드 API
    FOOD_SAFETY_API_KEY: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

settings = Settings()
