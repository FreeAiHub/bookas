#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Публикация очереди bookas.pt в Buffer через GraphQL API.

Скрипт, который был удалён из репозитория и который винил за собой ежедневное
падение воркфлоу. Пишется заново под ТЕКУЩИЙ API Buffer: старый REST
api.bufferapp.com/1/ объявлен легаси, сейчас это GraphQL на api.buffer.com
с заголовком `Authorization: Bearer <ключ>`.

Главное правило безопасности: пост с незаполненными заглушками не уходит
НИКОГДА. В очереди полно шаблонов вида `[TÍTULO] — [AUTOR]`, и такой текст,
попавший в публичный Instagram, не исправить задним числом.

Переменные окружения:
    BUFFER_API_KEY          ключ из https://publish.buffer.com/settings/api
    BUFFER_ORG_ID           id организации (для проверки, что каналы наши)
    BUFFER_CHANNEL_ID_IG    id канала Instagram
    BUFFER_CHANNEL_ID_FB    id канала Facebook
    DRY_RUN                 'true' — только показать, что будет отправлено
    STALE_DAYS              просроченные старше N дней не публиковать (по умолч. 3)

Запуск:
    python3 schedule_posts.py                  # боевой
    DRY_RUN=true python3 schedule_posts.py     # сухой прогон, сети не касается
"""

import json
import os
import re
import sys
from datetime import datetime, timezone, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
QUEUE = os.path.join(HERE, "posts_queue.json")
API_URL = "https://api.buffer.com"

# Заглушки, которые нельзя выпускать в свет. Список — от самых частых.
PLACEHOLDERS = ("[TÍTULO]", "[TITULO]", "[AUTOR]", "[TÍTULOS]", "[LINK]", "[PREÇO]", "[TEMA]")

CHANNEL_ENV = {
    "instagram": "BUFFER_CHANNEL_ID_IG",
    "facebook": "BUFFER_CHANNEL_ID_FB",
}

DRY_RUN = os.environ.get("DRY_RUN", "false").strip().lower() in ("1", "true", "yes")
STALE_DAYS = int(os.environ.get("STALE_DAYS", "3"))


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def placeholders_in(text: str) -> list[str]:
    return [p for p in PLACEHOLDERS if p in (text or "")]


def select_posts(posts: list, now: datetime) -> tuple[list, list]:
    """Отбирает посты к публикации. Возвращает (готово, отклонено с причиной)."""
    ready, skipped = [], []
    stale_before = now - timedelta(days=STALE_DAYS)

    for post in posts:
        pid = post.get("id")
        subject = post.get("notes") or post.get("text", "")[:40]

        if post.get("status") == "done":
            continue  # уже опубликован — не ошибка

        if post.get("blocked") or post.get("status") == "blocked":
            skipped.append((pid, subject, "заблокирован: ждёт списка от João"))
            continue

        if post.get("status") != "pending":
            skipped.append((pid, subject, f"статус {post.get('status')!r}, не публикуем"))
            continue

        if post.get("joao_required"):
            skipped.append((pid, subject, "требует данных от João"))
            continue

        found = placeholders_in(post.get("text", ""))
        if found:
            skipped.append((pid, subject, f"заглушки не заполнены: {', '.join(found)}"))
            continue

        if not post.get("text", "").strip():
            skipped.append((pid, subject, "пустой текст"))
            continue

        channel = (post.get("channel") or "").lower()
        if channel not in CHANNEL_ENV:
            skipped.append((pid, subject, f"неизвестный канал {channel!r}"))
            continue

        try:
            due = datetime.fromisoformat(post["scheduled_at"].replace("Z", "+00:00"))
        except (KeyError, ValueError):
            skipped.append((pid, subject, "нет разбираемой даты scheduled_at"))
            continue

        if due > now:
            skipped.append((pid, subject, f"срок ещё не наступил ({due:%d.%m %H:%M} UTC)"))
            continue

        if due < stale_before:
            days = (now - due).days
            skipped.append((pid, subject, f"просрочен на {days} дн. — в свет не выпускаем"))
            continue

        ready.append(post)

    return ready, skipped


CREATE_POST = """
mutation CreatePost($input: CreatePostInput!) {
  createPost(input: $input) {
    ... on PostActionSuccess { post { id } }
    ... on MutationError { message }
  }
}
"""


def publish(post: dict, api_key: str, channels: dict) -> str:
    channel_id = channels[(post.get("channel") or "").lower()]
    due = datetime.fromisoformat(post["scheduled_at"].replace("Z", "+00:00"))
    data = graphql(api_key, CREATE_POST, variables={
        "input": {
            "text": post["text"],
            "channelId": channel_id,
            "schedulingType": "automatic",
            "mode": "customScheduled",
            "dueAt": due.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z"),
        }
    })
    result = data.get("createPost") or {}
    if result.get("message"):
        raise RuntimeError(result["message"])
    return (result.get("post") or {}).get("id", "")


def graphql(api_key: str, query: str, variables: dict | None = None) -> dict:
    import requests

    response = requests.post(
        API_URL,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        json={"query": query, "variables": variables or {}},
        timeout=30,
    )
    response.raise_for_status()
    payload = response.json()
    if "errors" in payload:
        raise RuntimeError(f"GraphQL вернул ошибку: {payload['errors']}")
    return payload.get("data", {})


def main() -> None:
    queue_path = os.environ.get("QUEUE_PATH", QUEUE)
    if not os.path.exists(queue_path):
        sys.exit(f"Очередь не найдена: {queue_path}")

    with open(queue_path, encoding="utf-8") as fh:
        queue = json.load(fh)
    posts = queue if isinstance(queue, list) else queue.get("posts", [])

    now = now_utc()
    ready, skipped = select_posts(posts, now)

    print(f"Очередь: {queue_path}")
    print(f"Всего постов: {len(posts)}   к публикации: {len(ready)}   отклонено: {len(skipped)}")

    if skipped:
        print("\nОтклонено (и это правильно):")
        for pid, subject, reason in skipped:
            print(f"  #{pid}  {reason}\n        {subject[:70]}")

    if not ready:
        print("\nПубликовать нечего.")
        return

    print("\nГотово к публикации:")
    for post in ready:
        print(f"  #{post['id']}  {post.get('channel')}  {post['scheduled_at'][:16]}")

    if DRY_RUN:
        print("\nСУХОЙ ПРОГОН: сеть не трогается, очередь не меняется.")
        print("Боевой запуск: уберите DRY_RUN=true.")
        return

    api_key = os.environ.get("BUFFER_API_KEY", "").strip()
    if not api_key:
        sys.exit("Нет BUFFER_API_KEY. Возьмите на https://publish.buffer.com/settings/api")

    channels = {
        name: os.environ.get(var, "").strip()
        for name, var in CHANNEL_ENV.items()
    }
    missing = [n for n, v in channels.items() if not v]
    if missing:
        sys.exit(f"Не заданы каналы: {', '.join(missing)}")

    published = 0
    for post in ready:
        try:
            post["buffer_id"] = publish(post, api_key, channels)
            post["status"] = "done"
            post.pop("blocked", None)
            published += 1
            print(f"  опубликован #{post['id']} → {post['buffer_id']}")
        except Exception as exc:  # одно битое не должно ронять весь запуск
            print(f"  НЕ ОПУБЛИКОВАН #{post['id']}: {exc}", file=sys.stderr)

    if published:
        with open(queue_path, "w", encoding="utf-8") as fh:
            json.dump(queue, fh, ensure_ascii=False, indent=2)
        print(f"\nОпубликовано: {published}. Очередь сохранена.")


if __name__ == "__main__":
    main()