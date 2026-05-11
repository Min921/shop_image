from backend.app.schemas import AnalysisResult, ProductMatch, VisualFeatures
from backend.app.services.image_analyzer import ImageFeatures
from backend.app.services.knowledge_base import load_products


CATEGORY_KEYWORDS = {
    "服饰": ["衣", "穿搭", "外套", "裤", "裙", "鞋", "包", "通勤", "约会"],
    "数码": ["手机", "耳机", "电脑", "相机", "智能", "续航", "办公", "游戏"],
    "家居": ["家", "卧室", "客厅", "收纳", "厨房", "灯", "桌", "椅"],
    "美妆": ["护肤", "口红", "彩妆", "香水", "面霜", "敏感肌"],
    "运动": ["运动", "健身", "跑步", "户外", "训练", "瑜伽"],
}


def build_recommendation(features: ImageFeatures, need: str | None) -> AnalysisResult:
    user_need = (need or "").strip()
    category, confidence = _infer_category(user_need)
    matched_products = _match_products(category, features, user_need)

    selling_points = _selling_points(category, features, user_need)
    scenarios = _scenarios(category, user_need)
    advice = _purchase_advice(category, features, user_need)
    comparison = _comparison(category, matched_products)

    visual_features = VisualFeatures(
        primary_color=features.primary_color,
        color_hex=features.color_hex,
        brightness=features.brightness,
        saturation=features.saturation,
        style_tags=features.style_tags,
    )

    summary = (
        f"系统识别该商品偏向「{category}」类目，主色为{features.primary_color}，"
        f"整体呈现{', '.join(features.style_tags)}的视觉印象。"
    )
    if user_need:
        summary += f" 结合你的需求「{user_need}」，推荐重点关注适用场景、材质/参数和价格区间。"

    return AnalysisResult(
        category=category,
        confidence=confidence,
        visual_features=visual_features,
        selling_points=selling_points,
        suitable_scenarios=scenarios,
        purchase_advice=advice,
        comparison=comparison,
        recommendations=matched_products,
        summary=summary,
    )


def _infer_category(need: str) -> tuple[str, float]:
    if not need:
        return "通用商品", 0.56

    scores = {
        category: sum(1 for keyword in keywords if keyword in need)
        for category, keywords in CATEGORY_KEYWORDS.items()
    }
    best_category, best_score = max(scores.items(), key=lambda item: item[1])
    if best_score == 0:
        return "通用商品", 0.58
    return best_category, min(0.72 + best_score * 0.08, 0.96)


def _match_products(category: str, features: ImageFeatures, need: str) -> list[ProductMatch]:
    products = load_products()
    scored: list[ProductMatch] = []
    need_tokens = set(need)

    for product in products:
        score = 0.0
        if category == product.category:
            score += 3
        if features.primary_color in product.colors:
            score += 1.4
        score += len(set(product.styles).intersection(features.style_tags)) * 0.8
        text_pool = "".join(product.features + product.scenarios + [product.name])
        score += sum(0.2 for token in need_tokens if token in text_pool)

        reason = f"匹配{product.category}类目"
        if features.primary_color in product.colors:
            reason += f"，并包含{features.primary_color}配色"
        if product.scenarios:
            reason += f"，适合{product.scenarios[0]}"

        scored.append(
            ProductMatch(
                id=product.id,
                name=product.name,
                category=product.category,
                score=round(score, 2),
                reason=reason,
            )
        )

    return sorted(scored, key=lambda item: item.score, reverse=True)[:3]


def _selling_points(category: str, features: ImageFeatures, need: str) -> list[str]:
    points = [
        f"{features.primary_color}主色带来{', '.join(features.style_tags[:2])}的第一印象",
        "可结合商品标题、参数和评论进一步验证材质、尺寸与真实体验",
    ]
    if category != "通用商品":
        points.insert(0, f"需求语义更接近{category}类商品，推荐结果会优先考虑该类目的核心指标")
    if need:
        points.append("推荐理由已结合用户输入需求，适合做个性化筛选")
    return points


def _scenarios(category: str, need: str) -> list[str]:
    default = {
        "服饰": ["日常通勤", "周末出行", "轻商务搭配"],
        "数码": ["移动办公", "学习娱乐", "差旅携带"],
        "家居": ["小户型布置", "租房改造", "家庭日常使用"],
        "美妆": ["日常妆容", "通勤补妆", "礼物赠送"],
        "运动": ["日常训练", "户外活动", "健身房使用"],
    }
    scenarios = default.get(category, ["日常使用", "礼物选择", "性价比筛选"])
    if "送" in need or "礼物" in need:
        return ["礼物赠送", *scenarios[:2]]
    return scenarios


def _purchase_advice(category: str, features: ImageFeatures, need: str) -> list[str]:
    advice = [
        "优先查看实拍图和用户评价，确认颜色与图片识别结果是否一致",
        "对比同价位商品的核心参数，避免只被外观吸引",
    ]
    if category == "服饰":
        advice.append("重点确认尺码、面料、版型和退换政策")
    elif category == "数码":
        advice.append("重点确认续航、接口、保修和真实性能评价")
    elif category == "家居":
        advice.append("重点确认尺寸、安装方式、承重和清洁维护成本")
    elif category == "美妆":
        advice.append("重点确认肤质适配、成分、色号和过敏风险")
    elif category == "运动":
        advice.append("重点确认支撑性、透气性、耐磨性和使用强度")
    if features.brightness == "偏暗":
        advice.append("图片整体偏暗，建议查看更多光线条件下的商品图")
    return advice


def _comparison(category: str, matches: list[ProductMatch]) -> list[str]:
    if not matches:
        return ["当前商品库样本较少，建议补充更多商品后再做横向比较"]
    best = matches[0]
    return [
        f"与知识库商品相比，当前结果最接近「{best.name}」",
        f"同类{category}商品可从价格、场景、核心参数和评价稳定性四个角度对比",
        "若多个候选商品分数接近，建议优先选择售后明确且评价数量更多的商品",
    ]

