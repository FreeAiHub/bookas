# Bookas.pt — Claude Code Instructions

## Что это за проект
Автоматизация и маркетинговая инфраструктура для интернет-магазина **bookas.pt** (LUNADIL LDA, Португалия).
WooCommerce + WordPress, 13 издательств, собственный каталог на promobooks.net.

## Рабочая директория
Всегда работай в `/Users/investing/Desktop/bookas/` — это корень проекта.

## Структура папок и куда класть файлы

```
bookas/
├── automation/          # Скрипты автоматизации (email, соцсети, синхронизация)
├── seo/                 # SEO инструменты (ключевые слова, sitemap)
├── content/             # Генерация контента (блог, баннеры)
├── analytics/           # Аналитика и отчёты
├── images/              # Изображения для загрузки в WooCommerce (ISBN_XXXX.jpg)
├── data_samples/        # Примеры данных (JSON, CSV) — только образцы, не реальные
├── docs/                # Документация: стратегия, бюджет, календарь
├── logs/                # Логи выполнения скриптов (создаётся автоматически)
├── exports/             # Выгрузки данных: CSV, JSON отчёты (создаётся автоматически)
└── output/              # Сгенерированный контент: тексты, черновики (создаётся автоматически)
```

### Правила размещения файлов
- Новые скрипты Python → в соответствующую подпапку (`automation/`, `seo/`, `content/`, `analytics/`)
- Изображения товаров → `images/` (именование: `ISBN_XXXXXXXXXX.jpg`)
- Логи → `logs/` (именование: `YYYY-MM-DD_script_name.log`)
- Экспорты/отчёты → `exports/` (именование: `YYYY-MM-DD_report_name.csv`)
- Сгенерированный контент (тексты, черновики) → `output/`
- Конфигурационные примеры → корень проекта (например, `config_example.env`)
- Реальный `.env` → корень проекта, НЕ коммитить в git

## Технический стек
- **Python 3.11+**
- `requests` — HTTP запросы к WooCommerce/WordPress REST API
- `python-dotenv` — загрузка конфига из `.env`
- WooCommerce REST API v3: `{WC_BASE_URL}/wp-json/wc/v3/`
- WordPress REST API v2: `{WC_BASE_URL}/wp-json/wp/v2/`

## Конфигурация (.env)
Все секреты хранятся в `.env` (не в git). Пример в `config_example.env`.

Ключевые переменные:
- `WC_BASE_URL` — URL магазина (https://bookas.pt)
- `WC_CONSUMER_KEY` / `WC_CONSUMER_SECRET` — ключи WooCommerce API
- `IMAGES_DIR` — папка с изображениями (по умолчанию `./images`)
- `LOG_LEVEL` — уровень логирования (INFO / DEBUG)
- `DRY_RUN` — тестовый режим без реальных изменений (true/false)

## Архитектура кода
- `woo_client.py` — базовый клиент для WooCommerce/WordPress API (переиспользуй его)
- `image_sync.py` — синхронизация изображений по ISBN
- Новые модули импортируют `woo_client` для API запросов

## Стиль кода
- Комментарии и логи — на русском
- Имена переменных/функций — на английском (snake_case)
- Всегда используй `DRY_RUN` режим для тестирования перед реальным запуском
- Логируй через `logging`, не через `print`

## Деплой клиентского дашборда

Дашборд находится в `dashboard/` — React+Vite приложение, деплоится на Netlify.

### Стандартный рабочий процесс (обновление данных)

```bash
# 1. Редактируй только JSON файлы — код не трогай
nano dashboard/client/src/data/tasks.json   # или любой другой файл

# 2. Коммит + пуш — Netlify деплоит автоматически за ~60 сек
git add dashboard/client/src/data/
git commit -m "update: ..."
git push origin main
```

### Ручной деплой (если нужно срочно, не ждать GitHub)

```bash
bash dashboard/deploy.sh
```

### Учётные данные Netlify

| Параметр | Значение |
|---|---|
| **Netlify токен** | см. MY_SETUP.md (не хранить в git) |
| **SITE_ID** | Заполнить в `dashboard/deploy.sh` после первого деплоя через UI |
| **Base directory** | `dashboard` |
| **Build command** | `pnpm install && pnpm run build` |
| **Publish dir** | `dist/public` |
| **NODE_VERSION** | `20` |
| **PNPM_VERSION** | `10` |

### Добавить новую задачу в дашборд

Добавить объект в конец массива `items` в `dashboard/client/src/data/tasks.json`:

```json
{ "id": 18, "gh": null, "category": "automation", "status": "pending", "priority": 1,
  "en": "Task description in English",
  "ua": "Опис завдання українською",
  "pt": "Descrição da tarefa em português" }
```

Статусы: `"ready"` | `"in_progress"` | `"pending"` | `"blocked"`
Категории: `"setup"` | `"content"` | `"automation"` | `"seo"` | `"campaigns"` | `"recurring"` | `"analytics"`

### Первоначальная настройка Netlify (один раз)

1. app.netlify.com → "Add new site" → "Import from GitHub"
2. Репо: `FreeAiHub/bookas`
3. Base directory: `dashboard`
4. Build command: `pnpm install && pnpm run build`
5. Publish directory: `dist/public`
6. Env vars: `NODE_VERSION=20`, `PNPM_VERSION=10`
7. После деплоя: скопировать Site ID → вставить в `dashboard/deploy.sh`

---

## Язык общения
Общайся со мной на **русском языке**.
