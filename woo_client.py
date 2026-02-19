"""
Модуль для работы с WooCommerce и WordPress REST API.
Использует Basic Auth с consumer key/secret.
"""

import logging
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


def _get_config():
    """Загружает конфигурацию из переменных окружения."""
    import os

    base_url = os.getenv("WC_BASE_URL", "").rstrip("/")
    key = os.getenv("WC_CONSUMER_KEY", "")
    secret = os.getenv("WC_CONSUMER_SECRET", "")
    return base_url, key, secret


def _session():
    """Создаёт сессию requests с Basic Auth."""
    base_url, key, secret = _get_config()
    if not all([base_url, key, secret]):
        raise ValueError(
            "Задайте WC_BASE_URL, WC_CONSUMER_KEY и WC_CONSUMER_SECRET в .env"
        )
    auth = (key, secret)
    session = requests.Session()
    session.auth = auth
    session.headers["Content-Type"] = "application/json"
    return session, base_url


def get_products(page: int = 1, per_page: int = 20) -> list[dict]:
    """
    GET /wp-json/wc/v3/products с пагинацией.
    Возвращает список товаров.
    """
    session, base_url = _session()
    url = f"{base_url}/wp-json/wc/v3/products"
    params = {"page": page, "per_page": per_page}
    resp = session.get(url, params=params, timeout=30)
    if resp.status_code != 200:
        logger.error(
            "get_products: status=%s body=%s",
            resp.status_code,
            resp.text[:500],
        )
        resp.raise_for_status()
    return resp.json()


def upload_media(image_path: str) -> int:
    """
    POST /wp-json/wp/v2/media — загрузка файла в медиатеку.
    Возвращает media_id.
    """
    path = Path(image_path)
    if not path.exists():
        raise FileNotFoundError(f"Файл не найден: {image_path}")

    session, base_url = _session()
    url = f"{base_url}/wp-json/wp/v2/media"
    mime = "image/jpeg" if path.suffix.lower() in (".jpg", ".jpeg") else "image/png"
    with open(path, "rb") as f:
        files = {"file": (path.name, f, mime)}
        resp = session.post(url, files=files, timeout=60)
    if resp.status_code not in (200, 201):
        logger.error(
            "upload_media: status=%s body=%s",
            resp.status_code,
            resp.text[:500],
        )
        resp.raise_for_status()
    result = resp.json()
    return result.get("id", 0)


def update_product_images(product_id: int, image_ids: list[int]) -> None:
    """
    PUT /wp-json/wc/v3/products/{id} — обновление изображений товара.
    image_ids — список media_id (первый — основное изображение).
    """
    session, base_url = _session()
    url = f"{base_url}/wp-json/wc/v3/products/{product_id}"
    payload = {"images": [{"id": mid} for mid in image_ids]}
    resp = session.put(url, json=payload, timeout=30)
    if resp.status_code != 200:
        logger.error(
            "update_product_images: status=%s body=%s",
            resp.status_code,
            resp.text[:500],
        )
        resp.raise_for_status()
