from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.db.session import SessionLocal
from app.models.phone_verification import PhoneVerification


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def _create_pv(phone: str, code: str = "111111") -> None:
    now = datetime.now(timezone.utc)
    with SessionLocal() as db:
        pv = PhoneVerification(
            phone_e164=phone,
            code=code,
            expires_at=now + timedelta(minutes=10),
            attempts=0,
            used=False,
            locked_until=None,
        )
        db.add(pv)
        db.commit()


def test_verify_sms_lockout_after_max_attempts(client: TestClient) -> None:
    phone = "+79991234567"
    _create_pv(phone=phone, code="999999")

    # 5 wrong attempts => invalid_code; next call => 429 lockout
    for _ in range(5):
        r = client.post("/auth/verify_sms", json={"phone": phone, "code": "000000"})
        assert r.status_code == 400

    r = client.post("/auth/verify_sms", json={"phone": phone, "code": "000000"})
    assert r.status_code == 429
    data = r.json()
    assert data.get("detail", {}).get("error") == "too_many_attempts"
    assert isinstance(data.get("detail", {}).get("retry_after_seconds"), int)
