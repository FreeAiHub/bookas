# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Автоматизация и маркетинговая инфраструктура для интернет-магазина **bookas.pt** (LUNADIL LDA, Португалия). WooCommerce + WordPress, 13 издательств, собственный каталог на promobooks.net.

## Рабочая директория

Всегда работай в `/Users/investing/Desktop/bookas/` — это корень проекта.

## Команды запуска

### Python (автоматизация)

```bash
# Установка зависимостей
pip install -r requirements.txt

# Синхронизация изображений товаров в WooCommerce
python image_sync.py
DRY_RUN=false python image_sync.py   # реальный запуск

# Публикация постов из очереди в Buffer
python buffer/schedule_posts.py
python buffer/schedule_posts.py --post-id 25
python buffer/schedule_posts.py --dry-run

# Аудит очереди Buffer
python buffer/status.py

# Генерация изображений для постов (AI: DALL-E, Gemini, GPT)
python content/generate_images.py
python content/generate_images.py --post-id 25
python content/generate_images.py --model gemini-3.1-flash-image
python content/generate_images.py --dry-run
python content/generate_images.py --force

# Поиск книги в WooCommerce по названию
python SMM/book_lookup.py "название книги"
```

### Dashboard (React+Vite)

```bash
cd dashboard/client
pnpm install
pnpm run dev    # локальная разработка
pnpm run build  # сборка в dist/public
```

## Структура папок

```text
bookas/
├── automation/          # Скрипты автоматизации (email, соцсети, синхронизация)
├── buffer/              # Buffer API: клиент, очередь постов, планировщик
│   ├── client.py        # GraphQL-клиент Buffer API
│   ├── schedule_posts.py# Публикация из posts_queue.json в Buffer
│   ├── posts_queue.json # Очередь постов (IG + FB)
│   ├── status.py        # Аудит состояния очереди
│   └── exports/         # CSV для ручного импорта в Buffer UI
├── content/             # Генерация контента
│   ├── generate_images.py  # AI-генерация изображений для постов
│   └── smm_briefs/      # Брифы кампаний + VISUAL_STYLE.md
├── SMM/                 # SMM-утилиты: book_lookup.py, qa_check.py
├── seo/                 # SEO: keyword_tracker.py, sitemap_checker.py
├── analytics/           # Аналитика: weekly_report.py
├── email/               # Email-маркетинг (E-goi)
├── dashboard/           # React+Vite дашборд → Netlify
├── images/              # Изображения товаров (ISBN_XXXXXXXXXX.jpg)
├── data_samples/        # Образцы данных (не реальные)
├── docs/                # Стратегия, календарь, согласования
├── logs/                # Логи скриптов (YYYY-MM-DD_script_name.log)
├── exports/             # CSV/JSON отчёты (YYYY-MM-DD_report_name.csv)
├── output/              # Сгенерированный контент и черновики
│   └── images/          # AI-изображения: output/images/CAMPAIGN/MODEL/post_N.jpg
├── woo_client.py        # Базовый клиент WooCommerce/WordPress API
├── image_sync.py        # Синхронизация изображений по ISBN
├── config_example.env   # Шаблон конфигурации
└── SMM_MASTER.md        # Стратегия SMM: расписание, хэштеги, стиль
```

Новые Python-скрипты → соответствующая подпапка. Реальный `.env` → корень, не коммитить.

## Технический стек

- **Python 3.11+**, `requests`, `python-dotenv`
- WooCommerce REST API v3: `{WC_BASE_URL}/wp-json/wc/v3/`
- WordPress REST API v2: `{WC_BASE_URL}/wp-json/wp/v2/`
- Buffer GraphQL API: `https://api.buffer.com/graphql`
- AI-генерация изображений: DALL-E 3 (OpenAI), Gemini 3.1 Flash (OpenRouter), GPT-Image

## Конфигурация (.env)

Все секреты в `.env` (не в git). Полный шаблон в `config_example.env`.

| Группа | Переменные |
| --- | --- |
| WooCommerce | `WC_BASE_URL`, `WC_CONSUMER_KEY`, `WC_CONSUMER_SECRET` |
| Buffer | `BUFFER_ACCESS_TOKEN`, `BUFFER_ORG_ID`, `BUFFER_CHANNEL_ID_IG`, `BUFFER_CHANNEL_ID_FB` |
| Изображения AI | `OPENROUTER_API_KEY`, `OPENAI_API_KEY`, `IMAGE_MODEL` |
| Google Drive | `GOOGLE_DRIVE_FOLDER_ID`, `GOOGLE_SERVICE_ACCOUNT_JSON` |
| E-goi | `E_GOI_API_KEY`, `E_GOI_LIST_ID` |
| Общее | `LOG_LEVEL`, `DRY_RUN`, `IMAGES_DIR` |

## Архитектура кода

- **`woo_client.py`** — базовый клиент API: `get_products()`, `upload_media()`, `update_product_images()`. Все скрипты WooCommerce импортируют его.
- **`buffer/client.py`** — GraphQL-клиент Buffer: `get_channels()`, `graphql()`. Переиспользуй для любых запросов к Buffer.
- **`buffer/schedule_posts.py`** — читает `posts_queue.json`, валидирует (blocked, плейсхолдеры `[X%]`, URL изображений), публикует через `createPost` mutation, записывает `buffer_id` обратно в JSON.
- **`content/generate_images.py`** — генерирует изображения по промптам из `posts_queue.json`. Несколько моделей, watermark через PIL, загрузка на Google Drive. Сохраняет в `output/images/CAMPAIGN/MODEL/`.

