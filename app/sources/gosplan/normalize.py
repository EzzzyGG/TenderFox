from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(frozen=True)
class TenderNormalized:
    source: str
    source_id: str
    title: str
    price: Decimal | None
    currency: str | None
    region: str | None
    published_at: datetime | None
    deadline_at: datetime | None
    url: str | None
    raw: dict


def _parse_dt(value) -> datetime | None:
    if not value:
        return None
    # gosplan returns ISO 8601; python can parse with fromisoformat when Z is normalized
    if isinstance(value, str):
        v = value.replace("Z", "+00:00")
        try:
            return datetime.fromisoformat(v)
        except ValueError:
            return None
    return None


def normalize_purchase(item: dict) -> TenderNormalized:
    # Attempt to map common gosplan fields
    purchase_number = str(item.get("purchase_number") or item.get("reg_num") or item.get("number") or "")
    title = (
        item.get("object_info")
        or item.get("purchase_object")
        or item.get("name")
        or item.get("title")
        or ""
    )

    max_price = item.get("max_price") or item.get("price")
    price = None
    if max_price is not None:
        try:
            price = Decimal(str(max_price))
        except Exception:
            price = None

    region = item.get("region")
    region_str = str(region) if region is not None else None

    published_at = _parse_dt(item.get("published_at") or item.get("publish_date") or item.get("published"))
    deadline_at = _parse_dt(item.get("collecting_finished_at") or item.get("deadline_at"))

    url = item.get("url")
    if not url and purchase_number:
        # Fallback to zakupki tender card
        url = (
            "https://zakupki.gov.ru/epz/order/notice/ea44/view/common-info.html"
            f"?regNumber={purchase_number}"
        )

    return TenderNormalized(
        source="gosplan_fz44",
        source_id=purchase_number,
        title=title,
        price=price,
        currency="RUB",
        region=region_str,
        published_at=published_at,
        deadline_at=deadline_at,
        url=url,
        raw=item,
    )
