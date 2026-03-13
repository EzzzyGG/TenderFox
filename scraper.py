import random

def analyze_risk(inn: str):
    # В реальной версии здесь интеграция с API арбитражных судов и реестром ФАС
    score = random.randint(40, 95)
    
    if score > 80:
        advice = "Заказчик надежен. Оплата вовремя в 98% случаев."
    elif score > 60:
        advice = "Средний риск. Возможны задержки до 14 дней."
    else:
        advice = "Высокий риск. Заказчик часто судится по невыплатам."
        
    return {
        "score": score,
        "advice": advice,
        "details": {
            "court_cases_count": random.randint(0, 15),
            "typical_payment_delay": f"{random.randint(0, 30)} days",
            "corruption_index": f"{random.randint(5, 50)}%"
        }
    }
