# 📚 Bookas.pt — Digital Marketing & Automation System

> **EN** | [PT](#pt-version)

A full-stack digital marketing and automation platform built for **Bookas.pt** — a Portuguese online bookstore operated by LUNADIL LDA, distributing books from 13 exclusive publishers plus its own high-margin catalog at [promobooks.net](http://promobooks.net).

---

## 🎯 Project Overview

This repository contains all automation scripts, SEO tools, content pipelines, and marketing infrastructure powering the Bookas.pt growth engine.

| Layer | Stack | Status |
|-------|-------|--------|
| E-commerce | WooCommerce + WordPress | ✅ Live |
| Email Marketing | Brevo / E-goi | ✅ Active |
| SEO | Rank Math Pro + Search Console | 🔄 Setup |
| Content AI | Claude API + custom pipelines | 🔄 In Progress |
| Social Automation | OpenClaw-style agents | 🔜 Planned |
| Analytics | Weekly reporting scripts | 🔜 Planned |

---

## 🏗️ Repository Structure

```
bookas/
├── 📁 automation/           # Core automation scripts
│   ├── image_sync.py        # ✅ WooCommerce image sync by ISBN
│   ├── social_post_gen.py   # 🔜 Auto social posts from new releases
│   └── email_campaign.py    # 🔜 Brevo API campaign automation
│
├── 📁 seo/                  # SEO tooling
│   ├── keyword_tracker.py   # Track target keywords (PT market)
│   └── sitemap_checker.py   # Sitemap health monitoring
│
├── 📁 content/              # Content generation pipelines
│   ├── blog_generator.py    # Claude API → Portuguese blog articles
│   └── banner_specs.md      # Monthly banner specs & guidelines
│
├── 📁 analytics/            # Reporting
│   └── weekly_report.py     # Automated weekly performance report
│
├── 📁 docs/                 # Strategy & documentation
│   ├── STRATEGY.md          # Full marketing strategy 2026
│   ├── CALENDAR_2026.md     # Content calendar Mar–Dec 2026
│   └── BUDGET.md            # Tools & budget breakdown
│
├── 📁 data_samples/         # Sample API responses & test data
├── 📁 images/               # Local book cover storage (ISBN-based)
├── image_sync.py            # ✅ Entry point (WooCommerce image sync)
├── woo_client.py            # ✅ WooCommerce/WordPress API client
├── config_example.env       # Environment variables template
├── requirements.txt         # Python dependencies
└── README.md
```

---

## ✅ Module 1 — WooCommerce Image Sync (Live)

Automatically syncs book cover images to WooCommerce products by ISBN.

**How it works:**
1. Reads all products from WooCommerce API
2. Extracts ISBN from product meta or SKU
3. Looks up local `images/{ISBN}.jpg`
4. Uploads to WordPress media library
5. Assigns as product featured image

### Quick Start

```bash
# Clone & setup
git clone https://github.com/FreeAiHub/bookas.git
cd bookas
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Configure
cp config_example.env .env
# Fill in: WC_BASE_URL, WC_CONSUMER_KEY, WC_CONSUMER_SECRET

# Dry run (safe — no changes to site)
DRY_RUN=true MAX_PRODUCTS=5 python image_sync.py

# Full sync
python image_sync.py
```

### Environment Variables

```env
WC_BASE_URL=https://bookas.pt
WC_CONSUMER_KEY=ck_xxxxxxxxxxxx
WC_CONSUMER_SECRET=cs_xxxxxxxxxxxx
DRY_RUN=false
MAX_PRODUCTS=500
```

---

## 🗓️ Marketing Calendar 2026

Key campaigns tracked and automated through this system:

| Month | Campaign | Type |
|-------|----------|------|
| March | Dia da Mulher (Mar 8) · Dia da Poesia (Mar 21) | Email + Social |
| April | **Dia Mundial do Livro (Apr 23)** · Dia da Liberdade (Apr 25) | MAIN EVENT |
| May | **Dia da Mãe** — gift guide + email 2 weeks before | Email + Blog |
| June | Dia da Criança · Dia de Portugal · **Dia do Pai** · Summer reads | Multi-channel |
| Jul–Aug | Summer reading challenge · Back-to-school prep | Blog + Social |
| September | **Regresso às Aulas** — school lists + parent emails | Email + Social |
| October | Nobel Prize Literature · Halloween horror list | Blog + Email |
| November | **⚡ Black Friday** — site-wide promo, countdown | BIGGEST EVENT |
| December | Christmas rush (Dec 1–20) · Year-end sale | Full campaign |

---

## 🤖 AI & Automation Stack

| Tool | Purpose | Status |
|------|---------|--------|
| Claude Pro / API | Blog articles, social posts, email copy (PT) | ✅ Active |
| Brevo / E-goi | Email campaigns — weekly Tuesday sends | ✅ Active |
| OpenClaw agents | Auto social posts from new release Excel | 🔜 Planned |
| Rank Math Pro | WordPress SEO, schema, meta management | 🔄 Setup |
| Google Merchant | Product feed for Google Shopping | 🔜 Month 2 |
| Scraping proxies | Market research & competitor monitoring | 🔄 Testing |

---

## 📊 Weekly Operations Rhythm

```
Monday    → Plan week content based on John's Friday Excel
Tuesday   → Send email campaign (Brevo/E-goi) — top 3–5 new releases
Thursday  → 3–5 social posts (Instagram + Facebook)
Friday    → Receive new releases Excel from John
Friday    → Performance report → traffic, sales, pre-orders
28th/mo   → All next month's banners ready (Author + Theme of Month)
```

---

## 💰 Monthly Tools Budget (~€250)

| Tool | Cost |
|------|------|
| Claude Pro | €20 |
| Rank Math Pro | €7 |
| Link building tests | €80 |
| WordPress extensions | €40 |
| Scraping proxies | €50 |
| LLM APIs (OpenAI / Anthropic) | €30 |
| Misc SaaS tests | €23 |
| **Total** | **~€250** |

---

## 🚀 Roadmap

- [x] WooCommerce image sync by ISBN
- [x] WooCommerce API client module
- [ ] Blog article generator (Claude API → PT)
- [ ] Social post automation from Excel releases
- [ ] Brevo campaign automation script
- [ ] Weekly performance report generator
- [ ] SEO keyword tracker (PT market)
- [ ] Google Merchant Center product feed
- [ ] Pre-order monitoring dashboard

---

## 🤝 Contributing

This is a private operational repository for Bookas.pt / LUNADIL LDA.  
Built and maintained by **Alex** (Digital Marketing) in collaboration with **João** (Operations & Catalog).

---

<a name="pt-version"></a>

---

# 📚 Bookas.pt — Sistema de Marketing Digital & Automação

> **PT** | [EN](#top)

Plataforma de marketing digital e automação construída para a **Bookas.pt** — livraria online portuguesa operada pela LUNADIL LDA, distribuidora de livros de 13 editoras exclusivas e do catálogo próprio [promobooks.net](http://promobooks.net).

---

## 🎯 Visão Geral

Este repositório contém scripts de automação, ferramentas de SEO, pipelines de conteúdo e toda a infraestrutura de marketing que alimenta o crescimento da Bookas.pt.

### O que automatizamos

- **Sincronização de imagens** — capas de livros associadas a produtos WooCommerce por ISBN
- **Geração de conteúdo** — artigos de blog e posts para redes sociais em português via Claude API
- **Campanhas de email** — integração com Brevo/E-goi para envios semanais de terça-feira
- **Relatórios** — relatório semanal automático de desempenho (tráfego, vendas, pré-encomendas)
- **SEO** — monitorização de palavras-chave e saúde do sitemap

---

## ⚡ Início Rápido

```bash
git clone https://github.com/FreeAiHub/bookas.git
cd bookas
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp config_example.env .env
# Preenche as variáveis de ambiente
python image_sync.py
```

---

## 📬 Contacto

**Bookas.pt** — [bookas.pt](https://bookas.pt)  
**Catálogo próprio** — [promobooks.net](https://promobooks.net)

---

*Built with Python · WooCommerce API · Claude AI · Brevo · Rank Math*
