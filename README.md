# TenderFox

TenderFox — MVP агрегатора тендеров: **поиск → фильтры → подписка → уведомления в Telegram** + **сайт (лендинг/кабинет)**.

## Быстрый старт (Docker)

### 1) Подготовка
- Убедись, что установлен Docker + Docker Compose.
- Проверь переменные окружения в `.env` (для локального старта уже есть дефолты).

### 2) Запуск
```bash
docker compose up --build
```

### 3) Проверка
- Health: `GET http://localhost:8000/health`
- Search (пока заглушка): `GET http://localhost:8000/search?keyword=стройка&region=77`

## Локальный старт (Poetry)

### Требования
- Python **3.11**
- Poetry

### Установка
```bash
poetry install
```

### Запуск API
```bash
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Документы
- `PLAN.md` — полный план работ
- `CHECKLIST.md` — чеклист соответствия задумке
- `TODO.md` — дорожная карта
