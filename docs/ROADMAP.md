# TenderFox — Roadmap

> Роадмап фиксирует только то, что реально есть в репозитории, и следующие шаги.

## Текущее состояние (сделано)

- Docker Compose (api + postgres + redis)
- Alembic миграции
- Postgres модели: `tenders/subscriptions/deliveries`
- API: `/health`, `/search`, `/tenders/{id}`, `/subscriptions`
- Источник тендеров: GosPlan v2 test
- Лендинг (статический) в `web/`
- CI (GitHub Actions): `ruff` + `pytest`

## Следующий MVP (что нужно добить)

### 1) Пользователи (PHONE-first) + СНГ
- Нормализация телефонов СНГ в E.164 (минимум: +7, +375, +380, +374, +994, +995, +996, +998, +992, +993, +373)
- Подтверждение телефона:
  - сначала Telegram contact (если возможно)
  - fallback SMS (stub)
- JWT auth для Next.js

### 2) Подписки на сайте
- подписки принадлежат `user_id` (не chat_id)
- CRUD подписок только для авторизованного пользователя

### 3) Telegram как канал доставки
- привязка Telegram к `user_id`
- отправка уведомлений через scheduler

### 4) Scheduler end-to-end
- выбор `chat_id` через `telegram_links`
- дедуп через `deliveries`

## Funding / Grants
- Подготовить заявку на грант Yandex Cloud (см. `docs/TODO.md` → Funding / Grants)
