# TenderFox — подробный план от начала до конца (MVP → V1)

Цель продукта: агрегатор тендеров, который **находит релевантные тендеры**, позволяет **подписаться на фильтр** и **получать уведомления в Telegram**. Дальше — объяснимый риск/скоринг, аналитика, монетизация.

## Каналы (surface) продукта

Мы делаем **везде** одинаковую продуктовую логику, но разные интерфейсы:

### Сейчас (MVP)
1) **Telegram-бот** — канал доставки (и привязка аккаунта)
2) **Сайт** — лендинг + кабинет (управление подписками)

### Позже (V1/V2)
3) **Telegram Mini App**

---

## 0) Текущее состояние

- Запуск: Docker Compose (API + Postgres + Redis)
- Миграции: Alembic
- Тендеры: `/search`, `/tenders/{id}` (GosPlan v2 test)
- Подписки: `/subscriptions` (сейчас привязка по `chat_id`, нужно перевести на `user_id`)
- Есть каркас scheduler и telegram bot

---

## 1) Definition of Done (обновлено под текущую цель)

### MVP готов, если:
- На сайте есть PHONE-first регистрация (телефоны СНГ, нормализация в E.164)
- Подтверждение телефона: сначала через Telegram contact (если возможно), fallback через SMS-код (stub на MVP)
- Подписки создаются **на сайте** и принадлежат `user_id`
- Telegram-бот привязан к user и служит **только для доставки уведомлений**
- Scheduler находит новые тендеры и отправляет в Telegram, дедуп через `deliveries`

---

## 2) Этапы реализации (пакетами PR)

### PR-A: Документация и управление работой
- `docs/*`

### PR-B: Каркас проекта
- FastAPI + Poetry + Python 3.11

### PR-C: Docker bootstrap
- Dockerfile + docker-compose

### PR-D: DB + Alembic + tenders/subscriptions/deliveries

### PR-E: Реальный источник тендеров
- `/search` + `/tenders/{id}`

### PR-F (NEW): Пользователи + PHONE-first auth + верификация
- Alembic: добавить таблицы `users`, `phone_verifications`, `telegram_links`
- Нормализация телефонов СНГ → E.164 (минимум коды: +7, +375, +380, +374, +994, +995, +996, +998, +992, +993, +373)
- API (минимум):
  - `POST /auth/start` (создать попытку верификации)
  - `POST /auth/verify/telegram_contact` (подтверждение телефона через Telegram contact)
  - `POST /auth/request_sms` (stub)
  - `POST /auth/verify_sms` (stub)
  - `GET /me` (JWT)

### PR-G (NEW): Telegram-бот — только привязка и доставка
- `/start`
- `/link <code>` (если введём link_code как безопасную связку)
- получение контакта и вызов API подтверждения
- удалить/задепрекейтить команды управления подписками в боте (`/add`, `/my`)

### PR-H (NEW): Перевести подписки на `user_id`
- DB миграция: `subscriptions.user_id`
- API: CRUD подписок только для авторизованного user

### PR-I (NEW): Scheduler end-to-end по user_id
- выбор `chat_id` через `telegram_links`
- логирование и пропуски, если telegram не привязан

### PR-J: Next.js кабинет
- UI для регистрации/логина
- UI для подписок
- UI/страница привязки Telegram

---

## 3) Порядок приоритета

1) PR-F Users/Auth
2) PR-H Subscriptions → user
3) PR-G Bot linking
4) PR-I Scheduler delivery
5) PR-J Next.js кабинет
