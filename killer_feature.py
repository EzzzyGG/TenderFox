from fastapi import FastAPI

from .killer_feature import analyze_risk
from .scraper import search_tenders

app = FastAPI(title="TenderWin API")


@app.get("/")
async def root():
    return {"status": "TenderWin Empire Core Online"}


@app.get("/search")
async def get_tenders(keyword: str, region: str = None):
    results = search_tenders(keyword, region)
    return {"count": len(results), "items": results}


@app.get("/score/{inn}")
async def get_score(inn: str):
    data = analyze_risk(inn)
    return {
        "inn": inn,
        "score": data["score"],
        "advice": data["advice"],
        "details": data["details"],
    }
