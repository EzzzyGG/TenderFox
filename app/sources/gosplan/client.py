from __future__ import annotations

from dataclasses import dataclass

import httpx

from app.core.config import settings


@dataclass(frozen=True)
class GosplanClient:
    base_url: str = settings.gosplan_base_url

    async def get(self, path: str, params: dict | None = None) -> dict:
        url = f"{self.base_url}{path}"
        async with httpx.AsyncClient(timeout=30.0) as client:
            r = await client.get(url, params=params)
            r.raise_for_status()
            return r.json()

    async def list_purchases(
        self,
        *,
        keyword: str,
        region: int | None,
        limit: int = 20,
        skip: int = 0,
        stage: int = 1,
    ) -> dict:
        params: dict = {
            "object_info": keyword,
            "limit": limit,
            "skip": skip,
            "stage": stage,
            "sort": "published_at_desc",
        }
        if region is not None:
            params["region"] = region
        return await self.get("/purchases", params=params)

    async def get_purchase(self, purchase_number: str) -> dict:
        return await self.get(f"/purchases/{purchase_number}")
