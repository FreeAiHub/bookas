# Примеры данных WooCommerce

## product_example.json

Полный пример товара из API `wc/v3/products`.

**Важные поля для синхронизации изображений:**

| Поле | Описание |
|------|----------|
| `global_unique_id` | ISBN-13 (например `9789893380246`) — используется для поиска картинки `images/{ISBN}.jpg` |
| `images` | Массив прикреплённых изображений. Если не пустой — товар пропускается |
| `meta_data` | Дополнительные мета-поля (ISBN может быть в ключах `isbn`, `ISBN` и т.п.) |
| `attributes` | Атрибуты товара (Autor, Editora, Ano de Edição) |
| `sku` | Артикул, иногда совпадает с ISBN |

Скрипт `image_sync.py` ищет ISBN в порядке: `global_unique_id` → `meta_data` → `attributes` → `sku`.
