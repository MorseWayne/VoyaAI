"""
Parse flight/train ticket screenshots: OCR first to get text, then LLM parses text only.
Avoids using vision LLM for lower cost and faster response.
"""
import base64
import io
import json
import logging
import re
from pathlib import Path
from typing import Any

from services.llm_factory import create_client
from config import get_settings

logger = logging.getLogger(__name__)
PROMPTS_DIR = Path(__file__).parent.parent / "prompts"

# OCR: 轻量方案 rapidocr_onnxruntime（ONNX 推理，无 PyTorch，体积小）
try:
    from rapidocr_onnxruntime import RapidOCR
    from PIL import Image
    _OCR_AVAILABLE = True
except ImportError:
    _OCR_AVAILABLE = False
    RapidOCR = None
    Image = None

_ocr_engine = None


def _get_ocr_engine():
    """Lazy init RapidOCR (first run may download ONNX models)."""
    global _ocr_engine
    if _ocr_engine is None and _OCR_AVAILABLE:
        _ocr_engine = RapidOCR()
    return _ocr_engine


def _load_prompt_vision() -> str:
    """Prompt for vision LLM (fallback when OCR unavailable or returns empty)."""
    p = PROMPTS_DIR / "ticket_extract.txt"
    if p.exists():
        return p.read_text(encoding="utf-8")
    return "识别图片中的机票或火车票信息，仅返回一个 JSON 对象，包含 type(flight/train), origin_name, destination_name, departure_time, arrival_time, flight_no 或 train_no, seat_info。"


def _load_prompt_text() -> str:
    """Prompt for text-only LLM (after OCR)."""
    p = PROMPTS_DIR / "ticket_extract_from_text.txt"
    if p.exists():
        return p.read_text(encoding="utf-8")
    return (
        "根据下面从票据截图中 OCR 得到的文字，提取机票或火车票信息，仅返回一个 JSON 对象。"
        "格式：机票 type=flight 含 flight_no；火车 type=train 含 train_no。"
        "时间格式 YYYY-MM-DD HH:MM。无法识别的字段用空字符串。只输出一行 JSON。\n\n"
    )


def _image_base64_to_bytes(image_base64: str) -> bytes:
    """Strip optional data URL prefix and decode base64 to bytes."""
    raw = image_base64.strip()
    if raw.startswith("data:"):
        # data:image/png;base64,xxxx
        raw = raw.split(",", 1)[-1]
    return base64.b64decode(raw)


def ocr_image_to_text(image_base64: str) -> str:
    """
    Run OCR on a ticket screenshot (base64) and return extracted text.
    Uses RapidOCR (ONNX, lightweight, no PyTorch). Returns empty string if unavailable or fails.
    """
    if not _OCR_AVAILABLE:
        logger.warning("OCR not available (rapidocr_onnxruntime/PIL not installed), will use vision LLM")
        return ""
    try:
        engine = _get_ocr_engine()
        if engine is None:
            return ""
        img_bytes = _image_base64_to_bytes(image_base64)
        # RapidOCR 支持 bytes / path / ndarray；传 bytes 即可
        result, _ = engine(img_bytes)
        if not result:
            return ""
        # result: list of [box, text, score]
        lines = [item[1] for item in result]
        return "\n".join(lines).strip() if lines else ""
    except Exception as e:
        logger.warning(f"OCR failed: {e}")
        return ""


async def _parse_ticket_with_vision(image_base64: str) -> dict[str, Any]:
    """Fallback: use vision LLM to parse image (original behavior)."""
    if not image_base64.strip().startswith("data:"):
        image_base64 = "data:image/png;base64," + image_base64.strip()
    prompt = _load_prompt_vision()
    settings = get_settings()
    client = create_client()
    content = [
        {"type": "text", "text": prompt},
        {"type": "image_url", "image_url": {"url": image_base64}},
    ]
    response = await client.chat.completions.create(
        model=settings.llm_model,
        messages=[{"role": "user", "content": content}],
        timeout=120,
    )
    raw = (response.choices[0].message.content or "").strip()
    return _parse_json_from_llm(raw)


def _parse_json_from_llm(raw: str) -> dict[str, Any]:
    """Extract JSON object from LLM output (may be wrapped in markdown)."""
    json_str = raw
    m = re.search(r"\{[\s\S]*\}", raw)
    if m:
        json_str = m.group(0)
    data = json.loads(json_str)
    if not isinstance(data, dict):
        return {"type": "unknown", "error": "返回格式无效"}
    return data


async def _parse_ticket_from_text(ocr_text: str) -> dict[str, Any]:
    """Use text-only LLM to parse OCR result into structured ticket data."""
    prompt_template = _load_prompt_text()
    user_content = prompt_template + "\n\n" + (ocr_text or "(无文字)")
    settings = get_settings()
    client = create_client()
    response = await client.chat.completions.create(
        model=settings.llm_model,
        messages=[{"role": "user", "content": user_content}],
        timeout=60,
    )
    raw = (response.choices[0].message.content or "").strip()
    return _parse_json_from_llm(raw)


async def parse_ticket_image(image_base64: str) -> dict[str, Any]:
    """
    Parse a ticket screenshot (base64): first OCR to text, then LLM parses text only.
    Falls back to vision LLM if OCR is unavailable or returns too little text.
    """
    ocr_text = ocr_image_to_text(image_base64)

    # Prefer OCR + text LLM when we have meaningful text
    if ocr_text and len(ocr_text.strip()) >= 10:
        try:
            result = await _parse_ticket_from_text(ocr_text)
            if result.get("type") not in ("unknown", None):
                return result
            # type=unknown from LLM, fallback to vision
        except (json.JSONDecodeError, Exception) as e:
            logger.warning(f"Parse ticket from OCR text failed: {e}, fallback to vision")

    # Fallback: vision LLM (no OCR, or OCR empty, or text parse failed)
    try:
        return await _parse_ticket_with_vision(image_base64)
    except json.JSONDecodeError as e:
        logger.warning(f"Ticket parse JSON error: {e}")
        return {"type": "unknown", "error": "解析结果不是有效 JSON"}
    except Exception as e:
        logger.exception(f"Ticket parse failed: {e}")
        return {"type": "unknown", "error": str(e)}
