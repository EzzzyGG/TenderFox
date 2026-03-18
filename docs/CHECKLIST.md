# TenderFox — checklist соответствия задумке (Стартап #10)

Задумка: агрегатор тендеров (MVP), фильтры, уведомления (Telegram), далее — скоринг/риск и аналитика.

> Статусы: **DONE** / **PARTIAL** / **TODO**

## 0) Текущая оценка соответствия

- Общая готовность к задумке: **~55–60%**

---

## 1) Источник данных (тендеры)

- [x] **DONE** Подключён реальный REST-источник (через GosPlan v2 test как обёртку над ЕИС/zakupki)
- [x] **DONE** Получение карточки тендера (детали)
- [x] **DONE** Нормализация полей (единый формат результата в API)
- [ ] **TODO** Инкрементальная синхронизация «новых» тендеров по времени публикации/изменения
- [ ] **TODO** Резервный источник при недоступности обёртки

## 2) Хранилище (PostgreSQL)

- [x] **DONE** Схема БД: tenders, subscriptions, deliveries
- [x] **DONE** Миграции (Alembic)
- [x] **DONE** Idempotency: уникальные ключи по `(source, source_id)`

## 3) API (FastAPI)

- [x] **DONE** `GET /search` — реальные результаты
- [x] **DONE** `GET /tenders/{id}` — карточка (кеш в БД)
- [x] **DONE** `POST /subscriptions`
- [x] **DONE** `GET /subscriptions`

## 4) Уведомления (Telegram)

- [ ] **TODO** Telegram bot + получение chat_id
- [ ] **TODO** Отправка уведомлений по подписке

## 5) Планировщик

- [ ] **TODO** Периодическая проверка подписок и доставка
- [x] **DONE** Дедуп deliveries (unique subscription_id+tender_id)

## 6) Пипл-френдли

- [x] **DONE** Понятная выдача / фильтры

## 7) Инженерия

- [x] **DONE** Структура проекта
- [x] **DONE** Poetry/pyproject
- [x] **DONE** Dockerfile + docker-compose
- [x] **DONE** `.env.example`
- [ ] **TODO** CI (GitHub Actions): lint + tests
