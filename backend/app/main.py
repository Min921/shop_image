from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from backend.app.schemas import AnalysisResult, Product
from backend.app.services.image_analyzer import analyze_image
from backend.app.services.knowledge_base import load_products
from backend.app.services.recommender import build_recommendation


app = FastAPI(title="商品图片分析与推荐系统", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/products", response_model=list[Product])
def products() -> list[Product]:
    return load_products()


@app.post("/api/analyze", response_model=AnalysisResult)
async def analyze(
    image: UploadFile | None = File(default=None),
    need: str | None = Form(default=""),
) -> AnalysisResult:
    image_bytes = await image.read() if image else None
    features = analyze_image(image_bytes)
    return build_recommendation(features, need)

