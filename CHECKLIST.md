# TenderFox — checklist соответствия задумке (Стартап #10)

Задумка: агрегатор тендеров (MVP), фильтры, уведомления (Telegram), далее — скоринг/риск и аналитика.

> Статусы: DONE / PARTIAL / TODO

## Текущая оценка

- Готовность к MVP: **~85–90%**
- Не хватает до прод-MVP в основном: домен+HTTPS и минимальный /app кабинет.

---

## Источник данных (тендеры)

- [x] DONE поиск
- [x] DONE карточка
- [ ] TODO резервный источник

## Хранилище (Postgres)

- [x] DONE tenders/subscriptions/deliveries
- [x] DONE миграции
- [x] DONE дедуп deliveries

## Telegram

- [x] DONE бот (start/add/my)
- [x] DONE авто-рассылка scheduler

## Сайт

- [x] DONE лендинг
- [ ] TODO /app (минимум)

## Инженерия

- [x] DONE Docker
- [x] DONE CI
- [ ] TODO HTTPS + домен
