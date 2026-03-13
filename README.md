# TenderFox

TenderFox — MVP агрегатора тендеров: **поиск → фильтры → подписка → уведомления в Telegram**.

## Быстрый старт (локально)

### Требования
- Python **3.11**
- Poetry

### Установка
```bash
poetry install
```

### Запуск API
```bash
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Проверка
- Health: `GET http://localhost:8000/health`
- Search (пока заглушка): `GET http://localhost:8000/search?keyword=стройка&region=77`

## Что дальше
Смотри:
- `CHECKLIST.md`
- `TODO.md`
