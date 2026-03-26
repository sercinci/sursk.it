#!/usr/bin/env python3
from __future__ import annotations

import json
import time
from pathlib import Path

import requests

POKEAPI_BASE_URL = "https://pokeapi.co/api/v2"
TIMEOUT_SECONDS = 20
REQUEST_SLEEP_SECONDS = 0.05

# Gen 1/2 legendary + mythical that should not be added.
EXCLUDED_GEN1_GEN2_IDS = {
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
}


def fetch_json(url: str) -> dict | list:
    response = requests.get(url, timeout=TIMEOUT_SECONDS)
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


def fetch_ability_description(ability_name: str) -> str:
    payload = fetch_json(f"{POKEAPI_BASE_URL}/ability/{ability_name}")
    for effect_entry in payload.get("effect_entries", []):
        if effect_entry.get("language", {}).get("name") != "en":
            continue
        return normalize_description(
            effect_entry.get("short_effect") or effect_entry.get("effect")
        )
    return "No description available."


def read_json(path: Path) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    data_dir = project_root / "backend" / "app" / "data"
    pokemon_path = data_dir / "pokemon.json"
    hoenn_locations_path = data_dir / "pokemmo_hoenn_locations.json"

    pokemon_rows = read_json(pokemon_path)
    hoenn_locations = read_json(hoenn_locations_path)

    existing_ids = {int(row["id"]) for row in pokemon_rows}
    hoenn_encounter_ids: set[int] = set()
    for location in hoenn_locations:
        for encounter in location.get("encounters", []):
            pokemon_id = encounter.get("pokemon_id")
            if isinstance(pokemon_id, int):
                hoenn_encounter_ids.add(pokemon_id)

    target_ids = sorted(
        pokemon_id
        for pokemon_id in hoenn_encounter_ids
        if 1 <= pokemon_id <= 251 and pokemon_id not in EXCLUDED_GEN1_GEN2_IDS
    )
    missing_ids = [pokemon_id for pokemon_id in target_ids if pokemon_id not in existing_ids]

    if not missing_ids:
        print("No missing Hoenn-capturable Gen 1/2 Pokemon to add.")
        return

    ability_descriptions: dict[str, str] = {}
    for row in pokemon_rows:
        for ability in row.get("abilities", []):
            name = str(ability.get("name", "")).strip()
            description = str(ability.get("description", "")).strip()
            if name and description:
                ability_descriptions[name] = description

    print(f"Adding {len(missing_ids)} Pokemon IDs: {missing_ids}")
    for pokemon_id in missing_ids:
        print(f"Fetching pokemon {pokemon_id}...")
        detail = fetch_json(f"{POKEAPI_BASE_URL}/pokemon/{pokemon_id}")

        types = [
            item["type"]["name"]
            for item in sorted(detail["types"], key=lambda value: value["slot"])
        ]
        ability_names = [
            item["ability"]["name"]
            for item in sorted(detail["abilities"], key=lambda value: value["slot"])
            if not item.get("is_hidden", False)
        ]
        for ability_name in ability_names:
            if ability_name not in ability_descriptions:
                ability_descriptions[ability_name] = fetch_ability_description(ability_name)
                time.sleep(REQUEST_SLEEP_SECONDS)

        stats = {item["stat"]["name"]: item["base_stat"] for item in detail["stats"]}
        ev_yield = {
            item["stat"]["name"]: item["effort"]
            for item in detail["stats"]
            if int(item.get("effort", 0)) > 0
        }
        moves = sorted({entry["move"]["name"] for entry in detail.get("moves", [])})
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

        pokemon_rows.append(
            {
                "id": pokemon_id,
                "name": detail["name"],
                "types": types,
                "abilities": [
                    {
                        "name": ability_name,
                        "description": ability_descriptions.get(
                            ability_name, "No description available."
                        ),
                    }
                    for ability_name in ability_names
                ],
                "ev_yield": ev_yield,
                "stats": stats,
                "moves": moves,
                "sprites": sprites,
                "locations": encounter_names,
            }
        )
        time.sleep(REQUEST_SLEEP_SECONDS)

    pokemon_rows.sort(key=lambda row: int(row["id"]))
    pokemon_path.write_text(
        json.dumps(pokemon_rows, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {len(pokemon_rows)} pokemon rows to {pokemon_path}")


if __name__ == "__main__":
    main()
