from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.deps import get_locale, get_pokemon_service
from app.schemas.common import ApiEnvelope, success
from app.schemas.domain import (
    Location,
    LocationDetail,
    Move,
    MoveDetail,
    Pokemon,
    PokemonListItem,
    PokemonMove,
)
from app.services.pokemon_service import PokemonService

router = APIRouter()


@router.get("/health", response_model=ApiEnvelope[dict[str, str]])
def healthcheck() -> ApiEnvelope[dict[str, str]]:
    return success({"status": "ok"})


@router.get("/pokemon", response_model=ApiEnvelope[list[PokemonListItem]])
def list_pokemon(
    q: str | None = Query(default=None),
    type: str | None = Query(default=None),
    ev_yield: str | None = Query(default=None),
    hoenn_only: bool = Query(default=False),
    move: str | None = Query(default=None),
    limit: int = Query(default=24, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    service: PokemonService = Depends(get_pokemon_service),
) -> ApiEnvelope[list[PokemonListItem]]:
    pokemon_types = [item.strip().lower() for item in (type or "").split(",") if item.strip()]
    data, total = service.search_pokemon(
        q=q,
        pokemon_types=pokemon_types or None,
        ev_yield=ev_yield,
        hoenn_only=hoenn_only,
        move=move,
        limit=limit,
        offset=offset,
    )
    return success(data=data, meta={"total": total, "limit": limit, "offset": offset})


@router.get("/pokemon/{pokemon_id}", response_model=ApiEnvelope[Pokemon])
def get_pokemon(
    pokemon_id: int,
    locale: str = Depends(get_locale),
    service: PokemonService = Depends(get_pokemon_service),
) -> ApiEnvelope[Pokemon]:
    pokemon = service.get_pokemon(pokemon_id, locale=locale)
    if not pokemon:
        raise HTTPException(status_code=404, detail=f"Pokemon '{pokemon_id}' not found")
    return success(data=pokemon)


@router.get("/pokemon/{pokemon_id}/moves", response_model=ApiEnvelope[list[PokemonMove]])
def list_pokemon_moves(
    pokemon_id: int,
    locale: str = Depends(get_locale),
    service: PokemonService = Depends(get_pokemon_service),
) -> ApiEnvelope[list[PokemonMove]]:
    pokemon = service.get_pokemon(pokemon_id)
    if not pokemon:
        raise HTTPException(status_code=404, detail=f"Pokemon '{pokemon_id}' not found")
    moves = service.list_pokemon_moves(pokemon_id, locale=locale)
    return success(data=moves, meta={"total": len(moves)})


@router.get("/moves", response_model=ApiEnvelope[list[Move]])
def list_moves(
    locale: str = Depends(get_locale),
    service: PokemonService = Depends(get_pokemon_service),
) -> ApiEnvelope[list[Move]]:
    moves = service.list_moves(locale=locale)
    return success(data=moves, meta={"total": len(moves)})


@router.get("/moves/{move_name}", response_model=ApiEnvelope[MoveDetail])
def get_move_detail(
    move_name: str,
    locale: str = Depends(get_locale),
    service: PokemonService = Depends(get_pokemon_service),
) -> ApiEnvelope[MoveDetail]:
    move_detail = service.get_move_detail(move_name, locale=locale)
    if not move_detail:
        raise HTTPException(status_code=404, detail=f"Move '{move_name}' not found")
    return success(data=move_detail)


@router.get("/locations", response_model=ApiEnvelope[list[Location]])
def list_locations(
    locale: str = Depends(get_locale),
    service: PokemonService = Depends(get_pokemon_service),
) -> ApiEnvelope[list[Location]]:
    locations = service.list_locations(locale=locale)
    return success(data=locations, meta={"total": len(locations)})


@router.get("/locations/pokemmo/hoenn", response_model=ApiEnvelope[list[Location]])
def list_pokemmo_hoenn_locations(
    locale: str = Depends(get_locale),
    service: PokemonService = Depends(get_pokemon_service),
) -> ApiEnvelope[list[Location]]:
    locations = service.list_pokemmo_hoenn_locations(locale=locale)
    return success(data=locations, meta={"total": len(locations), "source": "pokemmo", "region": "hoenn"})


@router.get("/locations/pokemmo/hoenn/{location_name}", response_model=ApiEnvelope[LocationDetail])
def get_pokemmo_hoenn_location(
    location_name: str,
    locale: str = Depends(get_locale),
    service: PokemonService = Depends(get_pokemon_service),
) -> ApiEnvelope[LocationDetail]:
    location = service.get_pokemmo_hoenn_location(location_name, locale=locale)
    if not location:
        raise HTTPException(status_code=404, detail=f"Location '{location_name}' not found")
    return success(data=location)


@router.get("/meta/types", response_model=ApiEnvelope[list[str]])
def list_types(service: PokemonService = Depends(get_pokemon_service)) -> ApiEnvelope[list[str]]:
    types = service.list_types()
    return success(data=types, meta={"total": len(types)})
