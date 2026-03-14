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

## 3) Как запустить и проверить сейчас (чёткие команды)

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
1) возьми `source_id` из поиска
2) запрос:
```bash
curl 'http://localhost:8000/tenders/<source_id>'
```

Подписка:
```bash
curl -X POST http://localhost:8000/subscriptions \
  -H 'Content-Type: application/json' \
  -d '{"chat_id":"demo","keyword":"стройка","region":"77","min_price":100000}'
```

---

## 4) Что осталось до MVP по задумке (самое важное)

### 4.1 Telegram‑бот + рассылка
- бот `/start` + привязка chat_id
- задачи планировщика: поиск новых тендеров под подписки
- таблица `deliveries` уже готова для дедупа

### 4.2 Сайт
- лендинг с CTA «Открыть в Telegram»
- минимальная страница управления подписками (можно read‑only на старте)

### 4.3 Стабилизация источника
Сейчас используем GosPlan v2 test (без ключа). Дальше варианты:
- перейти на прод GosPlan (ключ) и/или
- прямой zakupki (HTML/FTP/XML), когда будет доступ из окружения

---

## 5) Принятые решения (важно)

- Регион в API: **код региона** (например, `77`). Для людей показываем название на UI‑слое.
- Миграции: **явной командой**, без авто‑применения при старте.
- Кеш тендеров: Postgres как единый источник истины для рассылки/аналитики.

