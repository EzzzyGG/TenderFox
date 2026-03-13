import requests

def search_tenders(keyword: str, region: str = None):
    # Эмуляция работы парсера. В MVP интеграция с открытым API zakupki.gov.ru
    dummy_results = [
        {"id": "3240001", "title": f"Поставка товаров: {keyword}", "price": 500000, "customer": "Минздрав"},
        {"id": "3240002", "title": f"Оказание услуг по {keyword}", "price": 1200000, "customer": "РЖД"},
    ]
    return dummy_results
