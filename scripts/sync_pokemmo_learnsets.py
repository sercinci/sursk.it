#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
import zipfile
from argparse import ArgumentParser
from pathlib import Path
from urllib.request import Request, urlopen

REMOTE_SOURCE_URL = (
    "https://raw.githubusercontent.com/PokeMMOZone/PokeMMO-Data/"
    "main/data/pokemon-data.json"
)
POKEAPI_MOVE_LIST_URL = "https://pokeapi.co/api/v2/move?limit=2000"
POKEAPI_MOVE_URL = "https://pokeapi.co/api/v2/move/{move_id}"
DEFAULT_CLIENT_DUMP_ZIP = (
    Path.home()
    / "Library"
    / "Application Support"
    / "com.pokeemu.macos"
    / "pokemmo-client-live"
    / "dump"
    / "resources"
    / "dump.zip"
)
TIMEOUT_SECONDS = 60
USER_AGENT = "surskit-pokemmo-learnset-sync/1.0"

MOVE_NAME_ALIASES = {
    "ancientpower": "ancient-power",
    "bubblebeam": "bubble-beam",
    "dragonbreath": "dragon-breath",
    "dynamicpunch": "dynamic-punch",
    "extremespeed": "extreme-speed",
    "featherdance": "feather-dance",
    "grasswhistle": "grass-whistle",
    "poisonpowder": "poison-powder",
    "psychic-move": "psychic",
    "smellingsalt": "smelling-salt",
    "solarbeam": "solar-beam",
    "sonicboom": "sonic-boom",
    "thundershock": "thunder-shock",
    "thunderpunch": "thunder-punch",
    "doubleslap": "double-slap",
    "vicegrip": "vice-grip",
    "self-destruct": "selfdestruct",
    "smokescreen": "smoke-screen",
    "high-jump-kick": "hi-jump-kick",
    "hail": "snowscape",
    "feint-attack": "faint-attack",
    "smelling-salts": "smelling-salt",
}

SOURCE_METHOD_MAP = {
    "level": "level-up",
    "tm??": "tm",
    "mt??": "tm",
    "tutor": "tutor",
    "egg": "egg",
    "uovo": "egg",
    "prevo": "prevo",
    "pre-evo": "prevo",
    "evolve": "on-evolution",
    "special": "special",
    "speciale": "special",
    "egg & item": "special-egg",
    "uovo & oggetto": "special-egg",
}

METHOD_ORDER = {
    "level-up": 0,
    "tm": 1,
    "tutor": 2,
    "egg": 3,
    "prevo": 4,
    "on-evolution": 5,
    "special-egg": 6,
    "special": 7,
}

TYPE_MAP = {
    "BUG": "bug",
    "DARK": "dark",
    "DRAGON": "dragon",
    "ELECTRIC": "electric",
    "FIGHTING": "fighting",
    "FIRE": "fire",
    "FLYING": "flying",
    "GHOST": "ghost",
    "GRASS": "grass",
    "GROUND": "ground",
    "ICE": "ice",
    "NORMAL": "normal",
    "POISON": "poison",
    "PSYCHIC": "psychic",
    "ROCK": "rock",
    "STEEL": "steel",
    "WATER": "water",
}

DAMAGE_CLASS_MAP = {
    "PHYSICAL": "physical",
    "SPECIAL": "special",
    "STATUS": "status",
    "Fisico": "physical",
    "Speciale": "special",
    "Stato": "status",
}

STAT_MAP = {
    "hp": "hp",
    "attack": "attack",
    "defense": "defense",
    "sp_attack": "special-attack",
    "sp_defense": "special-defense",
    "speed": "speed",
}

EV_YIELD_MAP = {
    "ev_hp": "hp",
    "ev_attack": "attack",
    "ev_defense": "defense",
    "ev_sp_attack": "special-attack",
    "ev_sp_defense": "special-defense",
    "ev_speed": "speed",
}


def fetch_json_url(url: str) -> dict | list:
    request = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=TIMEOUT_SECONDS) as response:
        return json.load(response)


