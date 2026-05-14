from __future__ import annotations

from urllib.parse import urlencode

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import RedirectResponse

from app.core.auth import (
    exchange_code,
    fetch_userinfo,
    generate_pkce,
    generate_state,
    get_oidc_config,
    revoke_token,
)
from app.core.config import (
    XCORE_BASE_URL,
    XCORE_CLIENT_ID,
    XCORE_CLIENT_SECRET,
    XCORE_REDIRECT_URI,
)
from app.schemas.common import ApiEnvelope, success

router = APIRouter()


def _require_auth_config() -> None:
    if not XCORE_CLIENT_ID or not XCORE_CLIENT_SECRET:
        raise HTTPException(status_code=503, detail="OAuth not configured")


@router.get("/auth/login")
async def login(request: Request) -> RedirectResponse:
    _require_auth_config()
    verifier, challenge = generate_pkce()
    state = generate_state()
    request.session["oauth_state"] = state
    request.session["oauth_verifier"] = verifier
    config = await get_oidc_config(XCORE_BASE_URL)
    params = urlencode(
        {
            "response_type": "code",
            "client_id": XCORE_CLIENT_ID,
            "redirect_uri": XCORE_REDIRECT_URI,
            "scope": "openid profile",
            "state": state,
            "code_challenge": challenge,
            "code_challenge_method": "S256",
        }
    )
    return RedirectResponse(f"{config['authorization_endpoint']}?{params}")


@router.get("/auth/callback")
async def callback(
    request: Request,
    code: str | None = Query(default=None),
    state: str | None = Query(default=None),
    error: str | None = Query(default=None),
    error_description: str | None = Query(default=None),
) -> RedirectResponse:
    if error:
        raise HTTPException(status_code=400, detail=error_description or error)

    expected_state = request.session.get("oauth_state")
    if not state or state != expected_state:
        raise HTTPException(status_code=400, detail="Invalid state parameter")

    verifier = request.session.get("oauth_verifier")
    if not verifier:
        raise HTTPException(status_code=400, detail="Missing PKCE verifier")

    if not code:
        raise HTTPException(status_code=400, detail="Missing authorization code")

    config = await get_oidc_config(XCORE_BASE_URL)
    tokens = await exchange_code(
        config, XCORE_CLIENT_ID, XCORE_CLIENT_SECRET, code, XCORE_REDIRECT_URI, verifier
    )
    userinfo = await fetch_userinfo(config, tokens["access_token"])

    request.session["access_token"] = tokens["access_token"]
    request.session["refresh_token"] = tokens.get("refresh_token")
    request.session["user"] = {
        "sub": userinfo.get("sub"),
        "name": userinfo.get("name"),
        "profile": userinfo.get("profile"),
        "picture": userinfo.get("picture"),
    }
    request.session.pop("oauth_state", None)
    request.session.pop("oauth_verifier", None)

    return RedirectResponse("/")


@router.get("/auth/me", response_model=ApiEnvelope[dict])
async def me(request: Request) -> ApiEnvelope[dict]:
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return success(data=user)


@router.post("/auth/logout", response_model=ApiEnvelope[dict])
async def logout(request: Request) -> ApiEnvelope[dict]:
    access_token = request.session.get("access_token")
    if access_token and XCORE_CLIENT_ID:
        try:
            config = await get_oidc_config(XCORE_BASE_URL)
            await revoke_token(config, access_token, XCORE_CLIENT_ID, XCORE_CLIENT_SECRET)
        except Exception:
            pass
    request.session.clear()
    return success(data={"logged_out": True})
