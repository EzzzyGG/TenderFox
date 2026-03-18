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

## Сайт (лендинг)

После запуска Docker лендинг доступен на:
- <http://localhost:8080>

Telegram бот:
- <https://t.me/RuTenderFox_bot>

---

## Telegram-бот (MVP)

Команды:
- `/start`
- `/add <ключевые слова> [регион_код]` (пример: `/add мебель 77`)
- `/my`

---

## Авто-рассылка (MVP)

Сервис `scheduler` в docker-compose каждые `SCHEDULER_INTERVAL_SECONDS` секунд:
- берёт активные подписки из БД
- ищет тендеры по каждому фильтру
- отправляет **новые** тендеры в Telegram
- дедуп делает через таблицу `deliveries` (unique по subscription+tender)

Логи:
```bash
docker compose logs -f scheduler
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
