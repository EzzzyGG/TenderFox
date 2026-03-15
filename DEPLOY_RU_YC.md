# TenderFox — деплой в РФ (Yandex Cloud) для MVP

Цель: быстро запустить TenderFox в прод, **без усложнений**, под РФ: 1 VM + Docker Compose, HTTPS, переменные окружения.

> Этот документ описывает самый практичный путь для MVP: **одна виртуалка** + `docker compose`.

---

## 1) Рекомендуемая архитектура (MVP)

### Компоненты
- **1 VM в Yandex Cloud Compute**
- **Docker Compose**:
  - `api` (FastAPI)
  - `postgres`
  - `redis`
- **Reverse proxy + HTTPS**: Caddy (самый простой вариант) или Nginx

### DNS / домены
- Когда домен будет выбран:
  - `api.<domain>` → публичный IP VM
  - (позже) `www.<domain>` → тот же IP (для лендинга)

> Пока домена нет, можно тестировать по IP.

---

## 2) Подготовка VM в Yandex Cloud

### Параметры VM (минимум)
- CPU: 2 vCPU
- RAM: 4 GB
- Disk: 40–60 GB SSD
- OS: Ubuntu 22.04 LTS

### Сеть
- Публичный IP
- Security group:
  - inbound: 22 (SSH) только с твоего IP
  - inbound: 80, 443 (HTTP/HTTPS) — для API/сайта
  - **НЕ** открывать наружу 5432 (Postgres) и 6379 (Redis)

---

## 3) Установка Docker на VM

```bash
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg

# Docker repo
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo $VERSION_CODENAME) stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

sudo usermod -aG docker $USER
# перелогинься в SSH
```

---

## 4) Деплой приложения

### 4.1 Клонировать репо
```bash
git clone https://github.com/EzzzyGG/TenderFox.git
cd TenderFox
```

### 4.2 Подготовить `.env`
На сервере **не коммитим** секреты. Заполняем `.env`:

- `DATABASE_URL` должен указывать на `postgres` (как сейчас в compose)
- `GOSPLAN_BASE_URL` по умолчанию test (можно оставить)
- позже добавим `TELEGRAM_BOT_TOKEN`

---

## 5) Запуск

```bash
docker compose up --build -d

docker compose run --rm api alembic upgrade head
```

Проверка:
```bash
curl http://127.0.0.1:8000/health
```

---

## 6) HTTPS (рекомендую Caddy)

### Вариант A: Caddy контейнером
Идея: поднимаем Caddy как отдельный сервис и проксируем `api`.

Когда будет домен, в `Caddyfile`:

```
api.example.ru {
  reverse_proxy api:8000
}
```

Caddy сам выпустит сертификат Let’s Encrypt.

> Это будет отдельным PR, когда определишь домен.

---

## 7) Набор практических правил

- Postgres/Redis наружу не публикуем.
- SSH ограничиваем по IP.
- Обновления: `git pull` + `docker compose up --build -d`.
- Логи: `docker compose logs -f api`.

---

## 8) Что дальше (последовательность)

1) Telegram-бот (MVP) + переменная `TELEGRAM_BOT_TOKEN`
2) Планировщик (Celery+beat) для рассылок
3) Сайт-лендинг
4) После выбора домена — PR с Caddy/Nginx + HTTPS

