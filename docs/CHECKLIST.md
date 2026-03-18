# TenderFox — checklist соответствия задумке

Задумка: агрегатор тендеров (MVP), фильтры, уведомления (Telegram), далее — скоринг/риск и аналитика.

> Статусы: **DONE** / **PARTIAL** / **TODO**

## 1) Источник данных (тендеры)
- [x] **DONE** Реальный REST-источник (через GosPlan v2 test)
- [x] **DONE** Карточка тендера
- [x] **DONE** Нормализация результата
- [ ] **TODO** Инкрементальная синхронизация «новых» тендеров
- [ ] **TODO** Резервный источник

## 2) Хранилище (PostgreSQL)
- [x] **DONE** Схема БД: tenders, subscriptions, deliveries
- [x] **DONE** Миграции (Alembic)
- [x] **DONE** Idempotency: уникальные ключи по `(source, source_id)`

## 3) API (FastAPI)
- [x] **DONE** `/search`
- [x] **DONE** `/tenders/{id}`
- [x] **DONE** `/subscriptions` (текущее: chat_id)

## 4) Пользователи и PHONE-first auth
- [ ] **TODO** Таблица users
- [ ] **TODO** Нормализация телефонов СНГ (E.164)
- [ ] **TODO** Верификация телефона: Telegram contact → fallback SMS
- [ ] **TODO** JWT auth (для Next.js)

## 5) Telegram (канал доставки)
- [ ] **TODO** Привязка Telegram к `user_id`
- [ ] **TODO** Отправка уведомлений

## 6) Scheduler
- [ ] **TODO** End-to-end рассылка по подпискам пользователя
- [x] **DONE** Дедуп deliveries (unique subscription_id+tender_id)

## 7) Инженерия
- [x] **DONE** Структура проекта
- [x] **DONE** Poetry/pyproject
- [x] **DONE** Dockerfile + docker-compose
- [x] **DONE** `.env.example`
- [x] **DONE** CI: lint + tests
