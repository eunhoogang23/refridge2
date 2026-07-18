# 냉장고 파먹기 도우미

FastAPI 백엔드 + HTML 프론트엔드 | Render 배포용

---

## Render 배포 방법 (5단계)

### 1단계: GitHub에 올리기
```bash
git init
git add .
git commit -m "init: 냉장고 파먹기 도우미"
git remote add origin https://github.com/YOUR_ID/fridge-app.git
git push -u origin main
```
> ⚠️ `.env` 파일은 `.gitignore`에 포함되어 있어 자동으로 제외돼요.

### 2단계: Render에서 PostgreSQL DB 만들기
1. [render.com](https://render.com) → New → PostgreSQL
2. 이름: `fridge-db`, 플랜: Free
3. 생성 후 **Internal Database URL** 복사해두기

### 3단계: Render에서 웹 서비스 만들기
1. New → Web Service
2. GitHub 레포 연결
3. 설정:
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### 4단계: 환경 변수 설정 (Render Dashboard → Environment)
| Key | Value |
|-----|-------|
| `DATABASE_URL` | PostgreSQL Internal URL (2단계에서 복사한 것) |
| `GEMINI_KEY_SCAN` | Gemini API 키 (바코드·영수증용) |
| `GEMINI_KEY_RECIPE` | Gemini API 키 (레시피용) |
| `GEMINI_MODEL` | `gemini-2.5-flash` |
| `ALLOWED_ORIGINS` | `*` (또는 실제 도메인) |

> Gemini API 키는 [Google AI Studio](https://aistudio.google.com/app/apikey)에서 무료 발급

### 5단계: 배포 완료 후 접속
- 백엔드 API: `https://your-app.onrender.com/`
- 프론트엔드: `https://your-app.onrender.com/app`
- API 문서: `https://your-app.onrender.com/docs`

---

## 로컬 개발 방법

```bash
# 1. 패키지 설치
pip install -r requirements.txt

# 2. 환경 변수 설정
cp .env.example .env
# .env 파일 열어서 실제 값 입력

# 3. 서버 실행
uvicorn main:app --reload --port 8000

# 4. 브라우저에서 열기
# http://localhost:8000/app  ← 프론트엔드
# http://localhost:8000/docs ← API 문서
```

> 로컬에서 SQLite 쓰려면 `.env`의 `DATABASE_URL`을 `sqlite:///./fridge.db`로 유지하면 됨.

---

## 파일 구조

```
fridge-app/
├── main.py              # FastAPI 앱 + 스케줄러
├── config.py            # 환경 변수 설정
├── database.py          # DB 연결
├── models.py            # SQLAlchemy 모델
├── schemas.py           # Pydantic 스키마
├── routers/
│   ├── items.py         # 재료 CRUD
│   ├── scan.py          # 바코드·영수증 AI 스캔
│   └── recipe.py        # 레시피 추천
├── services/
│   ├── ai_service.py    # Gemini/OpenAI 호출
│   └── barcode_service.py # 식품안전나라 API
├── frontend/
│   └── fridge-app.html  # 프론트엔드 (단일 HTML)
├── render.yaml          # Render 자동 배포 설정
├── Procfile             # 서버 시작 명령
├── requirements.txt     # Python 패키지
└── .env.example         # 환경 변수 예시
```