def fetch_remote_source_data(url: str) -> dict[int, dict]:
    payload = fetch_json_url(url)
    if not isinstance(payload, dict):
        raise ValueError(f"Expected object payload from {url}")

    source_by_id: dict[int, dict] = {}
    for row in payload.values():
        if not isinstance(row, dict):
            continue
        pokemon_id = row.get("id")
        if isinstance(pokemon_id, int):
            source_by_id[pokemon_id] = row
    return source_by_id


def load_client_dump_source_data(dump_zip_path: Path) -> dict[int, dict]:
    if not dump_zip_path.exists():
        raise FileNotFoundError(f"Missing PokeMMO client dump: {dump_zip_path}")

    with zipfile.ZipFile(dump_zip_path) as dump_zip:
        with dump_zip.open("info/monsters.json") as monsters_file:
            payload = json.load(monsters_file)

    if not isinstance(payload, list):
        raise ValueError(f"Expected list in {dump_zip_path}:info/monsters.json")

    source_by_id: dict[int, dict] = {}
    for row in payload:
        if not isinstance(row, dict):
            continue
        pokemon_id = row.get("id")
        if isinstance(pokemon_id, int):
            source_by_id[pokemon_id] = row
    return source_by_id


def load_client_dump_skills(dump_zip_path: Path) -> dict[int, dict]:
    if not dump_zip_path.exists():
        return {}

    with zipfile.ZipFile(dump_zip_path) as dump_zip:
        with dump_zip.open("info/skills.json") as skills_file:
            payload = json.load(skills_file)

    if not isinstance(payload, list):
        raise ValueError(f"Expected list in {dump_zip_path}:info/skills.json")

    skills_by_id: dict[int, dict] = {}
    for row in payload:
        if not isinstance(row, dict):
            continue
        skill_id = row.get("id")
        if isinstance(skill_id, int):
            skills_by_id[skill_id] = row
    return skills_by_id


def load_source_data(
    source: str,
    dump_zip_path: Path,
    remote_url: str,
) -> tuple[dict[int, dict], str]:
    if source == "auto":
        source = "client-dump" if dump_zip_path.exists() else "remote-json"

    if source == "client-dump":
        return load_client_dump_source_data(dump_zip_path), str(dump_zip_path)
    if source == "remote-json":
        return fetch_remote_source_data(remote_url), remote_url
    raise ValueError(f"Unsupported source: {source}")


