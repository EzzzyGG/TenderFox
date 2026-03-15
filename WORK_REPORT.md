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

> Деплой планируется в РФ, ориентир: **Yandex Cloud**. См. `DEPLOY_RU_YC.md`.

---

## 2) Что было сделано по этапам (в терминах целей)

### 2.1 Документация и управление работой

- `CHECKLIST.md` — чеклист соответствия задумке (есть/нет)
- `TODO.md` — план по кварталам, с MVP-скопом и требованиями «пипл‑френдли»
- `PLAN.md` — подробный end‑to‑end план с учётом **сайта**, **Telegram‑бота** и будущей **Telegram Mini App**

### 2.2 Каркас приложения (FastAPI + Poetry + Python 3.11)

- структура `app/` с роутерами
- базовый healthcheck: `GET /health`
- минимальный тест `pytest` для health

### 2.3 Docker / окружение

- `Dockerfile`
- `docker-compose.yml` (api + postgres + redis + healthchecks)
- `.env` и `.env.example`
- `README.md` обновлён: как запускать проект

### 2.4 База данных + миграции

- добавлены зависимости: `sqlalchemy`, `psycopg`, `alembic`
- добавлен DB слой: `app/db/engine.py`, `app/db/session.py`
- добавлены модели:
  - `Tender`
  - `Subscription`
  - `Delivery`
- добавлены миграции Alembic:
  - `0001_init` создаёт таблицы и индексы, включая:
    - уникальный индекс на `tenders (source, source_id)`
    - уникальный индекс на `deliveries (subscription_id, tender_id)` (для дедупа рассылок)

### 2.5 Подписки (готово для дальнейшей рассылки)

- `POST /subscriptions` — создаёт подписку в БД
- `GET /subscriptions` — возвращает список подписок, есть фильтр `chat_id`

### 2.6 Реальные тендеры (поиск + карточка)

Сделан первый рабочий источник данных:

- модуль `app/sources/gosplan/`
  - `client.py` — HTTPX клиент
  - `normalize.py` — нормализация данных в наш формат

Роуты:
- `GET /search?keyword=...&region=77&limit=...`
  - делает запрос в GosPlan `/purchases`
  - нормализует результаты
  - **upsert** каждого тендера в БД
  - возвращает нормализованный список

- `GET /tenders/{purchase_number}`
  - сначала пытается взять из Postgres
  - если нет — тянет из источника и upsert’ит

---

## 3) Как запустить и проверить сейчас

### 3.1 Запуск
```bash
docker compose up --build -d
```

### 3.2 Миграции
```bash
docker compose run --rm api alembic upgrade head
```

### 3.3 Проверка API
Health:
```bash
curl 'http://localhost:8000/health'
```

Поиск реальных тендеров:
```bash
curl 'http://localhost:8000/search?keyword=мебель&region=77&limit=5'
```

Карточка:
```bash
curl 'http://localhost:8000/tenders/<source_id>'
```

---

## 4) Что осталось до MVP по задумке

1) Telegram‑бот + onboarding
2) Планировщик + рассылка
3) Сайт‑лендинг + мини‑кабинет

