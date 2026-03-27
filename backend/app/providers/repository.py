from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

from pydantic import TypeAdapter

from app.schemas.domain import (
    Location,
    LocationEncounter,
    LocationDetail,
    Move,
    MoveDetail,
    MoveLearnMethod,
    MoveTmPurchase,
    MoveTmPurchaseOption,
    Pokemon,
    PokemonListItem,
    PokemonMove,
)

HOENN_LOCATION_PREFIXES = (
    "hoenn-route-",
    "hoenn-victory-road-",
    "granite-cave-",
    "meteor-falls-",
    "rusturf-tunnel-",
    "petalburg-woods-",
    "mt-pyre-",
    "cave-of-origin-",
    "sky-pillar-",
    "shoal-cave-",
    "seafloor-cavern-",
    "fiery-path-",
    "jagged-pass-",
    "desert-ruins-",
    "island-cave-",
    "ancient-tomb-",
)

HOENN_AGGREGATED_PREFIXES = tuple(
    prefix for prefix in HOENN_LOCATION_PREFIXES if prefix != "hoenn-route-"
)

EXCLUDED_LOCATION_TOKENS = (
    "north-oras",
    "south-oras",
    "weather-institute",
    "pokecenter",
)

NON_CAPTURABLE_POKEMON_IDS = {
    252,  # Treecko (starter)
    255,  # Torchic (starter)
    258,  # Mudkip (starter)
    351,  # Castform (gift)
    377,  # Regirock
    378,  # Regice
    379,  # Registeel
    380,  # Latias
    381,  # Latios
    382,  # Kyogre
    383,  # Groudon
    384,  # Rayquaza
    385,  # Jirachi
    386,  # Deoxys
}

LEGENDARY_POKEMON_IDS = {
    144,  # Articuno
    145,  # Zapdos
    146,  # Moltres
    150,  # Mewtwo
    151,  # Mew
    243,  # Raikou
    244,  # Entei
    245,  # Suicune
    249,  # Lugia
    250,  # Ho-Oh
    251,  # Celebi
    377,  # Regirock
    378,  # Regice
    379,  # Registeel
    380,  # Latias
    381,  # Latios
    382,  # Kyogre
    383,  # Groudon
    384,  # Rayquaza
    385,  # Jirachi
    386,  # Deoxys
}

GEN3_START = 252
GEN3_END = 386


