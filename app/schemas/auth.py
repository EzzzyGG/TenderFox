from __future__ import annotations

from pydantic import BaseModel, Field


class AuthStartIn(BaseModel):
    phone: str = Field(min_length=5, max_length=64)


class AuthStartOut(BaseModel):
    phone_e164: str
    sms_stub_code: str
    expires_in_seconds: int


class AuthVerifySmsIn(BaseModel):
    phone: str = Field(min_length=5, max_length=64)
    code: str = Field(min_length=3, max_length=16)


class AuthTokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class AuthVerifyTelegramContactIn(BaseModel):
    phone: str = Field(min_length=5, max_length=64)
    telegram_user_id: str = Field(min_length=1, max_length=64)
    chat_id: str = Field(min_length=1, max_length=64)
    phone_from_telegram: str = Field(min_length=5, max_length=64)
