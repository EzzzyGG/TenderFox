# TenderFox — отчёт по проделанной работе (на текущий момент)

Дата: 2026-03-18

## 1) Коротко: где мы сейчас

TenderFox — это работающий MVP-контур, который:

- запускается через **Docker Compose** (API + Postgres + Redis + Bot + Scheduler + Web)
- имеет **миграции Alembic** и рабочую **БД-схему**
- умеет:
  - создавать подписки (`/subscriptions`)
  - искать реальные тендеры (`/search`, `/tenders/{id}`)
  - принимать команды в Telegram (`/start`, `/add`, `/my`)
  - автоматически рассылать новые тендеры в Telegram (scheduler)
  - показывать лендинг (web на 8080)

Источник тендеров сейчас: **GosPlan API v2 test** (обёртка над ЕИС/zakupki по 44‑ФЗ).

Деплой планируется в РФ, ориентир: **Yandex Cloud**. См. `DEPLOY_RU_YC.md`.

---

## 2) Что сделано (по сути)

### Инфраструктура
- Dockerfile + docker-compose
- Postgres + Redis
- Alembic миграции

### Продуктовые поверхности
- Telegram-бот (основной MVP интерфейс)
- Scheduler (авто-рассылка)
- Web-лендинг

### Инженерия
- Добавлен CI (GitHub Actions): `ruff` + `pytest`
- Переменные окружения: `.env` **не хранится** в git, используем `.env.example` → `cp .env.example .env`

---

## 3) Как запустить и проверить

```bash
cp .env.example .env
# впиши TELEGRAM_BOT_TOKEN

docker compose up --build -d

docker compose run --rm api alembic upgrade head
```

Проверка:
- API health: `http://localhost:8000/health`
- Лендинг: `http://localhost:8080`
- Бот: https://t.me/RuTenderFox_bot

---

## 4) Что требуется сделать дальше (приоритет)

1) **Прод-домен + HTTPS на YC** (Caddy/Nginx)
2) **Стабилизация источника** (перейти на прод GosPlan с ключом или прямой zakupki, если нужно)
3) **Мини-кабинет (/app)** — хотя бы read-only подписки
4) Метрики/алерты (минимум)

