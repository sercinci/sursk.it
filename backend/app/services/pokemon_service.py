from __future__ import annotations

from app.providers.repository import DataRepository
from app.schemas.domain import (
    Location,
    LocationDetail,
    Move,
    MoveDetail,
    Pokemon,
    PokemonListItem,
    PokemonMove,
)


class PokemonService:
    def __init__(self, repository: DataRepository) -> None:
        self.repository = repository

    def search_pokemon(
        self,
        q: str | None,
        pokemon_types: list[str] | None,
        ev_yield: str | None,
        hoenn_only: bool,
        move: str | None,
        limit: int,
        offset: int,
    ) -> tuple[list[PokemonListItem], int]:
        return self.repository.query_pokemon(
            q=q,
            pokemon_types=pokemon_types,
            ev_yield=ev_yield,
            hoenn_only=hoenn_only,
            move=move,
            limit=limit,
            offset=offset,
        )

    def get_pokemon(self, pokemon_id: int, locale: str = "en") -> Pokemon | None:
        return self.repository.get_pokemon(pokemon_id, locale=locale)

    def list_moves(self, locale: str = "en") -> list[Move]:
        return self.repository.list_moves(locale=locale)

    def get_move_detail(self, move_name: str, locale: str = "en") -> MoveDetail | None:
        return self.repository.get_move_detail(move_name, locale=locale)

    def list_pokemon_moves(self, pokemon_id: int, locale: str = "en") -> list[PokemonMove]:
        return self.repository.list_pokemon_moves(pokemon_id, locale=locale)

    def list_locations(self, locale: str = "en") -> list[Location]:
        return self.repository.list_locations(locale=locale)

    def list_pokemmo_hoenn_locations(self, locale: str = "en") -> list[Location]:
        return self.repository.list_pokemmo_hoenn_locations(locale=locale)

    def get_pokemmo_hoenn_location(
        self,
        location_name: str,
        locale: str = "en",
    ) -> LocationDetail | None:
        return self.repository.get_pokemmo_hoenn_location(location_name, locale=locale)

    def list_types(self) -> list[str]:
        return self.repository.list_types()
