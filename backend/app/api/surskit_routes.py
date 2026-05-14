from __future__ import annotations

import json
from typing import Any, AsyncIterator

import httpx
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse, StreamingResponse

from app.core.auth import get_oidc_config, refresh_access_token
from app.core.config import XCORE_BASE_URL, XCORE_CLIENT_ID, XCORE_CLIENT_SECRET

router = APIRouter()

XCORE_TIMEOUT = httpx.Timeout(connect=10.0, read=None, write=60.0, pool=10.0)


async def _call_xcore(
    access_token: str,
    body: Any,
) -> tuple[httpx.Response, httpx.AsyncClient]:
    client = httpx.AsyncClient(timeout=XCORE_TIMEOUT)
    req = client.build_request(
        "POST",
        f"{XCORE_BASE_URL}/v1/surskit/matchup",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
        json=body,
    )
    resp = await client.send(req, stream=True)
    return resp, client


async def _try_refresh(request: Request) -> str:
    """Refresh the access token and update the session. Returns new access token."""
    refresh_token = request.session.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Session expired — please log in again")

    try:
        config = await get_oidc_config(XCORE_BASE_URL)
        tokens = await refresh_access_token(config, XCORE_CLIENT_ID, XCORE_CLIENT_SECRET, refresh_token)
    except httpx.HTTPStatusError:
        request.session.clear()
        raise HTTPException(status_code=401, detail="Session expired — please log in again")

    request.session["access_token"] = tokens["access_token"]
    if "refresh_token" in tokens:
        request.session["refresh_token"] = tokens["refresh_token"]

    return tokens["access_token"]


@router.post("/surskit/matchup")
async def surskit_matchup(request: Request) -> StreamingResponse:
    access_token = request.session.get("access_token")
    if not access_token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    body: Any = await request.json()

    # Open the connection and verify status BEFORE returning StreamingResponse.
    # Raising HTTPException inside the async generator would not be caught by
    # FastAPI's exception handler once streaming has started.
    resp, client = await _call_xcore(access_token, body)

    # On 401: refresh token and retry once
    if resp.status_code == 401:
        await resp.aclose()
        await client.aclose()
        access_token = await _try_refresh(request)
        resp, client = await _call_xcore(access_token, body)

    if resp.status_code != 200:
        error_body = await resp.aread()
        await resp.aclose()
        await client.aclose()
        raise HTTPException(status_code=resp.status_code, detail=error_body.decode())

    async def stream_body() -> AsyncIterator[bytes]:
        try:
            async for chunk in resp.aiter_bytes():
                yield chunk
        except Exception as exc:
            yield f"event: error\ndata: {json.dumps({'message': str(exc)})}\n\n".encode()
        finally:
            await resp.aclose()
            await client.aclose()

    return StreamingResponse(stream_body(), media_type="text/event-stream")


async def _xcore_json(method: str, path: str, request: Request, **kwargs: Any) -> JSONResponse:
    """Generic helper for non-streaming xcore calls with refresh-on-401."""
    access_token = request.session.get("access_token")
    if not access_token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    short_timeout = httpx.Timeout(connect=10.0, read=30.0, write=10.0, pool=10.0)

    async def _call(token: str) -> httpx.Response:
        async with httpx.AsyncClient(timeout=short_timeout) as client:
            return await client.request(
                method,
                f"{XCORE_BASE_URL}/v1/surskit{path}",
                headers={"Authorization": f"Bearer {token}"},
                **kwargs,
            )

    resp = await _call(access_token)
    if resp.status_code == 401:
        access_token = await _try_refresh(request)
        resp = await _call(access_token)

    if resp.status_code not in (200, 204):
        raise HTTPException(status_code=resp.status_code, detail=resp.text)

    if resp.status_code == 204:
        return JSONResponse(content=None, status_code=204)
    return JSONResponse(content=resp.json(), status_code=resp.status_code)


@router.get("/surskit/matchup")
async def list_matchup_analyses(request: Request) -> JSONResponse:
    return await _xcore_json("GET", "/matchup", request)


@router.delete("/surskit/matchup/{analysis_id}")
async def delete_matchup_analysis(request: Request, analysis_id: str) -> JSONResponse:
    return await _xcore_json("DELETE", f"/matchup/{analysis_id}", request)
