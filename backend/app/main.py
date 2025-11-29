from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.router import api_router

app = FastAPI(
    title="やどぺら API",
    description="小規模宿泊施設向けAI多言語自動案内システム",
    version="0.3.0",
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {
        "message": "やどぺら API v0.3",
        "status": "ok"
    }


@app.get("/health")
def health_check():
    return {"status": "ok"}


# APIルーター登録
app.include_router(api_router, prefix="/api/v1")

