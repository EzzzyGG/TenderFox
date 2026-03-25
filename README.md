# TenderFox

TenderFox — MVP агрегатор тендеров: **поиск → фильтры → подписка → уведомления**.

MVP поверхности:
- **Website (лендинг)**
- **Telegram bot**

---

## Быстрый старт (Docker)

1) Скопируй `.env.example` → `.env` и заполни переменные.

2) Собери и подними сервисы:

- `docker compose up --build -d`

3) Прогони миграции:

- `docker compose run --rm api alembic upgrade head`

4) Проверь health:

- `curl 'http://localhost:8000/health'`

---

## Сайт (лендинг)

После запуска Docker лендинг доступен на:
- <http://localhost:8080>

Telegram бот:
- <https://t.me/RuTenderFox_bot>


