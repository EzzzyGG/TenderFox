# TenderFox — отчёт по проделанной работе (на текущий момент)

Дата: 2026-03-14

## 1) Коротко: где мы сейчас

На сегодня TenderFox — это **живой MVP-каркас**, который:

- запускается через **Docker Compose** (API + Postgres + Redis)
- имеет **миграции Alembic** и рабочую **БД-схему**
- умеет **создавать и читать подписки** через API (`/subscriptions`)
- умеет **искать реальные тендеры** и получать **реальную карточку** через API (`/search`, `/tenders/{id}`)
- **кеширует тендеры в Postgres** (upsert по `(source, source_id)`) для дальнейшей рассылки/аналитики

Источник тендеров сейчас: **GosPlan API v2 test** (обёртка над ЕИС/zakupki по 44‑ФЗ), потому что прямой `zakupki.gov.ru` из нашей среды недоступен.

> Деплой планируется в РФ, ориентир: **Yandex Cloud**. См. `docs/DEPLOY_RU_YC.md`.

---

## 2) Что было сделано по этапам (в терминах целей)

### 2.1 Документация и управление работой

- `docs/CHECKLIST.md` — чеклист соответствия задумке
- `docs/TODO.md` — план по кварталам
- `docs/PLAN.md` — подробный end‑to‑end план

### 2.2 Каркас приложения (FastAPI + Poetry + Python 3.11)

- структура `app/`
- роутер API
- healthcheck + тест

### 2.3 Docker / окружение

- `Dockerfile`
- `docker-compose.yml`
- `.env.example`

### 2.4 База данных + миграции

- SQLAlchemy модели
- Alembic миграции

### 2.5 Реальный источник тендеров

- `GET /search`
- `GET /tenders/{id}`

---

## 3) Что дальше (3 ближайших шага)

1) Telegram onboarding (получить и сохранять `chat_id`)
2) Scheduler: end-to-end рассылка новых тендеров по подпискам
3) CI: lint + tests (GitHub Actions)
