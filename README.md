# Bookas — синхронизация изображений WooCommerce

Скрипт для привязки обложек книг к товарам WooCommerce по ISBN. Ищет картинки в локальной папке `images/{ISBN}.jpg` и загружает их в медиатеку WordPress.

## Установка

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Настройка

1. Скопируй `config_example.env` в `.env`
2. Заполни `WC_BASE_URL`, `WC_CONSUMER_KEY`, `WC_CONSUMER_SECRET`

## Запуск

```bash
python image_sync.py
```

**Тестовый режим (без изменений на сайте):**
```bash
DRY_RUN=true MAX_PRODUCTS=5 python image_sync.py
```

## Структура

- `woo_client.py` — работа с WooCommerce/WordPress API
- `image_sync.py` — логика обхода товаров, извлечение ISBN, загрузка картинок
- `images/` — локальные картинки по шаблону `{ISBN}.jpg` или `{ISBN}.png`
- `data_samples/` — примеры данных API
