from __future__ import annotations

import base64
import hashlib
import secrets
from typing import Any

import httpx

_oidc_config_cache: dict[str, Any] | None = None


async def get_oidc_config(base_url: str) -> dict[str, Any]:
    global _oidc_config_cache
    if _oidc_config_cache is None:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{base_url}/.well-known/openid-configuration", timeout=10.0
            )
            resp.raise_for_status()
            _oidc_config_cache = resp.json()
    return _oidc_config_cache


def generate_pkce() -> tuple[str, str]:
    verifier = secrets.token_urlsafe(32)
    challenge = (
        base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest())
        .rstrip(b"=")
        .decode()
    )
    return verifier, challenge


def generate_state() -> str:
    return secrets.token_urlsafe(16)


async def exchange_code(
    config: dict[str, Any],
    client_id: str,
    client_secret: str,
    code: str,
    redirect_uri: str,
    verifier: str,
) -> dict[str, Any]:
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            config["token_endpoint"],
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": redirect_uri,
                "client_id": client_id,
                "client_secret": client_secret,
                "code_verifier": verifier,
            },
            timeout=15.0,
        )
        resp.raise_for_status()
        return resp.json()


async def fetch_userinfo(config: dict[str, Any], access_token: str) -> dict[str, Any]:
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            config["userinfo_endpoint"],
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=10.0,
        )
        resp.raise_for_status()
        return resp.json()


async def refresh_access_token(
    config: dict[str, Any],
    client_id: str,
    client_secret: str,
    refresh_token: str,
) -> dict[str, Any]:
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            config["token_endpoint"],
            data={
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
                "client_id": client_id,
                "client_secret": client_secret,
            },
            timeout=15.0,
        )
        resp.raise_for_status()
        return resp.json()


async def revoke_token(
    config: dict[str, Any],
    token: str,
    client_id: str,
    client_secret: str,
) -> None:
    revocation_endpoint = config.get("revocation_endpoint")
    if not revocation_endpoint:
        return
    async with httpx.AsyncClient() as client:
        await client.post(
            revocation_endpoint,
            data={
                "token": token,
                "client_id": client_id,
                "client_secret": client_secret,
            },
            timeout=10.0,
        )
