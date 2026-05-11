from dataclasses import dataclass
from io import BytesIO

from PIL import Image, ImageStat


COLOR_NAMES = [
    ("黑色", (28, 28, 28)),
    ("白色", (235, 235, 235)),
    ("灰色", (128, 128, 128)),
    ("红色", (210, 55, 55)),
    ("粉色", (230, 135, 165)),
    ("橙色", (230, 135, 45)),
    ("黄色", (230, 205, 70)),
    ("绿色", (80, 160, 95)),
    ("蓝色", (70, 120, 210)),
    ("紫色", (140, 90, 190)),
    ("棕色", (135, 90, 55)),
]


@dataclass
class ImageFeatures:
    primary_color: str
    color_hex: str
    brightness: str
    saturation: str
    style_tags: list[str]


def analyze_image(image_bytes: bytes | None) -> ImageFeatures:
    if not image_bytes:
        return ImageFeatures(
            primary_color="未知",
            color_hex="#9aa0a6",
            brightness="未知",
            saturation="未知",
            style_tags=["待上传图片", "文本需求优先"],
        )

    image = Image.open(BytesIO(image_bytes)).convert("RGB")
    image.thumbnail((256, 256))

    stat = ImageStat.Stat(image)
    avg = tuple(int(channel) for channel in stat.mean)
    primary_color = _nearest_color(avg)
    color_hex = "#{:02x}{:02x}{:02x}".format(*avg)

    brightness_value = sum(avg) / 3
    brightness = "明亮" if brightness_value >= 180 else "中等亮度" if brightness_value >= 90 else "偏暗"

    saturation_value = _estimate_saturation(avg)
    saturation = "高饱和" if saturation_value >= 0.45 else "中饱和" if saturation_value >= 0.2 else "低饱和"

    tags = _style_tags(primary_color, brightness, saturation)
    return ImageFeatures(
        primary_color=primary_color,
        color_hex=color_hex,
        brightness=brightness,
        saturation=saturation,
        style_tags=tags,
    )


def _nearest_color(rgb: tuple[int, int, int]) -> str:
    def distance(item: tuple[str, tuple[int, int, int]]) -> int:
        _, color = item
        return sum((rgb[index] - color[index]) ** 2 for index in range(3))

    return min(COLOR_NAMES, key=distance)[0]


def _estimate_saturation(rgb: tuple[int, int, int]) -> float:
    high = max(rgb) / 255
    low = min(rgb) / 255
    if high == 0:
        return 0
    return (high - low) / high


def _style_tags(color: str, brightness: str, saturation: str) -> list[str]:
    tags: list[str] = []
    if color in {"黑色", "白色", "灰色"}:
        tags.append("简约百搭")
    if color in {"红色", "橙色", "黄色", "粉色"}:
        tags.append("醒目活力")
    if color in {"蓝色", "绿色"}:
        tags.append("清爽自然")
    if color in {"棕色", "紫色"}:
        tags.append("质感风格")
    if brightness == "明亮":
        tags.append("轻盈明亮")
    if saturation == "低饱和":
        tags.append("低调耐看")
    if not tags:
        tags.append("日常实用")
    return tags

