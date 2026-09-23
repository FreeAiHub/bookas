# bookas: WooCommerce maintenance tooling for a Portuguese online bookstore

Two working Python tools: one attaches book cover images to WooCommerce products by ISBN,
the other reports on a queued content calendar. The rest of the repository is briefs,
schedules and stubs.

## Status

The image sync works and has been run against a live catalogue. Last commit 2026-08-17.
16 issues are open, most of them campaigns and content tasks rather than code.

## What works

### WooCommerce image sync

Walks the product catalogue, works out each product's ISBN, finds `images/<ISBN>.jpg` or
`.png` locally, uploads it to the WordPress media library and sets it as the product image.
Confirmation: `image_sync.py`.

- ISBN is read from `global_unique_id`, then `meta_data` keys containing "isbn", then
  attribute names containing "isbn", then a numeric SKU. Confirmation: `extract_isbn()` in
  `image_sync.py`.
- Products that already have images are skipped, as are products with no local file.
  Confirmation: the `run_sync()` loop in `image_sync.py`.
- `DRY_RUN=true` logs what it would do and writes nothing. Confirmation: the `DRY_RUN` branch
  in `image_sync.py`.
- `MAX_PRODUCTS` caps how many products are handled in a run, `WC_PER_PAGE` sets page size.
  Confirmation: constants at the top of `image_sync.py`.
- The API client uses Basic auth with a consumer key and secret and covers three endpoints:
  `GET /wp-json/wc/v3/products`, `POST /wp-json/wp/v2/media`,
  `PUT /wp-json/wc/v3/products/{id}`. Confirmation: `woo_client.py`.

### Content queue report

`automation/orchestrator.py` reads `buffer/posts_queue.json` and reports queue totals,
posts scheduled in the next seven days, upcoming deadlines, alerts, and which monthly
content plans exist. Three output modes: a text report, `--json` for other systems, and
`--urgent` which prints only the alerts that need attention. Confirmation:
`automation/orchestrator.py`, `buffer/posts_queue.json`.

### Scheduled reports

Four GitHub Actions workflows run on a schedule. Confirmation: `.github/workflows/`.

| Workflow | Schedule | What it does |
|---|---|---|
| `deploy-dashboard.yml` | push to `dashboard/**` | builds the dashboard and deploys it to Netlify |
| `orchestrator-daily.yml` | daily 06:30 UTC | runs the orchestrator and publishes its summary |
| `buffer-autopublish.yml` | daily 07:00 UTC | publishes the queue through Buffer, with a `dry_run` input |
| `content-reminder.yml` | Thursdays 15:00 UTC | checks blocked posts and notifies |

### Dashboard

A React 19 + Vite + TypeScript single-page app under `dashboard/`, deployed to Netlify.
Confirmation: `dashboard/package.json`, `dashboard/netlify.toml`, `dashboard/client/src/App.tsx`.

## Quick start

Image sync:

```bash
git clone https://github.com/FreeAiHub/bookas.git
cd bookas
python -m venv .venv
source .venv/bin/activate           # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp config_example.env .env          # fill in WC_BASE_URL, WC_CONSUMER_KEY, WC_CONSUMER_SECRET
DRY_RUN=true MAX_PRODUCTS=5 python image_sync.py
python image_sync.py                # full run
```

Confirmed against `requirements.txt` (`requests`, `python-dotenv`), `config_example.env` and
the environment variables read in `image_sync.py`.

Put the covers in `images/` first, named `<ISBN>.jpg` or `<ISBN>.png`. That directory holds
only a `.gitkeep` in this repository.

Queue report:

```bash
python automation/orchestrator.py           # full text report
python automation/orchestrator.py --json    # JSON for other systems
python automation/orchestrator.py --urgent  # only what needs attention
```

Confirmed against the `__main__` block in `automation/orchestrator.py`.

Dashboard:

```bash
cd dashboard
pnpm install
pnpm dev
```

Confirmed against `dashboard/package.json`.

## How it is arranged

```
image_sync.py            catalogue walk, ISBN extraction, DRY_RUN, limits
woo_client.py            WooCommerce v3 + WordPress media over Basic auth
images/<ISBN>.jpg        local covers, not committed

automation/
  orchestrator.py        reads buffer/posts_queue.json → report / --json / --urgent
buffer/posts_queue.json  the queue itself, with per-post channel, status, schedule
content/smm_briefs/      seven briefs with the copy and the reasoning behind it
docs/CALENDAR_2026.md    campaign calendar with dates and deadlines
dashboard/               React app that renders the plan, deployed to Netlify
```

## What is not here yet

Six files are placeholders that contain a comment and `# TODO: implement`:

- `content/blog_generator.py` (85 bytes)
- `automation/social_post_gen.py` (103 bytes)
- `automation/email_campaign.py` (70 bytes)
- `seo/keyword_tracker.py` (79 bytes)
- `seo/sitemap_checker.py` (43 bytes)
- `analytics/weekly_report.py` (44 bytes)

So there is no blog generation, no social post generation, no Brevo or E-goi API call, no
keyword tracking, no sitemap check and no automated performance report in code. The earlier
README listed several of these as active.

`docs/STRATEGY.md` and `docs/BUDGET.md` exist but are empty, so the strategy and the tool
budget are not documented in the repository.

`automation/orchestrator.py` imports only the standard library while
`.github/workflows/*.yml` runs `pip install -r requirements.txt`, which lists `requests` and
`python-dotenv`. The workflows install more than the orchestrator needs.

No tests, no linter, no `LICENSE` file. The dashboard declares MIT in its own
`package.json`; nothing covers the Python tools.

## Contributing

This is a working repository for one store. Issues are the campaign and content backlog,
not a public roadmap.

## Contact

bookas.pt, promobooks.net.
