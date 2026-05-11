from pydantic import BaseModel, Field


class VisualFeatures(BaseModel):
    primary_color: str = Field(description="Dominant color name")
    color_hex: str
    brightness: str
    saturation: str
    style_tags: list[str]


class ProductMatch(BaseModel):
    id: str
    name: str
    category: str
    score: float
    reason: str


class AnalysisResult(BaseModel):
    category: str
    confidence: float
    visual_features: VisualFeatures
    selling_points: list[str]
    suitable_scenarios: list[str]
    purchase_advice: list[str]
    comparison: list[str]
    recommendations: list[ProductMatch]
    summary: str


class Product(BaseModel):
    id: str
    name: str
    category: str
    colors: list[str]
    styles: list[str]
    features: list[str]
    scenarios: list[str]
    price_level: str