## Стиль кода

- Комментарии и логи — на русском
- Имена переменных/функций — на английском (snake_case)
- Всегда используй `DRY_RUN` для тестирования перед реальным запуском
- Логируй через `logging`, не через `print`

## Buffer — работа с очередью постов

Каждый пост в `buffer/posts_queue.json`:

```json
{
  "id": 25,
  "channel": "instagram",
  "status": "pending",
  "scheduled_at": "2026-04-20T18:30:00+00:00",
  "text": "Текст поста на португальском...",
  "image_url": "https://...",
  "notes": "описание для логов",
  "blocked": false
}
```

Статус `"done"` + `buffer_id` — пост уже в Buffer. `"pending"` — ждёт публикации. `blocked: true` — пропускается при публикации (ждёт данных от João).

Ручной импорт в Buffer UI: готовые CSV в `buffer/exports/` (формат: `"Text","Image URL","Tags","Posting Time"`).

## Автономные агенты (GitHub Actions)

Три workflow работают в облаке без компьютера:

| Workflow | Расписание | Что делает |
| --- | --- | --- |
| `buffer-autopublish.yml` | Каждый день 08:00 WEST | Публикует pending посты в Buffer, коммитит обновлённый JSON |
| `content-reminder.yml` | Каждый четверг 16:00 WEST | Создаёт GitHub Issue если есть заблокированные посты |
| `orchestrator-daily.yml` | Каждый день 07:30 WEST | Общий статус + Issue если есть срочные задачи |

### GitHub Secrets — ОБЯЗАТЕЛЬНО настроить

Перейти: `github.com/[REPO] → Settings → Secrets and variables → Actions → New secret`

| Secret | Значение (из .env) |
| --- | --- |
| `BUFFER_ACCESS_TOKEN` | значение `BUFFER_ACCESS_TOKEN` из `.env` |
| `BUFFER_ORG_ID` | `69c54f6211e07e49d3fd0e74` |
| `BUFFER_CHANNEL_ID_IG` | значение `BUFFER_CHANNEL_ID_IG` из `.env` |
| `BUFFER_CHANNEL_ID_FB` | значение `BUFFER_CHANNEL_ID_FB` из `.env` |

### Ручной запуск оркестратора (локально)

```bash
# Полный статус — что нужно сделать сейчас
python3 automation/orchestrator.py

# JSON-отчёт (для интеграций)
python3 automation/orchestrator.py --json

# Только срочное
python3 automation/orchestrator.py --urgent
```

## Деплой клиентского дашборда

```bash
# Стандартный путь — CI деплоит автоматически за ~60 сек
git add dashboard/client/src/data/
git commit -m "update: ..."
git push origin main

# Ручной деплой (срочно, без ожидания GitHub)
bash dashboard/deploy.sh
```

| Netlify | Значение |
| --- | --- |
| Токен | см. MY_SETUP.md |
| Site ID | `cbe786ff-e330-4e70-9aee-8979011e48ee` |
| Build command | `pnpm install && pnpm run build` |
| Publish dir | `dist/public` |
| Base dir | `dashboard` |
| NODE_VERSION | `20`, PNPM_VERSION `10` |

### Добавить задачу в дашборд

```json
// dashboard/client/src/data/tasks.json — добавить в массив items:
{ "id": 18, "gh": null, "category": "automation", "status": "pending", "priority": 1,
  "en": "Task description", "ua": "Опис", "pt": "Descrição" }
```

Статусы: `"ready"` | `"in_progress"` | `"pending"` | `"blocked"`

Категории: `"setup"` | `"content"` | `"automation"` | `"seo"` | `"campaigns"` | `"recurring"` | `"analytics"`

---

## SMM — Социальные сети

### Роли

- **Alex**: SMM, SEO, продажи, контент, автоматизация
- **João**: каталог, логистика, загрузка товаров (каждую пятницу), выбор Author/Theme of Month

### Платформы

- Instagram (primary) + Facebook (secondary) через Buffer
- Email: **E-goi** (португальская платформа, ~50 000 клиентов)

### Важные бизнес-правила

- Португальский закон **запрещает скидки на 1-ю покупку** → вместо скидки: **бесплатная книга из promobooks.net**
- Новые товары João загружает **по пятницам** → лучшие слоты постов: пятница–воскресенье
- Author/Theme of the Month — **João выбирает**, Alex делает баннеры и публикует
- Посты с `[X%]` или `[PRÉMIO]` — заблокированы, ждут данных от João

### Визуальный стиль изображений

Полные правила в `content/smm_briefs/VISUAL_STYLE.md`. Базовый промпт:

```text
flat lay editorial photography, cream linen background, soft natural daylight from left,
warm neutral tones, no text, no watermark, no logo, books as main element,
Portuguese bookstore aesthetic, cozy and inviting atmosphere
```

Форматы: 1:1 (1080×1080) для Feed, 9:16 для Stories/Reels. Никогда не добавлять текст на изображение.

### Ключевые документы

- `SMM_MASTER.md` — стратегия, расписание, хэштеги
- `content/smm_briefs/` — брифы кампаний (Páscoa, Dia do Livro, Liberdade, Dia da Mãe, Feira do Livro)
- `docs/content_plan_approval.md` — план для согласования с João

---

## Язык общения

Общайся со мной на **русском языке**.
