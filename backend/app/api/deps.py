from __future__ import annotations

from fastapi import Query, Request

from app.core.locale import resolve_locale

from app.services.pokemon_service import PokemonService


def get_pokemon_service(request: Request) -> PokemonService:
    return request.app.state.pokemon_service


def get_locale(
    request: Request,
    lang: str | None = Query(default=None),
) -> str:
    return resolve_locale(lang, request.headers.get("accept-language"))
