# YooKassa — заметки по интеграции (черновик)

Ниже — сохранённый шаблон/идея из прежнего `LEGAL.md`.

```python
def create_yookassa_payment(amount, user_id):
    # Шаблон интеграции с ЮKassa SDK
    # 1. Формируем запрос к API
    # 2. Получаем confirmation_url
    return {"payment_id": "pay_12345", "url": "https://yookassa.ru/checkout/..."}


def handle_webhook(data):
    # Обработка уведомления об успешной оплате
    if data['event'] == "payment.succeeded":
        return True
    return False
```