class DataRepository:
    def __init__(self, data_dir: Path) -> None:
        self.data_dir = data_dir
        self.pokemon: list[Pokemon] = []
        self.moves: list[Move] = []
        self.moves_by_name: dict[str, Move] = {}
        self.move_details: dict[str, MoveDetail] = {}
        self.move_tm_by_name: dict[str, MoveTmPurchase] = {}
        self.move_methods_by_move: dict[str, dict[int, list[MoveLearnMethod]]] = {}
        self.locations: list[Location] = []
        self.locations_by_name: dict[str, Location] = {}
        self.pokemmo_hoenn_locations: list[LocationDetail] = []
        self.pokemmo_hoenn_by_name: dict[str, LocationDetail] = {}
        self.pokemmo_hoenn_locations_mtime: float | None = None
        self.location_visual_cache: dict[str, dict[str, object]] = {}
        self.it_move_display_by_slug: dict[str, str] = {}
        self.it_move_description_by_slug: dict[str, str] = {}
        self.it_ability_display_by_slug: dict[str, str] = {}
        self.it_ability_description_by_slug: dict[str, str] = {}
        self.it_location_display_by_slug: dict[str, str] = {}
        self.it_location_display_by_en: dict[str, str] = {}

        self.by_id: dict[int, Pokemon] = {}
        self.by_name: dict[str, Pokemon] = {}
        self.by_type: dict[str, list[Pokemon]] = {}
        self.by_move: dict[str, list[Pokemon]] = {}

    def load(self) -> None:
        self.pokemon = TypeAdapter(list[Pokemon]).validate_python(
            self._load_json("pokemon.json")
        )
        self.moves = TypeAdapter(list[Move]).validate_python(self._load_json("moves.json"))
        self.moves_by_name = {move.name.lower(): move for move in self.moves}
        parsed_move_details = TypeAdapter(list[MoveDetail]).validate_python(
            self._load_json("move_details.json")
        )
        self.move_details = {
            detail.name.lower(): detail for detail in parsed_move_details
        }
        self.move_tm_by_name = self._load_move_tm_catalog()
        self.move_methods_by_move = {
            detail.name.lower(): {
                learner.pokemon_id: learner.methods for learner in detail.learners
            }
            for detail in parsed_move_details
        }
        self.locations = TypeAdapter(list[Location]).validate_python(
            self._load_json("locations.json")
        )
        self._reload_pokemmo_hoenn_locations(force=True)
        self.locations_by_name = {location.name: location for location in self.locations}
        self._load_it_localizations()
        self._build_indexes()

    def _load_it_localizations(self) -> None:
        payload = self._load_json_object_optional("localization_it.json")
        self.it_move_display_by_slug = {}
        self.it_move_description_by_slug = {}
        self.it_ability_display_by_slug = {}
        self.it_ability_description_by_slug = {}
        self.it_location_display_by_slug = {}
        self.it_location_display_by_en = {}
        if not payload:
            return

        moves = payload.get("moves")
        if isinstance(moves, dict):
            for slug, row in moves.items():
                if not isinstance(row, dict):
                    continue
                key = str(slug).strip().lower()
                if not key:
                    continue
                display_name = str(row.get("display_name") or "").strip()
                description = str(row.get("description") or "").strip()
                if display_name:
                    self.it_move_display_by_slug[key] = display_name
                if description:
                    self.it_move_description_by_slug[key] = description

        abilities = payload.get("abilities")
        if isinstance(abilities, dict):
            for slug, row in abilities.items():
                if not isinstance(row, dict):
                    continue
                key = str(slug).strip().lower()
                if not key:
                    continue
                display_name = str(row.get("display_name") or "").strip()
                description = str(row.get("description") or "").strip()
                if display_name:
                    self.it_ability_display_by_slug[key] = display_name
                if description:
                    self.it_ability_description_by_slug[key] = description

        locations = payload.get("locations")
        if isinstance(locations, dict):
            for slug, display in locations.items():
                key = str(slug).strip()
                if not key:
                    continue
                display_name = str(display or "").strip()
                if not display_name:
                    continue
                self.it_location_display_by_slug[key] = display_name
                english_name = self._format_location_display_name(key)
                self.it_location_display_by_en[english_name] = display_name

    def _reload_pokemmo_hoenn_locations(self, force: bool = False) -> None:
        file_path = self.data_dir / "pokemmo_hoenn_locations.json"
        if not file_path.exists():
            self.pokemmo_hoenn_locations = []
            self.pokemmo_hoenn_by_name = {}
            self.pokemmo_hoenn_locations_mtime = None
            return

        try:
            current_mtime = file_path.stat().st_mtime
        except OSError:
            return

        if (
            not force
            and self.pokemmo_hoenn_locations_mtime is not None
            and current_mtime <= self.pokemmo_hoenn_locations_mtime
        ):
            return

        self.pokemmo_hoenn_locations = TypeAdapter(list[LocationDetail]).validate_python(
            self._load_json_optional("pokemmo_hoenn_locations.json")
        )
        self.pokemmo_hoenn_by_name = {
            location.name: location for location in self.pokemmo_hoenn_locations
        }
        self.pokemmo_hoenn_locations_mtime = current_mtime

    def _load_json(self, name: str) -> list[dict]:
        file_path = self.data_dir / name
        if not file_path.exists():
            raise FileNotFoundError(
                f"Missing {file_path}. Run scripts/build_data.py to generate data files."
            )
        with file_path.open("r", encoding="utf-8") as file:
            data = json.load(file)
        if not isinstance(data, list):
            raise ValueError(f"Expected list in {file_path}")
        return data

    def _load_json_optional(self, name: str) -> list[dict]:
        file_path = self.data_dir / name
        if not file_path.exists():
            return []
        with file_path.open("r", encoding="utf-8") as file:
            data = json.load(file)
        if not isinstance(data, list):
            raise ValueError(f"Expected list in {file_path}")
        return data

    def _load_json_object_optional(self, name: str) -> dict:
        file_path = self.data_dir / name
        if not file_path.exists():
            return {}
        with file_path.open("r", encoding="utf-8") as file:
            data = json.load(file)
        if not isinstance(data, dict):
            raise ValueError(f"Expected object in {file_path}")
        return data

    def _build_indexes(self) -> None:
        self.by_id.clear()
        self.by_name.clear()
        self.by_type.clear()
        self.by_move.clear()

        for pokemon in self.pokemon:
            self.by_id[pokemon.id] = pokemon
            self.by_name[pokemon.name.lower()] = pokemon

            for pokemon_type in pokemon.types:
                key = pokemon_type.lower()
                self.by_type.setdefault(key, []).append(pokemon)

            for move in pokemon.moves:
                key = move.lower()
                self.by_move.setdefault(key, []).append(pokemon)

    def _load_move_tm_catalog(self) -> dict[str, MoveTmPurchase]:
        rows = self._load_json_optional("move_tm_hoenn_lookup.json")
        catalog: dict[str, MoveTmPurchase] = {}

        for row in rows:
            if not isinstance(row, dict):
                continue
            if not row.get("exists_as_tm"):
                continue

            move_slug = str(row.get("move_slug") or "").strip().lower()
            location = str(row.get("hoenn_purchase_location") or "").strip()
            if not move_slug or not location:
                continue

            raw_price_value = row.get("price_pokeyen")
            if isinstance(raw_price_value, int):
                price_value = raw_price_value
            elif isinstance(raw_price_value, str) and raw_price_value.isdigit():
                price_value = int(raw_price_value)
            else:
                price_value = None

            price_text = row.get("price_text")
            if price_text is not None:
                price_text = str(price_text).strip() or None

            secondary_location = row.get("secondary_hoenn_purchase_location")
            if secondary_location is not None:
                secondary_location = str(secondary_location).strip() or None

            secondary_raw_price_value = row.get("secondary_price_pokeyen")
            if isinstance(secondary_raw_price_value, int):
                secondary_price_value = secondary_raw_price_value
            elif (
                isinstance(secondary_raw_price_value, str)
                and secondary_raw_price_value.isdigit()
            ):
                secondary_price_value = int(secondary_raw_price_value)
            else:
                secondary_price_value = None

            secondary_price_text = row.get("secondary_price_text")
            if secondary_price_text is not None:
                secondary_price_text = str(secondary_price_text).strip() or None

            secondary_option = None
            if secondary_location:
                secondary_option = MoveTmPurchaseOption(
                    location=secondary_location,
                    price_pokeyen=secondary_price_value,
                    price_text=secondary_price_text,
                )

            catalog[move_slug] = MoveTmPurchase(
                location=location,
                price_pokeyen=price_value,
                price_text=price_text,
                secondary=secondary_option,
            )

        return catalog

    def query_pokemon(
        self,
        q: str | None,
        pokemon_types: list[str] | None,
        ev_yield: str | None,
        hoenn_only: bool,
        move: str | None,
        limit: int,
        offset: int,
    ) -> tuple[list[PokemonListItem], int]:
        ids: set[int] | None = None

        if pokemon_types:
            normalized_types = [item.strip().lower() for item in pokemon_types if item.strip()]
            if normalized_types:
                type_sets = [
                    {pokemon.id for pokemon in self.by_type.get(pokemon_type, [])}
                    for pokemon_type in normalized_types
                ]
                type_ids = set.intersection(*type_sets) if type_sets else set()
                ids = type_ids

        if move:
            move_ids = {pokemon.id for pokemon in self.by_move.get(move.lower(), [])}
            ids = move_ids if ids is None else ids & move_ids

        if ev_yield:
            ev_key = ev_yield.lower().strip()
            ev_ids = {
                pokemon.id
                for pokemon in self.pokemon
                if (pokemon.ev_yield.get(ev_key) or 0) > 0
            }
            ids = ev_ids if ids is None else ids & ev_ids

        if hoenn_only:
            hoenn_ids = {
                pokemon.id for pokemon in self.pokemon if GEN3_START <= pokemon.id <= GEN3_END
            }
            ids = hoenn_ids if ids is None else ids & hoenn_ids

        if ids is None:
            candidates = self.pokemon
        else:
            candidates = [self.by_id[pokemon_id] for pokemon_id in sorted(ids)]

        if q:
            needle = q.strip().lower()
            number_query = needle[1:] if needle.startswith("#") else needle
            is_numeric_query = number_query.isdigit()

            def matches_query(pokemon: Pokemon) -> bool:
                if needle in pokemon.name.lower():
                    return True
                if not is_numeric_query:
                    return False

                pokemon_id = str(pokemon.id)
                return number_query in pokemon_id or number_query in pokemon_id.zfill(3)

            candidates = [pokemon for pokemon in candidates if matches_query(pokemon)]

        candidates = [
            pokemon
            for pokemon in candidates
            if pokemon.id not in LEGENDARY_POKEMON_IDS
        ]
        candidates = sorted(candidates, key=lambda pokemon: pokemon.id)
        total = len(candidates)
        page = candidates[offset : offset + limit]

        list_items = [
            PokemonListItem(
                id=pokemon.id,
                name=pokemon.name,
                types=pokemon.types,
                ev_yield=pokemon.ev_yield,
                sprite=(
                    pokemon.sprites.get("official_artwork")
                    or pokemon.sprites.get("front_default")
                ),
            )
            for pokemon in page
        ]

        return list_items, total

    def get_pokemon(self, identifier: int | str, locale: str = "en") -> Pokemon | None:
        if isinstance(identifier, int) or str(identifier).isdigit():
            pokemon = self.by_id.get(int(identifier))
        else:
            pokemon = self.by_name.get(str(identifier).lower())
        if not pokemon:
            return None
        if locale != "it":
            return pokemon
        return self._localize_pokemon(pokemon, locale=locale)

    def _localize_pokemon(self, pokemon: Pokemon, locale: str) -> Pokemon:
        if locale != "it":
            return pokemon

        localized_abilities = [
            ability.model_copy(
                update={
                    "display_name": self.it_ability_display_by_slug.get(ability.name.lower()),
                    "description": self.it_ability_description_by_slug.get(
                        ability.name.lower(),
                        ability.description,
                    ),
                }
            )
            for ability in pokemon.abilities
        ]
        return pokemon.model_copy(update={"abilities": localized_abilities})

    def list_moves(self, locale: str = "en") -> list[Move]:
        rows = sorted(self.moves, key=lambda move: move.name)
        if locale != "it":
            return [
                move.model_copy(
                    update={
                        "type": self._legacy_move_type(move.name, move.type),
                    }
                )
                for move in rows
            ]
        return [
            move.model_copy(
                update={
                    "type": self._legacy_move_type(move.name, move.type),
                    "display_name": self.it_move_display_by_slug.get(move.name.lower()),
                }
            )
            for move in rows
        ]

    def get_move_detail(self, move_name: str, locale: str = "en") -> MoveDetail | None:
        normalized_name = move_name.lower()
        move_detail = self.move_details.get(normalized_name)
        if not move_detail:
            return None

        tm_purchase = self.move_tm_by_name.get(normalized_name)
        filtered_learners = [
            learner
            for learner in move_detail.learners
            if learner.pokemon_id not in LEGENDARY_POKEMON_IDS
        ]

        updates: dict[str, object] = {}
        if tm_purchase:
            updates["tm_purchase"] = tm_purchase
        if len(filtered_learners) != len(move_detail.learners):
            updates["learners"] = filtered_learners
        if locale == "it":
            updates["display_name"] = self.it_move_display_by_slug.get(normalized_name)
            updates["description"] = self.it_move_description_by_slug.get(normalized_name)
            if tm_purchase:
                updates["tm_purchase"] = self._localize_tm_purchase(tm_purchase, locale=locale)

        if not updates:
            return move_detail
        return move_detail.model_copy(update=updates)

    def list_pokemon_moves(self, pokemon_id: int, locale: str = "en") -> list[PokemonMove]:
        pokemon = self.by_id.get(pokemon_id)
        if not pokemon:
            return []

        rows: list[PokemonMove] = []
        for move_name in sorted(pokemon.moves):
            normalized_name = move_name.lower()
            move_meta = self.moves_by_name.get(normalized_name)
            move_detail = self.move_details.get(normalized_name)
            methods = self.move_methods_by_move.get(normalized_name, {}).get(
                pokemon_id, []
            )
            rows.append(
                PokemonMove(
                    name=move_name,
                    display_name=(
                        self.it_move_display_by_slug.get(normalized_name)
                        if locale == "it"
                        else None
                    ),
                    type=(
                        self._legacy_move_type(move_name, move_meta.type)
                        if move_meta
                        else None
                    ),
                    category=move_meta.category if move_meta else None,
                    power=move_meta.power if move_meta else None,
                    pp=move_meta.pp if move_meta else None,
                    accuracy=move_meta.accuracy if move_meta else None,
                    description=(
                        self.it_move_description_by_slug.get(normalized_name)
                        if locale == "it"
                        else move_detail.description if move_detail else None
                    ),
                    methods=methods,
                )
            )
        return rows

    def list_locations(self, locale: str = "en") -> list[Location]:
        rows = sorted(self.locations, key=lambda location: location.name)
        if locale != "it":
            return rows
        return [
            location.model_copy(
                update={
                    "display_name": self._localized_location_display_name(location.name, locale),
                }
            )
            for location in rows
        ]

    def list_pokemmo_hoenn_locations(self, locale: str = "en") -> list[Location]:
        self._reload_pokemmo_hoenn_locations()
        grouped_ids: dict[str, set[int]] = {}
        if self.pokemmo_hoenn_by_name:
            supported_names = set(self.pokemmo_hoenn_by_name.keys())
        else:
            supported_names = {
                self._normalize_location_key(location.name)
                for location in self.locations
                if self._is_supported_hoenn_location(location.name)
            }

        for normalized_name in sorted(supported_names):
            pokemon_ids: set[int] = set()
            source_names = self._expand_location_aliases(normalized_name)

            # Prefer persisted Hoenn encounter data (Emerald-aligned), then fallback.
            detail_candidates = [self.pokemmo_hoenn_by_name.get(normalized_name)] + [
                self.pokemmo_hoenn_by_name.get(source_name) for source_name in source_names
            ]
            for detail in detail_candidates:
                if not detail:
                    continue
                for encounter in detail.encounters:
                    if encounter.pokemon_id is None:
                        continue
                    if encounter.pokemon_id in NON_CAPTURABLE_POKEMON_IDS:
                        continue
                    pokemon_ids.add(encounter.pokemon_id)

            if not pokemon_ids:
                for source_name in source_names:
                    location = self.locations_by_name.get(source_name)
                    if not location:
                        continue
                    for pokemon_id in location.pokemon_ids:
                        if pokemon_id in NON_CAPTURABLE_POKEMON_IDS:
                            continue
                        pokemon_ids.add(pokemon_id)

            if not pokemon_ids:
                continue
            grouped_ids[normalized_name] = pokemon_ids

        rows = [
            Location(
                name=name,
                display_name=self._localized_location_display_name(name, locale),
                pokemon_ids=sorted(ids),
            )
            for name, ids in grouped_ids.items()
            if ids
        ]
        return sorted(rows, key=lambda location: location.name)

    def get_pokemmo_hoenn_location(
        self,
        location_name: str,
        locale: str = "en",
    ) -> LocationDetail | None:
        self._reload_pokemmo_hoenn_locations()
        normalized_name = self._normalize_location_key(location_name)
        if self.pokemmo_hoenn_by_name and normalized_name not in self.pokemmo_hoenn_by_name:
            return None
        persisted_detail = self.pokemmo_hoenn_by_name.get(normalized_name)
        if not self._is_supported_hoenn_location(location_name) and not persisted_detail:
            return None

        source_names = self._expand_location_aliases(location_name)
        base_locations = [self.locations_by_name[name] for name in source_names if name in self.locations_by_name]
        if not base_locations and not persisted_detail:
            return None

        if persisted_detail and (
            persisted_detail.birdview_image_url
            or persisted_detail.birdview_images
            or persisted_detail.map_image_url
            or persisted_detail.source_url
        ):
            persisted_birdview_images = [
                image.model_dump() for image in persisted_detail.birdview_images
            ]
            if not persisted_birdview_images and persisted_detail.birdview_image_url:
                persisted_birdview_images = [
                    {
                        "label": self._format_location_display_name(normalized_name),
                        "image_url": persisted_detail.birdview_image_url,
                        "source_url": persisted_detail.birdview_source_url,
                    }
                ]
            primary_birdview_image_url = persisted_detail.birdview_image_url
            primary_birdview_source_url = persisted_detail.birdview_source_url
            if not primary_birdview_image_url and persisted_birdview_images:
                first = persisted_birdview_images[0]
                primary_birdview_image_url = first.get("image_url")
                primary_birdview_source_url = first.get("source_url")
            visual = {
                "birdview_image_url": primary_birdview_image_url,
                "birdview_source_url": primary_birdview_source_url,
                "birdview_images": persisted_birdview_images,
                "map_image_url": persisted_detail.map_image_url,
                "map_source_url": persisted_detail.map_source_url,
                "source_url": persisted_detail.source_url,
            }
        else:
            visual = self._build_location_visuals(normalized_name)

        encounters = []
        normalized_detail = self.pokemmo_hoenn_by_name.get(normalized_name)
        if normalized_detail:
            for encounter in normalized_detail.encounters:
                if (
                    encounter.pokemon_id is not None
                    and encounter.pokemon_id in NON_CAPTURABLE_POKEMON_IDS
                ):
                    continue
                encounters.append(encounter)

        for source_name in source_names:
            detail = self.pokemmo_hoenn_by_name.get(source_name)
            if not detail:
                continue
            for encounter in detail.encounters:
                if (
                    encounter.pokemon_id is not None
                    and encounter.pokemon_id in NON_CAPTURABLE_POKEMON_IDS
                ):
                    continue
                encounters.append(encounter)

        if not encounters:
            ids = sorted(
                {
                    pokemon_id
                    for location in base_locations
                    for pokemon_id in location.pokemon_ids
                    if pokemon_id not in NON_CAPTURABLE_POKEMON_IDS
                }
            )
            encounters = self._fallback_encounters(ids)
        else:
            deduped = {
                (
                    encounter.pokemon_name,
                    encounter.pokemon_id,
                    encounter.sub_location,
                    encounter.level_range,
                    encounter.method,
                    encounter.rate,
                    encounter.period,
                    encounter.category,
                ): encounter
                for encounter in encounters
            }
            encounters = [
                deduped[key]
                for key in sorted(
                    deduped.keys(),
                    key=lambda row: (
                        str(row[0]).lower(),
                        str(row[4]).lower(),
                        str(row[2]).lower(),
                        str(row[3]).lower(),
                        str(row[5] or "").lower(),
                        str(row[6] or "").lower(),
                    ),
                )
            ]

        return LocationDetail(
            name=normalized_name,
            display_name=self._localized_location_display_name(normalized_name, locale),
            birdview_image_url=visual["birdview_image_url"],
            birdview_source_url=visual["birdview_source_url"],
            birdview_images=visual["birdview_images"],
            map_image_url=visual["map_image_url"],
            map_source_url=visual["map_source_url"],
            source_url=visual["source_url"],
            encounters=self._localize_encounters(encounters, normalized_name, locale),
        )

    def _localized_location_display_name(self, location_name: str, locale: str) -> str:
        if locale != "it":
            return self._format_location_display_name(location_name)
        return self.it_location_display_by_slug.get(
            location_name,
            self._format_location_display_name(location_name),
        )

    def _localize_tm_purchase(
        self,
        tm_purchase: MoveTmPurchase,
        locale: str,
    ) -> MoveTmPurchase:
        if locale != "it":
            return tm_purchase
        secondary = None
        if tm_purchase.secondary:
            secondary = tm_purchase.secondary.model_copy(
                update={
                    "location": self._localize_freeform_location_text(
                        tm_purchase.secondary.location,
                        locale,
                    )
                }
            )
        return tm_purchase.model_copy(
            update={
                "location": self._localize_freeform_location_text(tm_purchase.location, locale),
                "secondary": secondary,
            }
        )

    def _localize_encounters(
        self,
        encounters: list[LocationEncounter] | list[dict],
        location_name: str,
        locale: str,
    ) -> list[LocationEncounter]:
        rows = TypeAdapter(list[LocationEncounter]).validate_python(encounters)
        if locale != "it":
            return rows

        period_map = {
            "Any": "Qualsiasi",
            "Morning": "Mattina",
            "Day": "Giorno",
            "Night": "Notte",
        }
        category_map = {
            "Wild": "Selvatico",
        }
        rate_map = {
            "Very Common": "Molto comune",
            "Common": "Comune",
            "Uncommon": "Non comune",
            "Rare": "Raro",
            "Very Rare": "Molto raro",
            "Horde": "Orda",
            "Lure": "Aroma",
            "Unknown": "Sconosciuto",
        }
        method_map = {
            "Old Rod": "Amo Vecchio",
            "Good Rod": "Amo Buono",
            "Super Rod": "Super Amo",
            "Surf": "Surf",
            "Rock Smash": "Spaccaroccia",
            "Headbutt": "Bottintesta",
            "Walk": "Cammina",
            "Unknown": "Sconosciuto",
            "Gift": "Dono",
            "Special": "Speciale",
            "Underwater": "Subacqueo",
        }

        localized: list[LocationEncounter] = []
        base_english_name = self._format_location_display_name(location_name)
        base_italian_name = self._localized_location_display_name(location_name, locale)

        for encounter in rows:
            sub_location = encounter.sub_location
            if sub_location:
                if sub_location == base_english_name:
                    sub_location = base_italian_name
                else:
                    sub_location = self._localize_freeform_location_text(sub_location, locale)
            localized.append(
                encounter.model_copy(
                    update={
                        "sub_location": sub_location,
                        "method": method_map.get(encounter.method, encounter.method),
                        "rate": rate_map.get(encounter.rate, encounter.rate),
                        "period": period_map.get(encounter.period, encounter.period),
                        "category": category_map.get(encounter.category, encounter.category),
                    }
                )
            )
        return localized

    def _localize_freeform_location_text(self, value: str, locale: str) -> str:
        if locale != "it":
            return value
        translated = value
        for english, italian in sorted(
            self.it_location_display_by_en.items(),
            key=lambda item: len(item[0]),
            reverse=True,
        ):
            translated = translated.replace(english, italian)

        translated = re.sub(r"\bRoute\s+(\d+)\b", r"Percorso \1", translated)
        translated = translated.replace("Pokémon Marts", "Poké Market")
        translated = translated.replace("Dept. Store", "Grande Emporio")
        translated = translated.replace("(4th Floor TM Shop)", "(4º Piano - Negozio MT)")
        translated = translated.replace("Game Corners", "Casinò")
        translated = re.sub(r"\bfor\b", "per", translated)
        translated = translated.replace("coins", "gettoni")
        return translated

    def _legacy_move_type(self, _move_name: str, move_type: str | None) -> str | None:
        if not move_type:
            return move_type
        # PokéMMO Gen2-5 typing has no Fairy type; legacy fallback is Normal.
        if move_type.lower() == "fairy":
            return "normal"
        return move_type

    def _fallback_encounters(self, pokemon_ids: list[int]):
        rows = []
        for pokemon_id in sorted(set(pokemon_ids)):
            pokemon = self.by_id.get(pokemon_id)
            rows.append(
                {
                    "pokemon_name": pokemon.name.capitalize() if pokemon else f"Pokemon {pokemon_id}",
                    "pokemon_id": pokemon_id,
                    "sub_location": None,
                    "level_range": "Unknown",
                    "method": "Unknown",
                    "rate": "Unknown",
                    "period": None,
                    "category": "Wild",
                }
            )
        return rows

    def _normalize_location_key(self, location_name: str) -> str:
        for prefix in HOENN_AGGREGATED_PREFIXES:
            if location_name.startswith(prefix):
                return f"{prefix[:-1]}-area"
        return location_name

    def _expand_location_aliases(self, location_name: str) -> list[str]:
        normalized_name = self._normalize_location_key(location_name)
        matches = sorted(
            {
                location.name
                for location in self.locations
                if self._is_supported_hoenn_location(location.name)
                and self._normalize_location_key(location.name) == normalized_name
            }
        )
        if matches:
            return matches
        if location_name in self.locations_by_name:
            return [location_name]
        return []

    def _is_supported_hoenn_location(self, location_name: str) -> bool:
        if any(token in location_name for token in EXCLUDED_LOCATION_TOKENS):
            return False
        normalized_name = self._normalize_location_key(location_name)
        if (
            location_name in self.pokemmo_hoenn_by_name
            or normalized_name in self.pokemmo_hoenn_by_name
        ):
            return True
        return any(location_name.startswith(prefix) for prefix in HOENN_LOCATION_PREFIXES)

    def _format_location_display_name(self, location_name: str) -> str:
        segments = [segment for segment in location_name.replace("hoenn-", "").split("-") if segment]
        if segments and segments[-1] == "area":
            segments = segments[:-1]

        rendered = []
        for segment in segments:
            if segment == "oras":
                rendered.append("ORAS")
                continue
            if re.fullmatch(r"b?\d+f", segment, flags=re.IGNORECASE):
                rendered.append(segment.upper())
                continue
            merged_floor_match = re.fullmatch(r"(\d+f)([a-z].*)", segment, flags=re.IGNORECASE)
            if merged_floor_match:
                floor = merged_floor_match.group(1).upper()
                trailing = merged_floor_match.group(2).capitalize()
                rendered.extend([floor, trailing])
                continue
            if segment.isdigit():
                rendered.append(segment)
                continue
            rendered.append(segment.capitalize())
        return " ".join(rendered)

    def _mediawiki_upload_url(self, host_root: str, filename: str) -> str:
        digest = hashlib.md5(filename.encode("utf-8")).hexdigest()
        return f"{host_root}/{digest[0]}/{digest[:2]}/{filename}"

    def _build_location_visuals(self, location_name: str) -> dict[str, object]:
        cached = self.location_visual_cache.get(location_name)
        if cached:
            return cached

        route_match = re.search(r"hoenn-route-(\d+)", location_name)
        if route_match:
            route = route_match.group(1)
            birdview_filename = f"Hoenn_Route_{route}.png"
            map_filename = f"Hoenn_Route_{route}_Map.png"
            birdview_image_url = self._mediawiki_upload_url(
                "https://images.shoutwiki.com/pokemmo",
                birdview_filename,
            )
            map_image_url = self._mediawiki_upload_url(
                "https://archives.bulbagarden.net/media/upload",
                map_filename,
            )
            visual = {
                "birdview_image_url": birdview_image_url,
                "birdview_source_url": f"https://pokemmo.shoutwiki.com/wiki/File:{birdview_filename}",
                "birdview_images": [
                    {
                        "label": f"Route {route}",
                        "image_url": birdview_image_url,
                        "source_url": f"https://pokemmo.shoutwiki.com/wiki/File:{birdview_filename}",
                    }
                ],
                "map_image_url": map_image_url,
                "map_source_url": (
                    f"https://bulbapedia.bulbagarden.net/wiki/Hoenn_Route_{route}"
                    f"#/media/File:{map_filename}"
                ),
                "source_url": f"https://pokemmo.fandom.com/wiki/Route_{route}",
            }
            self.location_visual_cache[location_name] = visual
            return visual

        if location_name.startswith("hoenn-victory-road-"):
            floor = "1F"
            floor_match = re.search(r"hoenn-victory-road-([a-z0-9]+)$", location_name)
            if floor_match:
                floor = floor_match.group(1).upper()

            birdview_filename = f"Hoenn_Victory_Road_{floor}.png"
            map_filename = "Hoenn_Victory_Road_Map.png"
            visual = {
                "birdview_image_url": self._mediawiki_upload_url(
                    "https://images.shoutwiki.com/pokemmo",
                    birdview_filename,
                ),
                "birdview_source_url": f"https://pokemmo.shoutwiki.com/wiki/File:{birdview_filename}",
                "birdview_images": [
                    {
                        "label": self._format_location_display_name(location_name),
                        "image_url": self._mediawiki_upload_url(
                            "https://images.shoutwiki.com/pokemmo",
                            birdview_filename,
                        ),
                        "source_url": f"https://pokemmo.shoutwiki.com/wiki/File:{birdview_filename}",
                    }
                ],
                "map_image_url": self._mediawiki_upload_url(
                    "https://archives.bulbagarden.net/media/upload",
                    map_filename,
                ),
                "map_source_url": (
                    "https://bulbapedia.bulbagarden.net/wiki/Victory_Road_(Hoenn)"
                    "#/media/File:Hoenn_Victory_Road_Map.png"
                ),
                "source_url": "https://pokemmo.fandom.com/wiki/Victory_Road_(Hoenn)",
            }
            self.location_visual_cache[location_name] = visual
            return visual

        page_title = self._hoenn_page_title(location_name)
        page_slug = page_title.replace(" ", "_")
        birdview_image_url = self._wiki_page_thumbnail(
            "https://pokemmo.shoutwiki.com/w/api.php", page_title
        )
        map_image_url = self._wiki_page_thumbnail(
            "https://bulbapedia.bulbagarden.net/w/api.php", page_title
        )

        if not birdview_image_url:
            birdview_filename = f"{page_title.replace(' ', '_')}.png"
            birdview_image_url = self._mediawiki_upload_url(
                "https://images.shoutwiki.com/pokemmo",
                birdview_filename,
            )

        visual = {
            "birdview_image_url": birdview_image_url,
            "birdview_source_url": f"https://pokemmo.shoutwiki.com/wiki/{quote(page_slug)}",
            "birdview_images": (
                [
                    {
                        "label": self._format_location_display_name(location_name),
                        "image_url": birdview_image_url,
                        "source_url": f"https://pokemmo.shoutwiki.com/wiki/{quote(page_slug)}",
                    }
                ]
                if birdview_image_url
                else []
            ),
            "map_image_url": map_image_url,
            "map_source_url": f"https://bulbapedia.bulbagarden.net/wiki/{quote(page_slug)}",
            "source_url": f"https://pokemmo.fandom.com/wiki/{quote(page_slug)}",
        }
        self.location_visual_cache[location_name] = visual
        return visual

    def _wiki_page_thumbnail(self, api_url: str, page_title: str) -> str | None:
        params = urlencode(
            {
                "action": "query",
                "titles": page_title,
                "prop": "pageimages",
                "pithumbsize": "1200",
                "format": "json",
            }
        )
        request = Request(
            f"{api_url}?{params}",
            headers={"User-Agent": "Sursk.it/1.0"},
        )
        try:
            with urlopen(request, timeout=20) as response:
                payload = json.loads(response.read().decode("utf-8", "ignore"))
        except Exception:
            return None

        pages = payload.get("query", {}).get("pages", {})
        if not isinstance(pages, dict):
            return None
        page = next(iter(pages.values()), {})
        thumbnail = page.get("thumbnail", {})
        if not isinstance(thumbnail, dict):
            return None
        source = thumbnail.get("source")
        if not isinstance(source, str) or not source:
            return None
        return source

    def _hoenn_page_title(self, location_name: str) -> str:
        base = location_name
        if base.startswith("hoenn-"):
            base = base[len("hoenn-") :]

        for suffix in (
            "-backsmall-room",
            "-high-tide",
            "-low-tide",
            "-outside",
            "-summit",
            "-apex",
            "-back",
            "-1f",
            "-2f",
            "-3f",
            "-4f",
            "-5f",
            "-6f",
            "-b1f",
            "-b2f",
            "-b3f",
            "-b4f",
            "-area",
        ):
            if base.endswith(suffix):
                base = base[: -len(suffix)]
                break

        # Some keys merge floor and area labels (example: "1fsmall-room").
        base = re.sub(r"-(?:b?\d+f[a-z-]*)$", "", base, flags=re.IGNORECASE)

        words = [word for word in base.split("-") if word]
        rendered: list[str] = []
        lower_connectors = {"of", "the", "and"}
        for word in words:
            if word == "mt":
                rendered.append("Mt.")
                continue
            if word in lower_connectors:
                rendered.append(word)
                continue
            rendered.append(word.capitalize())
        return " ".join(rendered)

    def list_types(self) -> list[str]:
        return sorted(self.by_type.keys())
