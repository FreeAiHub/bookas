# bookas: инструменты для WooCommerce португальского книжного магазина

Два рабочих скрипта на Python: один привязывает обложки книг к товарам WooCommerce по
ISBN, второй собирает отчёт по очереди контента. Остальное в репозитории это брифы,
календари и заглушки.

## Статус

Синхронизация изображений работает, запускалась на живом каталоге. Последний коммит
2026-08-17. Открыто 16 issue, почти все про кампании и контент, а не про код.

## Что уже работает

### Синхронизация изображений WooCommerce

Скрипт обходит каталог товаров, определяет ISBN товара, ищет локальный файл
`images/<ISBN>.jpg` или `.png`, загружает его в медиатеку WordPress и ставит изображением
товара. Подтверждение: `image_sync.py`.

- ISBN берётся по порядку: `global_unique_id` → ключи `meta_data`, содержащие «isbn» →
  названия атрибутов, содержащие «isbn» → числовой SKU. Подтверждение: функция
  `extract_isbn()` в `image_sync.py`.
- Товары, у которых изображения уже есть, пропускаются; товары без локального файла тоже.
  Подтверждение: цикл `run_sync()` в `image_sync.py`.
- `DRY_RUN=true` пишет в лог, что было бы сделано, и ничего не меняет. Подтверждение:
  ветка `DRY_RUN` в `image_sync.py`.
- `MAX_PRODUCTS` ограничивает число обработанных товаров за запуск, `WC_PER_PAGE` задаёт
  размер страницы. Подтверждение: константы в начале `image_sync.py`.
- Клиент API использует Basic auth с consumer key и secret и работает с тремя эндпоинтами:
  `GET /wp-json/wc/v3/products`, `POST /wp-json/wp/v2/media`,
  `PUT /wp-json/wc/v3/products/{id}`. Подтверждение: `woo_client.py`.

### Отчёт по очереди контента

`automation/orchestrator.py` читает `buffer/posts_queue.json` и выводит итоги очереди,
посты на ближайшие семь дней, приближающиеся дедлайны, предупреждения и список
существующих месячных планов. Три режима: текстовый отчёт, `--json` для внешних систем и
`--urgent` выводит только то, что требует внимания. Подтверждение: `automation/orchestrator.py`,
`buffer/posts_queue.json`.

### Отчёты по расписанию

Четыре workflow в GitHub Actions работают по расписанию. Подтверждение:
`.github/workflows/`.

| Workflow | Расписание | Что делает |
|---|---|---|
| `deploy-dashboard.yml` | пуш в `dashboard/**` | собирает дашборд и публикует его на Netlify |
| `orchestrator-daily.yml` | ежедневно 06:30 UTC | запускает оркестратор и публикует сводку |
| `buffer-autopublish.yml` | ежедневно 07:00 UTC | публикует очередь через Buffer, есть вход `dry_run` |
| `content-reminder.yml` | четверг 15:00 UTC | проверяет заблокированные посты и уведомляет |

### Дашборд

Одностраничное приложение на React 19 + Vite + TypeScript в каталоге `dashboard/`,
публикуется на Netlify. Подтверждение: `dashboard/package.json`, `dashboard/netlify.toml`,
`dashboard/client/src/App.tsx`.

## Быстрый старт

Синхронизация изображений:

```bash
git clone https://github.com/FreeAiHub/bookas.git
cd bookas
python -m venv .venv
source .venv/bin/activate           # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp config_example.env .env          # заполнить WC_BASE_URL, WC_CONSUMER_KEY, WC_CONSUMER_SECRET
DRY_RUN=true MAX_PRODUCTS=5 python image_sync.py
python image_sync.py                # полный запуск
```

Подтверждение: `requirements.txt` (`requests`, `python-dotenv`), `config_example.env` и
переменные окружения, которые читает `image_sync.py`.

Обложки нужно положить в `images/` заранее, с именем `<ISBN>.jpg` или `<ISBN>.png`. В
репозитории в этом каталоге лежит только `.gitkeep`.

Отчёт по очереди:

```bash
python automation/orchestrator.py           # полный текстовый отчёт
python automation/orchestrator.py --json    # JSON для внешних систем
python automation/orchestrator.py --urgent  # только то, что требует внимания
```

Подтверждение: блок `__main__` в `automation/orchestrator.py`.

Дашборд:

```bash
cd dashboard
pnpm install
pnpm dev
```

Подтверждение: `dashboard/package.json`.

## Как это устроено

```
image_sync.py            обход каталога, извлечение ISBN, DRY_RUN, лимиты
woo_client.py            WooCommerce v3 + медиатека WordPress по Basic auth
images/<ISBN>.jpg        локальные обложки, в git не попадают

automation/
  orchestrator.py        читает buffer/posts_queue.json → отчёт / --json / --urgent
buffer/posts_queue.json  сама очередь: канал, статус, время публикации по каждому посту
content/smm_briefs/      семь брифов с текстами и обоснованием
docs/CALENDAR_2026.md    календарь кампаний с датами и дедлайнами
dashboard/               React-приложение, которое показывает план, публикуется на Netlify
```

## Чего пока нет

Шесть файлов это заглушки: комментарий и `# TODO: implement`.

- `content/blog_generator.py` (85 байт)
- `automation/social_post_gen.py` (103 байта)
- `automation/email_campaign.py` (70 байт)
- `seo/keyword_tracker.py` (79 байт)
- `seo/sitemap_checker.py` (43 байта)
- `analytics/weekly_report.py` (44 байта)

То есть генерации статей, генерации постов, обращений к API Brevo или E-goi, отслеживания
ключевых слов, проверки sitemap и автоматического отчёта по эффективности в коде нет.
В прошлой версии README часть из этого была указана как работающая.

`docs/STRATEGY.md` и `docs/BUDGET.md` существуют, но пустые, поэтому стратегия и бюджет на
инструменты в репозитории не описаны.

`automation/orchestrator.py` использует только стандартную библиотеку, а
`.github/workflows/*.yml` выполняет `pip install -r requirements.txt`, где перечислены
`requests` и `python-dotenv`. Workflow ставит больше, чем нужно оркестратору.

Тестов, линтера и файла `LICENSE` нет. Дашборд объявляет MIT в своём `package.json`;
на Python-скрипты лицензия не распространяется.

## Участие

Это рабочий репозиторий одного магазина. Issues это бэклог кампаний и контента, а не
публичный roadmap.

## Контакты

bookas.pt, promobooks.net.
