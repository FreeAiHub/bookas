"""
Оркестратор Bookas — главный координатор всех задач.

Запуск:
  python automation/orchestrator.py           # полный отчёт
  python automation/orchestrator.py --json    # JSON для внешних систем
  python automation/orchestrator.py --urgent  # только срочное (для Todoist)
"""

import json
import sys
import os
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).parent.parent
QUEUE_FILE = ROOT / "buffer" / "posts_queue.json"
BRIEFS_DIR = ROOT / "content" / "smm_briefs"

# Временная зона Португалии (WEST/UTC+1 летом, UTC+0 зимой)
# Используем UTC для простоты — Buffer сам конвертирует
NOW = datetime.now(timezone.utc)
TODAY = NOW.date()


def load_queue() -> list:
    if not QUEUE_FILE.exists():
        return []
    return json.loads(QUEUE_FILE.read_text(encoding="utf-8"))


def analyze_queue(posts: list) -> dict:
    """Анализирует очередь и возвращает сводку статусов."""
    done = [p for p in posts if p.get("status") == "done"]
    pending = [p for p in posts if p.get("status") == "pending" and not p.get("blocked")]
    blocked = [p for p in posts if p.get("blocked")]

    # Посты, которые должны выйти в следующие 7 дней
    upcoming = []
    for p in done:
        try:
            dt = datetime.fromisoformat(p["scheduled_at"].replace("Z", "+00:00"))
            if 0 <= (dt.date() - TODAY).days <= 7:
                upcoming.append(p)
        except (KeyError, ValueError):
            pass

    # Ближайший заблокированный пост (нужны данные от João)
    blocked_urgent = []
    for p in blocked:
        try:
            dt = datetime.fromisoformat(p["scheduled_at"].replace("Z", "+00:00"))
            days_until = (dt.date() - TODAY).days
            if days_until <= 5:
                p["_days_until"] = days_until
                blocked_urgent.append(p)
        except (KeyError, ValueError):
            pass

    return {
        "total": len(posts),
        "done": len(done),
        "pending": len(pending),
        "blocked": len(blocked),
        "upcoming_7d": upcoming,
        "blocked_urgent": blocked_urgent,
    }


def check_monthly_plan() -> dict:
    """Проверяет наличие плана на текущий и следующий месяц."""
    current_month = NOW.strftime("%m")
    next_month = (NOW.replace(day=1) + timedelta(days=32)).strftime("%m")
    months = {
        "01": "janeiro", "02": "fevereiro", "03": "marco",
        "04": "abril",   "05": "maio",       "06": "junho",
        "07": "julho",   "08": "agosto",     "09": "setembro",
        "10": "outubro", "11": "novembro",   "12": "dezembro",
    }

    status = {}
    for month_num, month_name in [(current_month, months[current_month]),
                                   (next_month, months[next_month])]:
        # Ищем файл плана: NN_monthname_YYYY_MASTER.md
        year = NOW.year if month_num >= current_month else NOW.year + 1
        pattern = f"{month_num}_{month_name}{year}_MASTER.md"
        found = list(BRIEFS_DIR.glob(f"*{month_name}*"))
        status[month_name] = len(found) > 0

    return status


def build_report(verbose: bool = True) -> dict:
    posts = load_queue()
    queue_stats = analyze_queue(posts)
    monthly = check_monthly_plan()

    # Определяем уровень тревоги
    alerts = []

    if queue_stats["pending"] > 0:
        alerts.append({
            "level": "warn",
            "action": "publish",
            "message": f"⚡ {queue_stats['pending']} постов ждут публикации в Buffer",
            "command": "python buffer/schedule_posts.py",
        })

    for p in queue_stats["blocked_urgent"]:
        days = p.get("_days_until", "?")
        alerts.append({
            "level": "urgent",
            "action": "fill_template",
            "message": f"🔒 Пост #{p['id']} через {days} д. — нужен список от João ({p.get('notes','')[:60]})",
            "command": f"Получить список новинок от João → заполнить пост #{p['id']}",
        })

    current_m = NOW.strftime("%m")
    months_map = {"01":"janeiro","02":"fevereiro","03":"marco","04":"abril","05":"maio","06":"junho",
                  "07":"julho","08":"agosto","09":"setembro","10":"outubro","11":"novembro","12":"dezembro"}
    next_m_date = (NOW.replace(day=1) + timedelta(days=32))
    next_m_name = months_map[next_m_date.strftime("%m")]

    if not monthly.get(next_m_name):
        alerts.append({
            "level": "plan",
            "action": "create_plan",
            "message": f"📅 Нет плана на {next_m_name.capitalize()} {next_m_date.year}",
            "command": f"Создать content/smm_briefs/{next_m_date.strftime('%m')}_{next_m_name}{next_m_date.year}_MASTER.md",
        })

    return {
        "timestamp": NOW.isoformat(),
        "today": str(TODAY),
        "queue": queue_stats,
        "monthly_plans": monthly,
        "alerts": alerts,
        "summary": {
            "urgent_count": sum(1 for a in alerts if a["level"] == "urgent"),
            "warn_count": sum(1 for a in alerts if a["level"] == "warn"),
            "all_good": len(alerts) == 0,
        },
    }


def print_report(report: dict):
    print(f"\n{'='*60}")
    print(f"  BOOKAS ORCHESTRATOR — {report['today']}")
    print(f"{'='*60}")

    q = report["queue"]
    print(f"\n📊 ОЧЕРЕДЬ ПОСТОВ")
    print(f"  Всего: {q['total']} | Готово: {q['done']} | Pending: {q['pending']} | Блок: {q['blocked']}")

    if q["upcoming_7d"]:
        print(f"\n📅 БЛИЖАЙШИЕ 7 ДНЕЙ (уже в Buffer):")
        for p in q["upcoming_7d"]:
            dt = datetime.fromisoformat(p["scheduled_at"].replace("Z", "+00:00"))
            print(f"  {dt.strftime('%d.%m %H:%M')} [{p['channel'][:2].upper()}] {p.get('notes','')[:55]}")

    alerts = report["alerts"]
    if not alerts:
        print(f"\n✅ Всё в порядке — никаких срочных задач.")
    else:
        print(f"\n🚨 ТРЕБУЕТ ВНИМАНИЯ ({len(alerts)} задач):")
        for a in alerts:
            print(f"\n  [{a['level'].upper()}] {a['message']}")
            print(f"  → {a['command']}")

    plans = report["monthly_plans"]
    print(f"\n📋 КОНТЕНТ-ПЛАНЫ:")
    for month, exists in plans.items():
        icon = "✅" if exists else "❌"
        print(f"  {icon} {month.capitalize()}")

    print(f"\n{'='*60}\n")


if __name__ == "__main__":
    report = build_report()

    if "--json" in sys.argv:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    elif "--urgent" in sys.argv:
        for a in report["alerts"]:
            if a["level"] in ("urgent", "warn"):
                print(a["message"])
    else:
        print_report(report)
