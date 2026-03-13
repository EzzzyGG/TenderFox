# TenderFox

TenderFox — MVP агрегатора тендеров: **поиск → фильтры → подписка → уведомления в Telegram** + **сайт (лендинг/кабинет)**.

## Быстрый старт (Docker)

### 1) Подготовка
- Установи Docker + Docker Compose.
- Проверь переменные окружения в `.env`.

### 2) Запуск инфраструктуры
```bash
docker compose up --build -d
```

### 3) Применить миграции (обязательно)
```bash
docker compose run --rm api alembic upgrade head
```

### 4) Проверка
- Health: `GET http://localhost:8000/health`

### 5) Проверка подписок (MVP)
Создать подписку:
```bash
curl -X POST http://localhost:8000/subscriptions \
  -H 'Content-Type: application/json' \
  -d '{"chat_id":"demo","keyword":"стройка","region":"77","min_price":100000}'
```

Посмотреть подписки:
```bash
curl 'http://localhost:8000/subscriptions?chat_id=demo'
```

## Локальный старт (Poetry)

### Требования
- Python **3.11**
- Poetry

### Установка
```bash
poetry install
```

### Миграции (локально)
```bash
export DATABASE_URL='postgresql+psycopg://tenderfox:tenderfox@localhost:5432/tenderfox'
alembic upgrade head
```

### Запуск API
```bash
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Документы
- `PLAN.md` — полный план работ
- `CHECKLIST.md` — чеклист соответствия задумке
- `TODO.md` — дорожная карта
