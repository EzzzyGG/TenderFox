# TenderFox

TenderFox — MVP агрегатора тендеров: **поиск → фильтры → подписка → уведомления в Telegram** + **сайт (лендинг/кабинет)**.

## Быстрый старт (Docker)

### 1) Подготовка
- Установи Docker + Docker Compose.
- Скопируй `.env.example` → `.env` и заполни минимум: `TELEGRAM_BOT_TOKEN`.

```bash
cp .env.example .env
```

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

## CI

В репозитории настроен GitHub Actions CI:
- `ruff` (lint)
- `pytest` (tests)

---

## Документы

Все документы проекта лежат в папке `docs/`:
- `docs/DEPLOY_RU_YC.md` — деплой в РФ (Yandex Cloud) для MVP
- `docs/WORK_REPORT.md` — отчёт по проделанной работе
- `docs/PLAN.md` — подробный план
- `docs/CHECKLIST.md` — чеклист соответствия задумке
- `docs/TODO.md` — план развития
- `docs/ROADMAP.md` — продуктовый роадмап
- `docs/LEGAL_RU.md` — заметки по юр.части (РФ)
- `docs/PAYMENTS_YOOKASSA_NOTES.md` — заметки по интеграции оплат (YooKassa)

## Источники

- Swagger GosPlan (44‑ФЗ): <https://swagger.gosplan.info/?urls.primaryName=44-%D0%A4%D0%97>
- Wiki GosPlan: <https://wiki.gosplan.info>
