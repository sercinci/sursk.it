from __future__ import annotations

from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class ApiError(BaseModel):
    code: str
    message: str
    details: Any | None = None


class ApiEnvelope(BaseModel, Generic[T]):
    data: T | None
    meta: dict[str, Any] = Field(default_factory=dict)
    error: ApiError | None = None


def success(data: T, meta: dict[str, Any] | None = None) -> ApiEnvelope[T]:
    return ApiEnvelope(data=data, meta=meta or {}, error=None)


def failure(
    code: str,
    message: str,
    details: Any | None = None,
    meta: dict[str, Any] | None = None,
) -> ApiEnvelope[None]:
    return ApiEnvelope(
        data=None,
        meta=meta or {},
        error=ApiError(code=code, message=message, details=details),
    )
