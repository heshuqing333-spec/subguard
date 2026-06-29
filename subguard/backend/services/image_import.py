from io import BytesIO
from os import environ
from pathlib import Path
from shutil import which

from services.text_import import parse_bill_text

from PIL import ImageOps


def parse_bill_image(file_storage):
    try:
        from PIL import Image
        import pytesseract
    except ImportError as exc:
        raise RuntimeError("图片识别需要安装 Pillow 和 pytesseract 依赖。") from exc

    configure_tesseract(pytesseract)

    try:
        image = Image.open(BytesIO(file_storage.read()))
        raw_text = run_ocr_variants(image, pytesseract)
    except pytesseract.TesseractNotFoundError as exc:
        raise RuntimeError("未找到 Tesseract OCR，请先在电脑上安装 Tesseract 并配置 PATH。") from exc
    except Exception as exc:
        raise ValueError("图片读取或 OCR 识别失败，请换一张清晰截图再试。") from exc

    raw_text = raw_text.strip()
    if not raw_text:
        raise ValueError("未从图片中识别到文字，请上传更清晰的账单截图。")

    subscription = parse_bill_text(raw_text)
    return {
        "raw_text": raw_text,
        "subscription": subscription,
    }


def configure_tesseract(pytesseract):
    configured = environ.get("TESSERACT_CMD")
    candidates = [
        configured,
        which("tesseract"),
        r"D:\software\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    ]

    for candidate in candidates:
        if candidate and Path(candidate).exists():
            pytesseract.pytesseract.tesseract_cmd = candidate
            return


def run_ocr_variants(image, pytesseract):
    gray = ImageOps.autocontrast(ImageOps.grayscale(image))
    variants = [
        gray,
        gray.resize((image.width * 2, image.height * 2)),
        crop_amount_area(gray),
    ]

    texts = []
    for variant in variants:
        texts.append(pytesseract.image_to_string(variant, lang="chi_sim+eng", config="--psm 6"))

    return "\n".join(text for text in texts if text.strip())


def crop_amount_area(image):
    width, height = image.size
    top = int(height * 0.09)
    bottom = int(height * 0.28)
    crop = image.crop((0, top, width, bottom))
    return crop.resize((width * 2, 1000))
