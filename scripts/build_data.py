#!/usr/bin/env python3
from __future__ import annotations

import json
import time
from pathlib import Path

import requests

BASE_URL = "https://pokeapi.co/api/v2"
GEN3_START = 252
GEN3_END = 386
TIMEOUT = 20
LEVEL_UP_VERSION_GROUP = "black-white"
TM_VERSION_GROUP = "scarlet-violet"
LEARN_METHOD_ORDER = {"level-up": 0, "tm": 1, "tutor": 2, "egg": 3}


def fetch_json(url: str) -> dict | list:
    response = requests.get(url, timeout=TIMEOUT)
    response.raise_for_status()
    return response.json()


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
    description = None
    effect_entries = move_payload.get("effect_entries", [])
    for effect_entry in effect_entries:
        if effect_entry.get("language", {}).get("name") != "en":
            continue
        description = effect_entry.get("short_effect") or effect_entry.get("effect")
        if description:
            break

    if description is None:
        flavor_entries = move_payload.get("flavor_text_entries", [])
        for flavor_entry in flavor_entries:
            if flavor_entry.get("language", {}).get("name") != "en":
                continue
            description = flavor_entry.get("flavor_text")
            if description:
                break

    if description:
        effect_chance = move_payload.get("effect_chance")
        if effect_chance is not None:
            description = str(description).replace("$effect_chance", str(effect_chance))
    return normalize_description(description)


def extract_learn_methods(version_group_details: list[dict]) -> list[dict]:
    level_values = sorted(
        {
            int(detail.get("level_learned_at", 0))
            for detail in version_group_details
            if detail.get("version_group", {}).get("name") == LEVEL_UP_VERSION_GROUP
            and detail.get("move_learn_method", {}).get("name") == "level-up"
            and int(detail.get("level_learned_at", 0)) > 0
        }
    )
    has_tm = any(
        detail.get("version_group", {}).get("name") == TM_VERSION_GROUP
        and detail.get("move_learn_method", {}).get("name") == "machine"
        for detail in version_group_details
    )
    has_tutor = any(
        detail.get("move_learn_method", {}).get("name") == "tutor"
        for detail in version_group_details
    )
    has_egg = any(
        detail.get("move_learn_method", {}).get("name") == "egg"
        for detail in version_group_details
    )

    methods: list[dict] = []
    if level_values:
        methods.append({"method": "level-up", "level": level_values[0]})
    if has_tm:
        methods.append({"method": "tm", "level": None})
    if has_tutor:
        methods.append({"method": "tutor", "level": None})
    if has_egg:
        methods.append({"method": "egg", "level": None})
    return methods


def sort_learner_methods(methods: list[dict]) -> list[dict]:
    return sorted(
        methods,
        key=lambda method: (
            LEARN_METHOD_ORDER.get(str(method.get("method")), 99),
            method.get("level") is None,
            method.get("level") or 0,
        ),
    )