def read_json(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError(f"Expected list in {path}")
    return data


def read_json_object(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Expected object in {path}")
    return data


def write_json(path: Path, rows: list[dict]) -> None:
    path.write_text(
        json.dumps(rows, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def write_json_object(path: Path, data: dict) -> None:
    path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def slugify_move_name(move_name: str) -> str:
    normalized = (
        move_name.strip()
        .lower()
        .replace("é", "e")
        .replace("'", "")
        .replace(".", "")
    )
    normalized = re.sub(r"[^a-z0-9]+", "-", normalized).strip("-")
    return MOVE_NAME_ALIASES.get(normalized, normalized)


def fetch_move_id_map(move_rows: list[dict]) -> tuple[dict[int, str], dict[str, int]]:
    move_catalog = {str(move.get("name")).lower() for move in move_rows}
    payload = fetch_json_url(POKEAPI_MOVE_LIST_URL)
    if not isinstance(payload, dict) or not isinstance(payload.get("results"), list):
        raise ValueError(f"Expected move list payload from {POKEAPI_MOVE_LIST_URL}")

    move_slug_by_id: dict[int, str] = {}
    move_id_by_slug: dict[str, int] = {}
    for row in payload["results"]:
        if not isinstance(row, dict):
            continue
        name = str(row.get("name") or "").strip().lower()
        url = str(row.get("url") or "")
        if not name or not url:
            continue
        move_id = int(url.rstrip("/").split("/")[-1])
        local_slug = MOVE_NAME_ALIASES.get(name, name)
        move_slug_by_id[move_id] = local_slug
        move_id_by_slug[local_slug] = move_id

        # Keep the raw PokeAPI slug too when the local catalog still uses it.
        if name in move_catalog:
            move_id_by_slug[name] = move_id

    return move_slug_by_id, move_id_by_slug


def normalize_description(value: str | None) -> str:
    if not value:
        return "No description available."
    return (
        str(value)
        .replace("\n", " ")
        .replace("\r", " ")
        .replace("  ", " ")
        .strip()
    )


def extract_move_description(move_payload: dict) -> str:
    for effect_entry in move_payload.get("effect_entries", []):
        if effect_entry.get("language", {}).get("name") != "en":
            continue
        description = effect_entry.get("short_effect") or effect_entry.get("effect")
        if description:
            effect_chance = move_payload.get("effect_chance")
            if effect_chance is not None:
                description = str(description).replace(
                    "$effect_chance",
                    str(effect_chance),
                )
            return normalize_description(description)

    for flavor_entry in move_payload.get("flavor_text_entries", []):
        if flavor_entry.get("language", {}).get("name") == "en":
            return normalize_description(flavor_entry.get("flavor_text"))
    return "No description available."


def fetch_ability_id_map() -> dict[int, str]:
    payload = fetch_json_url("https://pokeapi.co/api/v2/ability?limit=1000")
    if not isinstance(payload, dict) or not isinstance(payload.get("results"), list):
        raise ValueError("Expected ability list payload from PokeAPI")

    ability_slug_by_id: dict[int, str] = {}
    for row in payload["results"]:
        if not isinstance(row, dict):
            continue
        name = str(row.get("name") or "").strip().lower()
        url = str(row.get("url") or "")
        if not name or not url:
            continue
        ability_id = int(url.rstrip("/").split("/")[-1])
        ability_slug_by_id[ability_id] = name
    return ability_slug_by_id


def fetch_ability_description(ability_slug: str) -> str:
    payload = fetch_json_url(f"https://pokeapi.co/api/v2/ability/{ability_slug}")
    if not isinstance(payload, dict):
        return "No description available."

    for effect_entry in payload.get("effect_entries", []):
        if effect_entry.get("language", {}).get("name") == "en":
            return normalize_description(
                effect_entry.get("short_effect") or effect_entry.get("effect")
            )
    return "No description available."


def build_ability_descriptions(
    pokemon_rows: list[dict],
    ability_slugs: set[str],
) -> dict[str, str]:
    descriptions: dict[str, str] = {}
    for pokemon in pokemon_rows:
        for ability in pokemon.get("abilities", []):
            if not isinstance(ability, dict):
                continue
            name = str(ability.get("name") or "").strip().lower()
            description = str(ability.get("description") or "").strip()
            if name and description:
                descriptions[name] = description

    for ability_slug in sorted(ability_slugs - set(descriptions)):
        descriptions[ability_slug] = fetch_ability_description(ability_slug)
    return descriptions


def fetch_missing_move_catalog_rows(
    missing_move_slugs: set[str],
    move_id_by_slug: dict[str, int],
) -> tuple[list[dict], dict[str, str]]:
    rows: list[dict] = []
    descriptions: dict[str, str] = {}

    for move_slug in sorted(missing_move_slugs):
        move_id = move_id_by_slug.get(move_slug)
        if move_id is None:
            raise ValueError(f"Missing PokeAPI move id for {move_slug}")

        payload = fetch_json_url(POKEAPI_MOVE_URL.format(move_id=move_id))
        if not isinstance(payload, dict):
            raise ValueError(f"Expected move payload for {move_slug}")

        rows.append(
            {
                "name": move_slug,
                "type": payload.get("type", {}).get("name"),
                "power": payload.get("power"),
                "pp": payload.get("pp"),
                "accuracy": payload.get("accuracy"),
                "category": payload.get("damage_class", {}).get("name"),
                "priority": payload.get("priority"),
                "target_type": None,
                "true_damage": None,
            }
        )
        descriptions[move_slug] = extract_move_description(payload)

    return rows, descriptions


def move_catalog_row_from_skill(move_slug: str, skill: dict) -> dict:
    base_power = int(skill.get("base_power") or 0)
    base_accuracy = int(skill.get("base_accuracy") or 0)
    return {
        "name": move_slug,
        "type": TYPE_MAP.get(str(skill.get("type") or "").upper()),
        "power": None if base_power == 0 else base_power,
        "pp": skill.get("base_pp"),
        "accuracy": None if base_accuracy in (0, 101) else base_accuracy,
        "category": DAMAGE_CLASS_MAP.get(str(skill.get("skill_damage_type") or "")),
        "priority": skill.get("priority"),
        "target_type": skill.get("target_type"),
        "true_damage": skill.get("true_damage"),
    }


def build_skill_move_catalog_rows(
    skill_rows_by_id: dict[int, dict],
    move_slug_by_id: dict[int, str],
) -> dict[str, dict]:
    rows: dict[str, dict] = {}
    for skill_id, skill in skill_rows_by_id.items():
        move_slug = move_slug_by_id.get(skill_id)
        if not move_slug:
            continue
        rows[move_slug] = move_catalog_row_from_skill(move_slug, skill)
    return rows


def sync_it_localization_from_client_dump(
    localization: dict,
    source_data: dict[int, dict],
    skill_rows_by_id: dict[int, dict],
    move_slug_by_id: dict[int, str],
    ability_slug_by_id: dict[int, str],
) -> dict[str, int]:
    moves = localization.setdefault("moves", {})
    abilities = localization.setdefault("abilities", {})
    changes = {"moves": 0, "abilities": 0}

    for skill_id, skill in skill_rows_by_id.items():
        move_slug = move_slug_by_id.get(skill_id)
        display_name = str(skill.get("name") or "").strip()
        if not move_slug or not display_name:
            continue
        row = moves.setdefault(move_slug, {})
        if row.get("display_name") != display_name:
            row["display_name"] = display_name
            changes["moves"] += 1
        row.setdefault("description", "")

    for source_row in source_data.values():
        for ability in source_row.get("abilities", []):
            if not isinstance(ability, dict):
                continue
            ability_id = ability.get("id")
            ability_slug = (
                ability_slug_by_id.get(ability_id)
                if isinstance(ability_id, int)
                else None
            )
            display_name = str(ability.get("name") or "").strip()
            if not ability_slug or not display_name or display_name == "-":
                continue
            row = abilities.setdefault(ability_slug, {})
            if row.get("display_name") != display_name:
                row["display_name"] = display_name
                changes["abilities"] += 1
            row.setdefault("description", "")

    return changes


def source_method_to_learn_method(source_method: str) -> str:
    normalized = source_method.strip().lower()
    method = SOURCE_METHOD_MAP.get(normalized)
    if not method:
        raise ValueError(f"Unsupported learn method: {source_method}")
    return method


def sort_methods(methods: list[dict]) -> list[dict]:
    return sorted(
        methods,
        key=lambda method: (
            METHOD_ORDER.get(str(method.get("method")), 99),
            method.get("level") is None,
            method.get("level") or 0,
        ),
    )


def build_learnsets(
    pokemon_rows: list[dict],
    source_data: dict[int, dict],
    move_slug_by_id: dict[int, str],
) -> tuple[dict[int, list[str]], dict[str, dict[int, list[dict]]]]:
    pokemon_moves: dict[int, set[str]] = {}
    move_learners: dict[str, dict[int, list[dict]]] = {}

    for pokemon in pokemon_rows:
        pokemon_id = int(pokemon["id"])
        pokemon_name = str(pokemon["name"])
        source_row = source_data.get(pokemon_id)
        if not isinstance(source_row, dict):
            raise KeyError(f"Missing source learnset for {pokemon_name} ({pokemon_id})")

        move_methods: dict[str, set[tuple[str, int | None]]] = {}
        for move in source_row.get("moves", []):
            if not isinstance(move, dict):
                continue

            move_id = move.get("id")
            if isinstance(move_id, int) and move_id in move_slug_by_id:
                move_slug = move_slug_by_id[move_id]
            else:
                move_name = str(move.get("name") or "").strip()
                if not move_name:
                    continue
                move_slug = slugify_move_name(move_name)

            if not move_slug:
                continue
            method = source_method_to_learn_method(str(move.get("type") or ""))

            level: int | None = None
            if method == "level-up":
                raw_level = move.get("level")
                if raw_level is None:
                    raw_level = move.get("learn_level")
                if raw_level not in (None, ""):
                    level = int(raw_level)

            move_methods.setdefault(move_slug, set()).add((method, level))

        pokemon_moves[pokemon_id] = set(move_methods)
        for move_slug, method_keys in move_methods.items():
            methods = [
                {"method": method, "level": level}
                for method, level in sorted(
                    method_keys,
                    key=lambda item: (
                        METHOD_ORDER.get(item[0], 99),
                        item[1] is None,
                        item[1] or 0,
                    ),
                )
            ]
            move_learners.setdefault(move_slug, {})[pokemon_id] = sort_methods(methods)

    return (
        {pokemon_id: sorted(moves) for pokemon_id, moves in pokemon_moves.items()},
        move_learners,
    )


def pokemon_sprite(pokemon: dict) -> str | None:
    sprites = pokemon.get("sprites")
    if not isinstance(sprites, dict):
        return None
    return sprites.get("official_artwork") or sprites.get("front_default")


def sync_pokemon_moves(
    pokemon_rows: list[dict],
    source_moves_by_pokemon: dict[int, list[str]],
) -> tuple[int, int]:
    additions = 0
    removals = 0
    for pokemon in pokemon_rows:
        pokemon_id = int(pokemon["id"])
        current_moves = set(str(move) for move in pokemon.get("moves", []))
        source_moves = set(source_moves_by_pokemon[pokemon_id])
        additions += len(source_moves - current_moves)
        removals += len(current_moves - source_moves)
        pokemon["moves"] = sorted(source_moves)
    return additions, removals


def source_types(source_row: dict) -> list[str]:
    types: list[str] = []
    for raw_type in source_row.get("types", []):
        pokemon_type = TYPE_MAP.get(str(raw_type).upper())
        if pokemon_type and pokemon_type not in types:
            types.append(pokemon_type)
    return types


def source_stats(source_row: dict) -> dict[str, int]:
    stats = source_row.get("stats")
    if not isinstance(stats, dict):
        return {}
    return {
        target_name: int(stats[source_name])
        for source_name, target_name in STAT_MAP.items()
        if source_name in stats
    }


def source_ev_yield(source_row: dict) -> dict[str, int]:
    yields = source_row.get("yields")
    if not isinstance(yields, dict):
        return {}
    return {
        target_name: int(yields[source_name])
        for source_name, target_name in EV_YIELD_MAP.items()
        if int(yields.get(source_name) or 0) > 0
    }


def source_abilities(
    source_row: dict,
    ability_slug_by_id: dict[int, str],
    ability_descriptions: dict[str, str],
) -> list[dict]:
    ability_ids: list[int] = []
    for ability in source_row.get("abilities", []):
        if not isinstance(ability, dict):
            continue
        ability_id = ability.get("id")
        if not isinstance(ability_id, int) or ability_id == 0:
            continue
        if ability_id not in ability_ids:
            ability_ids.append(ability_id)

    rows: list[dict] = []
    for ability_id in ability_ids:
        ability_slug = ability_slug_by_id.get(ability_id)
        if not ability_slug:
            continue
        rows.append(
            {
                "name": ability_slug,
                "description": ability_descriptions.get(
                    ability_slug,
                    "No description available.",
                ),
            }
        )
    return rows


def sync_pokemon_core_data(
    pokemon_rows: list[dict],
    source_data: dict[int, dict],
    ability_slug_by_id: dict[int, str],
    ability_descriptions: dict[str, str],
) -> dict[str, int]:
    changed = {"types": 0, "stats": 0, "ev_yield": 0, "abilities": 0}
    for pokemon in pokemon_rows:
        pokemon_id = int(pokemon["id"])
        source_row = source_data.get(pokemon_id)
        if not source_row:
            continue

        updates = {
            "types": source_types(source_row),
            "stats": source_stats(source_row),
            "ev_yield": source_ev_yield(source_row),
            "abilities": source_abilities(
                source_row,
                ability_slug_by_id,
                ability_descriptions,
            ),
        }
        for key, value in updates.items():
            if value and pokemon.get(key) != value:
                pokemon[key] = value
                changed[key] += 1
    return changed


def build_move_detail_rows(
    pokemon_rows: list[dict],
    move_detail_rows: list[dict],
    move_learners: dict[str, dict[int, list[dict]]],
    new_move_descriptions: dict[str, str],
) -> list[dict]:
    pokemon_by_id = {int(pokemon["id"]): pokemon for pokemon in pokemon_rows}
    local_pokemon_ids = set(pokemon_by_id)
    source_move_names = set(move_learners)
    existing_by_name = {
        str(detail.get("name")).lower(): detail for detail in move_detail_rows
    }
    all_move_names = sorted(set(existing_by_name) | source_move_names)
    refreshed_rows: list[dict] = []

    for move_name in all_move_names:
        existing = existing_by_name.get(move_name, {})
        learners: list[dict] = []

        if move_name in source_move_names:
            for pokemon_id in sorted(move_learners[move_name]):
                pokemon = pokemon_by_id[pokemon_id]
                learners.append(
                    {
                        "pokemon_id": pokemon_id,
                        "pokemon_name": pokemon["name"],
                        "methods": move_learners[move_name][pokemon_id],
                        "pokemon_sprite": pokemon_sprite(pokemon),
                    }
                )
        else:
            for learner in existing.get("learners", []):
                if int(learner.get("pokemon_id", 0)) in local_pokemon_ids:
                    continue
                learners.append(learner)

        refreshed_rows.append(
            {
                "name": move_name,
                "description": existing.get(
                    "description",
                    new_move_descriptions.get(move_name, "No description available."),
                ),
                "learners": learners,
            }
        )

    return refreshed_rows


def sync_move_catalog(
    move_rows: list[dict],
    move_learners: dict[str, dict[int, list[dict]]],
    move_id_by_slug: dict[str, int],
    skill_move_rows: dict[str, dict],
) -> tuple[list[dict], dict[str, str], list[str], int]:
    catalog_names = {str(move.get("name")).lower() for move in move_rows}
    missing = set(move_learners) - catalog_names
    descriptions: dict[str, str] = {}
    added_rows: list[dict] = []
    missing_without_skill = {move for move in missing if move not in skill_move_rows}

    if missing_without_skill:
        fetched_rows, descriptions = fetch_missing_move_catalog_rows(
            missing_without_skill,
            move_id_by_slug,
        )
        added_rows.extend(fetched_rows)

    for move_slug in sorted(missing & set(skill_move_rows)):
        added_rows.append(skill_move_rows[move_slug])

    rows_by_name = {str(move.get("name")).lower(): dict(move) for move in move_rows}
    updated_count = 0
    for move_slug, skill_row in skill_move_rows.items():
        existing = rows_by_name.get(move_slug)
        if existing is None:
            continue
        if existing != skill_row:
            rows_by_name[move_slug] = skill_row
            updated_count += 1

    for row in added_rows:
        rows_by_name[str(row.get("name")).lower()] = row

    return (
        [rows_by_name[name] for name in sorted(rows_by_name)],
        descriptions,
        sorted(missing),
        updated_count,
    )


def parse_args() -> object:
    parser = ArgumentParser(
        description="Sync Pokemon learnsets from PokeMMO client monsters.json.",
    )
    parser.add_argument(
        "--source",
        choices=("auto", "client-dump", "remote-json"),
        default="auto",
        help="Use local client dump when available, otherwise remote JSON.",
    )
    parser.add_argument(
        "--dump-zip",
        type=Path,
        default=DEFAULT_CLIENT_DUMP_ZIP,
        help="Path to PokeMMO dump/resources/dump.zip.",
    )
    parser.add_argument(
        "--remote-json-url",
        default=REMOTE_SOURCE_URL,
        help="Fallback remote JSON source.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    project_root = Path(__file__).resolve().parents[1]
    data_dir = project_root / "backend" / "app" / "data"
    pokemon_path = data_dir / "pokemon.json"
    moves_path = data_dir / "moves.json"
    move_details_path = data_dir / "move_details.json"
    localization_it_path = data_dir / "localization_it.json"

    pokemon_rows = read_json(pokemon_path)
    move_rows = read_json(moves_path)
    move_detail_rows = read_json(move_details_path)
    localization_it = read_json_object(localization_it_path)
    source_data, source_label = load_source_data(
        source=args.source,
        dump_zip_path=args.dump_zip,
        remote_url=args.remote_json_url,
    )
    using_client_dump = source_label == str(args.dump_zip)
    move_slug_by_id, move_id_by_slug = fetch_move_id_map(move_rows)
    skill_rows_by_id = (
        load_client_dump_skills(args.dump_zip) if using_client_dump else {}
    )
    skill_move_rows = build_skill_move_catalog_rows(
        skill_rows_by_id,
        move_slug_by_id,
    )

    ability_slug_by_id = fetch_ability_id_map()
    current_pokemon_ids = {int(pokemon["id"]) for pokemon in pokemon_rows}
    source_ability_slugs = {
        ability_slug_by_id[ability["id"]]
        for pokemon_id, source_row in source_data.items()
        if pokemon_id in current_pokemon_ids
        for ability in source_row.get("abilities", [])
        if isinstance(ability, dict)
        and isinstance(ability.get("id"), int)
        and ability["id"] in ability_slug_by_id
        and ability["id"] != 0
    }
    ability_descriptions = build_ability_descriptions(
        pokemon_rows,
        source_ability_slugs,
    )
    localization_changes = (
        sync_it_localization_from_client_dump(
            localization_it,
            source_data,
            skill_rows_by_id,
            move_slug_by_id,
            ability_slug_by_id,
        )
        if using_client_dump
        else {"moves": 0, "abilities": 0}
    )

    source_moves_by_pokemon, move_learners = build_learnsets(
        pokemon_rows,
        source_data,
        move_slug_by_id,
    )
    move_rows, new_move_descriptions, added_move_slugs, updated_move_count = sync_move_catalog(
        move_rows,
        move_learners,
        move_id_by_slug,
        skill_move_rows,
    )

    core_changes = sync_pokemon_core_data(
        pokemon_rows,
        source_data,
        ability_slug_by_id,
        ability_descriptions,
    )
    additions, removals = sync_pokemon_moves(pokemon_rows, source_moves_by_pokemon)
    refreshed_move_detail_rows = build_move_detail_rows(
        pokemon_rows,
        move_detail_rows,
        move_learners,
        new_move_descriptions,
    )

    pokemon_rows.sort(key=lambda pokemon: int(pokemon["id"]))
    write_json(pokemon_path, pokemon_rows)
    write_json(moves_path, move_rows)
    write_json(move_details_path, refreshed_move_detail_rows)
    write_json_object(localization_it_path, localization_it)

    print(f"Synced learnsets for {len(pokemon_rows)} Pokemon from {source_label}")
    print(f"Pokemon move additions: {additions}")
    print(f"Pokemon move removals: {removals}")
    print(f"Move catalog additions: {', '.join(added_move_slugs) if added_move_slugs else 0}")
    print(f"Move catalog updates from skills.json: {updated_move_count}")
    print(
        "Pokemon core updates: "
        + ", ".join(f"{key}={value}" for key, value in core_changes.items())
    )
    print(
        "Italian localization updates from client dump: "
        + ", ".join(f"{key}={value}" for key, value in localization_changes.items())
    )
    print(f"Wrote {pokemon_path}")
    print(f"Wrote {moves_path}")
    print(f"Wrote {move_details_path}")
    print(f"Wrote {localization_it_path}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise
