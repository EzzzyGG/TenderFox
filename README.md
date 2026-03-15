# TenderFox

TenderFox — MVP агрегатора тендеров: **поиск → фильтры → подписка → уведомления в Telegram** + **сайт (лендинг/кабинет)**.

## Быстрый старт (Docker)

### 1) Подготовка
- Установи Docker + Docker Compose.
- Заполни `.env` (минимум: `TELEGRAM_BOT_TOKEN`).

### 2) Запуск инфраструктуры
```bash
docker compose up --build -d
```

### 3) Применить миграции (обязательно)
```bash
docker compose run --rm api alembic upgrade head
```

### 4) Проверка
Health:
```bash
curl 'http://localhost:8000/health'
```

---

## Telegram-бот (MVP)

Команды:
- `/start`
- `/add <ключевые слова> [регион_код]` (пример: `/add мебель 77`)
- `/my`

---

## Реальный поиск тендеров (MVP)

> Источник: GosPlan API v2 test (обёртка над ЕИС/zakupki, 44‑ФЗ). Настраивается переменной `GOSPLAN_BASE_URL`.

Поиск:
```bash
curl 'http://localhost:8000/search?keyword=мебель&region=77&limit=5'
```

Карточка:
```bash
curl 'http://localhost:8000/tenders/<source_id>'
```

---

## Документы

- `DEPLOY_RU_YC.md` — деплой в РФ (Yandex Cloud) для MVP
- `WORK_REPORT.md` — подробный отчёт по проделанной работе
- `PLAN.md` — полный план работ
- `CHECKLIST.md` — чеклист соответствия задумке
- `TODO.md` — дорожная карта

## Источники

- Swagger GosPlan (44‑ФЗ): <https://swagger.gosplan.info/?urls.primaryName=44-%D0%A4%D0%97>
- Wiki GosPlan: <https://wiki.gosplan.info>