def build_data() -> tuple[list[dict], list[dict], list[dict], list[dict]]:
    pokemon_rows: list[dict] = []
    locations_map: dict[str, set[int]] = {}
    move_names: set[str] = set()
    ability_names: set[str] = set()
    move_learners_map: dict[str, dict[int, dict]] = {}

    for pokemon_id in range(GEN3_START, GEN3_END + 1):
        print(f"Fetching pokemon {pokemon_id}...")
        detail = fetch_json(f"{BASE_URL}/pokemon/{pokemon_id}")

        types = [
            item["type"]["name"]
            for item in sorted(detail["types"], key=lambda value: value["slot"])
        ]
        abilities = [
            item["ability"]["name"]
            for item in sorted(detail["abilities"], key=lambda value: value["slot"])
            if not item.get("is_hidden", False)
        ]
        ability_names.update(abilities)
        stats = {item["stat"]["name"]: item["base_stat"] for item in detail["stats"]}
        ev_yield = {
            item["stat"]["name"]: item["effort"]
            for item in detail["stats"]
            if int(item.get("effort", 0)) > 0
        }
        learner_sprite = (
            detail["sprites"].get("other", {})
            .get("official-artwork", {})
            .get("front_default")
            or detail["sprites"].get("front_default")
        )
        pokemon_move_names: set[str] = set()
        for move_entry in detail["moves"]:
            move_name = move_entry["move"]["name"]
            pokemon_move_names.add(move_name)

            methods = extract_learn_methods(
                move_entry.get("version_group_details", [])
            )
            if not methods:
                continue

            move_learner_index = move_learners_map.setdefault(move_name, {})
            learner = move_learner_index.setdefault(
                pokemon_id,
                {
                    "pokemon_id": pokemon_id,
                    "pokemon_name": detail["name"],
                    "pokemon_sprite": learner_sprite,
                    "methods": [],
                },
            )
            for method in methods:
                if method not in learner["methods"]:
                    learner["methods"].append(method)

        moves = sorted(pokemon_move_names)
        move_names.update(moves)

        sprites = {
            "front_default": detail["sprites"].get("front_default"),
            "official_artwork": detail["sprites"].get("other", {})
            .get("official-artwork", {})
            .get("front_default"),
        }

        encounter_names: list[str] = []
        encounters_url = detail.get("location_area_encounters")
        if encounters_url:
            encounter_data = fetch_json(encounters_url)
            encounter_names = sorted(
                {
                    encounter["location_area"]["name"]
                    for encounter in encounter_data
                    if "location_area" in encounter
                }
            )
            for encounter_name in encounter_names:
                locations_map.setdefault(encounter_name, set()).add(pokemon_id)

        pokemon_rows.append(
            {
                "id": pokemon_id,
                "name": detail["name"],
                "types": types,
                "ability_names": abilities,
                "ev_yield": ev_yield,
                "stats": stats,
                "moves": moves,
                "sprites": sprites,
                "locations": encounter_names,
            }
        )

        # Keep requests respectful.
        time.sleep(0.05)

    move_rows: list[dict] = []
    move_descriptions: dict[str, str] = {}
    for move_name in sorted(move_names):
        print(f"Fetching move {move_name}...")
        move = fetch_json(f"{BASE_URL}/move/{move_name}")
        move_descriptions[move_name] = extract_move_description(move)
        move_rows.append(
            {
                "name": move_name,
                "type": move.get("type", {}).get("name"),
                "category": move.get("damage_class", {}).get("name"),
                "power": move.get("power"),
                "pp": move.get("pp"),
                "accuracy": move.get("accuracy"),
            }
        )
        time.sleep(0.03)

    ability_descriptions: dict[str, str] = {}
    for ability_name in sorted(ability_names):
        print(f"Fetching ability {ability_name}...")
        ability = fetch_json(f"{BASE_URL}/ability/{ability_name}")
        description = "No description available."
        for effect_entry in ability.get("effect_entries", []):
            language = effect_entry.get("language", {}).get("name")
            if language == "en":
                description = (
                    effect_entry.get("short_effect")
                    or effect_entry.get("effect")
                    or description
                )
                break

        ability_descriptions[ability_name] = (
            str(description)
            .replace("\n", " ")
            .replace("\r", " ")
            .replace("  ", " ")
            .strip()
        )
        time.sleep(0.03)

    for pokemon in pokemon_rows:
        pokemon["abilities"] = [
            {
                "name": ability_name,
                "description": ability_descriptions.get(
                    ability_name, "No description available."
                ),
            }
            for ability_name in pokemon.pop("ability_names", [])
        ]

    location_rows = [
        {"name": name, "pokemon_ids": sorted(ids)}
        for name, ids in sorted(locations_map.items(), key=lambda item: item[0])
    ]

    move_detail_rows: list[dict] = []
    for move_name in sorted(move_names):
        learners = list(move_learners_map.get(move_name, {}).values())
        learners.sort(key=lambda learner: learner["pokemon_id"])
        for learner in learners:
            learner["methods"] = sort_learner_methods(learner["methods"])

        move_detail_rows.append(
            {
                "name": move_name,
                "description": move_descriptions.get(
                    move_name, "No description available."
                ),
                "learners": learners,
            }
        )

    return pokemon_rows, move_rows, location_rows, move_detail_rows


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    out_dir = project_root / "backend" / "app" / "data"
    out_dir.mkdir(parents=True, exist_ok=True)

    pokemon_rows, move_rows, location_rows, move_detail_rows = build_data()

    (out_dir / "pokemon.json").write_text(
        json.dumps(pokemon_rows, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (out_dir / "moves.json").write_text(
        json.dumps(move_rows, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (out_dir / "locations.json").write_text(
        json.dumps(location_rows, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (out_dir / "move_details.json").write_text(
        json.dumps(move_detail_rows, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    print(f"Data written to {out_dir}")


if __name__ == "__main__":
    main()
