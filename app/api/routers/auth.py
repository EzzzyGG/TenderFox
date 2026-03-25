from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.phone_verification import PhoneVerification
from app.models.telegram_link import TelegramLink
from app.models.user import User
from app.schemas.auth import (
    AuthStartIn,
    AuthStartOut,
    AuthTokenOut,
    AuthVerifySmsIn,
    AuthVerifyTelegramContactIn,
)
from app.services.jwt import create_access_token
from app.utils.phone import normalize_phone_to_e164

router = APIRouter(prefix="/auth", tags=["auth"])

# --- anti-bruteforce controls (MVP) ---
MAX_SMS_VERIFY_ATTEMPTS = 5
LOCKOUT_MINUTES = 15


@router.post("/start")
def start(payload: AuthStartIn, db: Session = Depends(get_db)) -> AuthStartOut:
    phone_e164 = normalize_phone_to_e164(payload.phone)

    # SMS stub: deterministic short code for dev.
    # Replace with random + provider later.
    code = str(abs(hash(phone_e164)) % 1000000).zfill(6)

    expires_at = datetime.now(tz=timezone.utc) + timedelta(minutes=10)

    pv = PhoneVerification(phone_e164=phone_e164, code=code, expires_at=expires_at)
    db.add(pv)
    db.commit()

    return AuthStartOut(phone_e164=phone_e164, sms_stub_code=code, expires_in_seconds=600)


def _latest_pv(db: Session, phone_e164: str) -> PhoneVerification | None:
    return (
        db.execute(
            select(PhoneVerification)
            .where(PhoneVerification.phone_e164 == phone_e164)
            .order_by(PhoneVerification.id.desc())
            .limit(1)
        )
        .scalars()
        .one_or_none()
    )


@router.post("/verify_sms")
def verify_sms(payload: AuthVerifySmsIn, db: Session = Depends(get_db)) -> AuthTokenOut:
    phone_e164 = normalize_phone_to_e164(payload.phone)

    pv = _latest_pv(db, phone_e164)
    if not pv:
        raise HTTPException(status_code=400, detail="verification_not_found")

    now = datetime.now(tz=timezone.utc)

    # expired
    if pv.expires_at < now:
        raise HTTPException(status_code=400, detail="verification_expired")

    # lockout
    if pv.locked_until is not None and pv.locked_until > now:
        seconds = int((pv.locked_until - now).total_seconds())
        raise HTTPException(
            status_code=429,
            detail={"error": "too_many_attempts", "retry_after_seconds": seconds},
        )

    # attempt accounting (always increment on verify call)
    pv.attempts += 1

    if pv.code != payload.code:
        # lock after N attempts (including this one)
        if pv.attempts >= MAX_SMS_VERIFY_ATTEMPTS:
            pv.locked_until = now + timedelta(minutes=LOCKOUT_MINUTES)
        db.commit()
        raise HTTPException(status_code=400, detail="invalid_code")

    pv.used = True

    user = db.execute(select(User).where(User.phone_e164 == phone_e164)).scalar_one_or_none()
    if not user:
        user = User(phone_e164=phone_e164, phone_verified=True, phone_verified_via="sms")
        db.add(user)
    else:
        user.phone_verified = True
        user.phone_verified_via = "sms"

    db.commit()
    db.refresh(user)

    return AuthTokenOut(access_token=create_access_token(sub=str(user.id)))


@router.post("/verify_telegram_contact")
def verify_telegram_contact(
    payload: AuthVerifyTelegramContactIn,
    db: Session = Depends(get_db),
) -> AuthTokenOut:
    phone_e164 = normalize_phone_to_e164(payload.phone)
    phone_from_tg = normalize_phone_to_e164(payload.phone_from_telegram)
    if phone_e164 != phone_from_tg:
        raise HTTPException(status_code=400, detail="phone_mismatch")

    user = db.execute(select(User).where(User.phone_e164 == phone_e164)).scalar_one_or_none()
    if not user:
        user = User(phone_e164=phone_e164, phone_verified=True, phone_verified_via="telegram_contact")
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        user.phone_verified = True
        user.phone_verified_via = "telegram_contact"
        db.commit()

    link = db.execute(select(TelegramLink).where(TelegramLink.user_id == user.id)).scalar_one_or_none()
    if not link:
        link = TelegramLink(
            user_id=user.id,
            telegram_user_id=payload.telegram_user_id,
            chat_id=payload.chat_id,
            phone_e164_from_telegram=phone_from_tg,
        )
        db.add(link)
    else:
        link.telegram_user_id = payload.telegram_user_id
        link.chat_id = payload.chat_id
        link.phone_e164_from_telegram = phone_from_tg

    db.commit()

    return AuthTokenOut(access_token=create_access_token(sub=str(user.id)))
