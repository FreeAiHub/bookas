"""
Скрипт синхронизации изображений товаров WooCommerce по ISBN.
Ищет картинки в локальной папке images/{ISBN}.jpg и прикрепляет к товарам.
"""

import logging
import os
from pathlib import Path

from dotenv import load_dotenv

from woo_client import get_products, update_product_images, upload_media

load_dotenv()

# Настройка логирования
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

IMAGES_DIR = Path(os.getenv("IMAGES_DIR", "./images"))
DRY_RUN = os.getenv("DRY_RUN", "false").lower() in ("true", "1", "yes")
MAX_PRODUCTS = int(os.getenv("MAX_PRODUCTS", "0"))  # 0 = без лимита
WC_PER_PAGE = int(os.getenv("WC_PER_PAGE", "20"))


def test_connection() -> bool:
    """
    Тестовый GET товаров (per_page=1).
    Печатает статус и краткое резюме. Возвращает True при успехе.
    """
    try:
        products = get_products(page=1, per_page=1)
        if not products:
            logger.info("Соединение OK. Товаров на первой странице: 0")
            return True
        p = products[0]
        logger.info(
            "Соединение OK. Товар: id=%s name=%s",
            p.get("id"),
            (p.get("name") or "")[:50],
        )
        return True
    except Exception as e:
        logger.error("Ошибка соединения: %s", e)
        return False


def extract_isbn(product: dict) -> str | None:
    """
    Извлекает ISBN из товара.
    Проверяет global_unique_id, meta_data (ключи isbn, ISBN, _isbn), атрибуты, sku.
    """
    # global_unique_id — часто совпадает с ISBN-13
    gid = product.get("global_unique_id")
    if gid and isinstance(gid, str) and gid.strip():
        return gid.strip()

    # meta_data
    for meta in product.get("meta_data") or []:
        key = (meta.get("key") or "").lower()
        if "isbn" in key:
            val = meta.get("value")
            if val and isinstance(val, str) and val.strip():
                return val.strip()

    # attributes
    for attr in product.get("attributes") or []:
        name = (attr.get("name") or "").lower()
        if "isbn" in name:
            options = attr.get("options") or []
            if options and options[0]:
                return str(options[0]).strip()

    # sku иногда совпадает с ISBN
    sku = product.get("sku")
    if sku and isinstance(sku, str) and sku.strip().replace("-", "").isdigit():
        return sku.strip()

    return None


def image_path_for_isbn(isbn: str) -> Path | None:
    """Возвращает путь к картинке по ISBN или None, если файла нет."""
    path = IMAGES_DIR / f"{isbn}.jpg"
    if path.exists():
        return path
    path_png = IMAGES_DIR / f"{isbn}.png"
    if path_png.exists():
        return path_png
    return None


def run_sync() -> None:
    """Основной цикл: обход товаров, привязка ISBN → картинка, обновление."""
    if not test_connection():
        logger.error("Тест соединения не пройден. Выход.")
        return

    processed = 0
    page = 1
    while True:
        products = get_products(page=page, per_page=WC_PER_PAGE)
        if not products:
            break

        for p in products:
            if MAX_PRODUCTS and processed >= MAX_PRODUCTS:
                logger.info("Достигнут лимит MAX_PRODUCTS=%s", MAX_PRODUCTS)
                return

            pid = p.get("id")
            name = (p.get("name") or "")[:40]

            isbn = extract_isbn(p)
            if not isbn:
                logger.debug("Пропуск id=%s (%s): ISBN не найден", pid, name)
                continue

            images = p.get("images") or []
            if images:
                logger.debug("Пропуск id=%s (%s): уже есть изображения", pid, name)
                continue

            img_path = image_path_for_isbn(isbn)
            if not img_path:
                logger.debug("Пропуск id=%s (%s): нет файла %s", pid, name, isbn)
                continue

            if DRY_RUN:
                logger.info(
                    "[DRY RUN] id=%s (%s) ISBN=%s -> %s",
                    pid,
                    name,
                    isbn,
                    img_path,
                )
                processed += 1
                continue

            try:
                media_id = upload_media(str(img_path))
                update_product_images(pid, [media_id])
                logger.info("OK id=%s (%s) ISBN=%s media_id=%s", pid, name, isbn, media_id)
                processed += 1
            except Exception as e:
                logger.error("Ошибка id=%s (%s): %s", pid, name, e)

        page += 1


if __name__ == "__main__":
    run_sync()
