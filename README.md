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
Health:
```bash
curl 'http://localhost:8000/health'
```

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

## Подписки (пока MVP без бота)

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
