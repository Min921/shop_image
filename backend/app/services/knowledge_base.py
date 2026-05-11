import json
from functools import lru_cache
from pathlib import Path

from backend.app.schemas import Product


DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "products.json"


@lru_cache(maxsize=1)
def load_products() -> list[Product]:
    with DATA_PATH.open("r", encoding="utf-8") as file:
        raw_products = json.load(file)
    return [Product(**item) for item in raw_products]

