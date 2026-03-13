# TenderFox — подробный план от начала до конца (MVP → V1)

Цель продукта: агрегатор тендеров, который **находит релевантные тендеры**, позволяет **подписаться на фильтр** и **получать уведомления в Telegram**. Дальше — объяснимый риск/скоринг, аналитика, монетизация.

> Принципы: без воды, без холодных продаж, только таргет/реклама. MVP = «первый успех за 2 минуты».

---

## 0) Текущее состояние (что уже в репо)

- Документация: `CHECKLIST.md`, `TODO.md`
- Каркас проекта: FastAPI + Poetry + тест `/health`
- Сейчас **нет**: docker-compose, БД/миграций, источника zakupki, Telegram-бота, планировщика.

---

## 1) Definition of Done

### MVP готов, если:
- `GET /search` возвращает **реальные** тендеры из источника
- `POST /subscriptions` сохраняет фильтр + chat_id
- Планировщик находит новые тендеры под подписки
- Telegram бот доставляет сообщения
- Запуск одной командой: `docker compose up --build`

### V1 готов, если:
- Есть личный кабинет/минимальный UI или хотя бы админ-страница
- Есть тарифы/лимиты (если включаем оплату)
- Есть объяснимый скоринг/риск (rule-based)

---

## 2) Этапы разработки (пакетами PR)

### PR-A (сделано)
- Док-пакет: чеклист + TODO
- Каркас FastAPI + Poetry + тест

### PR-B: Docker + окружение (1 день)
**Цель:** поднять api+postgres+redis.

Deliverables:
- `Dockerfile`
- `docker-compose.yml` (api, postgres, redis)
- `README.md` с командами запуска
- healthcheck’и

Acceptance:
- `docker compose up --build` → `GET /health` отдаёт `{status: ok}`

---

### PR-C: DB слой + миграции (1–2 дня)
**Цель:** подготовить PostgreSQL как источник истины.

Добавить зависимости:
- `sqlalchemy`, `alembic`, `psycopg`

Модели (минимум):
- `Tender` (source, source_id, title, price, region, published_at, url, raw_json)
- `Subscription` (chat_id, keyword, region, min_price, created_at, active)
- `Delivery` (subscription_id, tender_id, sent_at, status)

Deliverables:
- `app/db/` (engine, session)
- `app/models/`
- `app/repositories/`
- `alembic/` + первая миграция

Acceptance:
- миграции применяются в docker-compose
- `POST /subscriptions` реально пишет в БД

---

### PR-D: Источник данных zakupki.gov.ru (2–4 дня)
**Цель:** реальный поиск и нормализация.

Решение:
- Начать с одного источника: `zakupki.gov.ru`.
- Реализовать клиент в `app/sources/zakupki/`.

Функции:
- `search(keyword, region, min_price, published_from)` → list[TenderNormalized]
- `get_tender(source_id)` → TenderNormalized + детали (минимум: title, price, deadline/published, url)

Нормализация (единый формат):
- `id` (source_id)
- `title`
- `price`
- `currency`
- `region`
- `published_at`
- `deadline_at` (если доступно)
- `customer`
- `url`

Acceptance:
- `/search` выдаёт 10+ реальных тендеров
- `/tenders/{id}` отдаёт реальную карточку

---

### PR-E: Подписки + дедуп (1–2 дня)
**Цель:** подписка сохраняется, а выдача/рассылка не дублирует.

Deliverables:
- `POST /subscriptions` принимает фильтр (keyword, region, min_price) + `chat_id`
- уникальность/дедуп логика (Delivery уникальна по subscription+tender)

Acceptance:
- при повторной обработке не создаются повторные deliveries

---

### PR-F: Telegram бот (1–2 дня)
**Цель:** “пипл-френдли” onboarding.

Минимум команд:
- `/start` — приветствие + как пользоваться
- `/my` — показать активные подписки
- `/add` — быстрый флоу добавления (можно кнопками позже)

Deliverables:
- `app/integrations/telegram/` (aiogram или python-telegram-bot)
- хранение chat_id

Acceptance:
- бот отвечает на `/start`
- можно привязать chat_id и создать подписку

---

### PR-G: Планировщик рассылки (1–2 дня)
**Цель:** периодическая проверка и отправка.

Вариант 1 (рекомендую): Celery + Beat
- tasks: `sync_new_tenders()`, `deliver_notifications()`

Deliverables:
- celery worker + beat в docker-compose
- rate limiting и обработка ошибок

Acceptance:
- раз в N минут появляются сообщения по новым тендерам

---

### PR-H: Пипл-френдли полировка (1 день)
**Цель:** “первый успех за 2 минуты”.

- короткие сообщения
- понятные ошибки
- демо-режим/пример
- README: сценарии

---

## 3) Формат уведомления (коротко и понятно)

Шаблон:
- Заголовок (1 строка)
- Цена + дедлайн
- Регион + заказчик
- Ссылка

Пример:
- `🦊 Тендер: Поставка офисной мебели`
- `Цена: 1 200 000 ₽ | Дедлайн: 2026-03-20`
- `Регион: Москва | Заказчик: ГБУ ...`
- `Ссылка: ...`

(иконки можно убрать, если хочешь максимально строго)

---

## 4) Скоринг/риск (после MVP)

Только explainable:
- `score: 0..100`
- `reasons[]`: список причин

Источник причин (пример):
- частые отмены
- слишком короткий срок подачи
- подозрительно узкое ТЗ

---

## 5) Монетизация (после MVP)

Freemium:
- Free: 1 подписка + 1 регион
- Pro: до N подписок + больше фильтров + чаще проверка

ЮKassa:
- подключаем после стабилизации MVP

---

## 6) Маркетинг (только таргет)

- Реклама ведёт на лендинг с одним CTA: «получать тендеры в Telegram»
- Минимальный лендинг позже; в MVP можно начать с Telegram.

---

## 7) Риски и анти-риски

- API zakupki может быть нестабильным → кеширование + ретраи + backoff
- Дубли рассылок → таблица `deliveries` + unique constraint
- Бан/антибот → минимизировать агрессию, использовать API/официальные пути, лимиты

---

## 8) Порядок прямо сейчас (следующий шаг)

1) PR-B Docker
2) PR-C DB + миграции
3) PR-D zakupki search
4) PR-F Telegram
5) PR-G scheduler

