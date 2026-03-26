#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.parse import quote

import cloudscraper

POKEAPI_MOVE_LIST = "https://pokeapi.co/api/v2/move?limit=2000"
POKEAPI_ABILITY_DETAIL = "https://pokeapi.co/api/v2/ability/{slug}"
POKEMONCENTRAL_RAW = "https://wiki.pokemoncentral.it/index.php?title={title}&action=raw"
POKEMONCENTRAL_API = "https://wiki.pokemoncentral.it/api.php"

LOCATION_LABEL_OVERRIDES = {
    "abandoned-ship-area": "Vecchia Nave",
    "altering-cave-area": "Grotta Mutevole",
    "aqua-hideout-area": "Rifugio Idro",
    "cave-of-origin-area": "Grotta dei Tempi",
    "dewford-town-area": "Bluruvia",
    "ever-grande-city-area": "Iridopoli",
    "granite-cave-area": "Grotta Pietrosa",
    "hoenn-victory-road-area": "Via Vittoria",
    "jagged-pass-area": "Passo Selvaggio",
    "lilycove-city-area": "Porto Alghepoli",
    "meteor-falls-area": "Cascate Meteora",
    "mirage-tower-area": "Torre Miraggio",
    "mossdeep-city-area": "Verdeazzupoli",
    "mt-pyre-area": "Monte Pira",
    "new-mauville-area": "Ciclanova",
    "pacifidlog-town-area": "Orocea",
    "petalburg-city-area": "Petalipoli",
    "petalburg-woods-area": "Bosco Petalo",
    "rusturf-tunnel-area": "Tunnel Menferro",
    "safari-zone-area": "Zona Safari",
    "scorched-slab-area": "Grottino Solare",
    "seafloor-cavern-area": "Antro Abissale",
    "sealed-chamber-area": "Sala Incisa",
    "shoal-cave-area": "Grotta Ondosa",
    "slateport-city-area": "Porto Selcepoli",
    "sootopolis-city-area": "Ceneride",
    "underwater-area": "Sott'acqua",
}


def build_scraper():
    return cloudscraper.create_scraper(
        browser={"browser": "chrome", "platform": "darwin", "mobile": False}
    )


def split_template_args(text: str) -> list[str]:
    args: list[str] = []
    buffer: list[str] = []
    curly_depth = 0
    square_depth = 0
    index = 0
    while index < len(text):
        char = text[index]
        nxt = text[index + 1] if index + 1 < len(text) else ""
        if char == "{" and nxt == "{":
            curly_depth += 1
            buffer.append(char)
            index += 1
            buffer.append(nxt)
        elif char == "}" and nxt == "}":
            curly_depth = max(0, curly_depth - 1)
            buffer.append(char)
            index += 1
            buffer.append(nxt)
        elif char == "[" and nxt == "[":
            square_depth += 1
            buffer.append(char)
            index += 1
            buffer.append(nxt)
        elif char == "]" and nxt == "]":
            square_depth = max(0, square_depth - 1)
            buffer.append(char)
            index += 1
            buffer.append(nxt)
        elif char == "|" and curly_depth == 0 and square_depth == 0:
            args.append("".join(buffer).strip())
            buffer = []
        else:
            buffer.append(char)
        index += 1
    if buffer:
        args.append("".join(buffer).strip())
    return args


def clean_wikitext(text: str) -> str:
    cleaned = text
    cleaned = re.sub(r"<!--.*?-->", " ", cleaned, flags=re.S)
    cleaned = cleaned.replace("&nbsp;", " ")
    cleaned = re.sub(r"\{\{tt\|([^|{}]+)\|[^{}]*\}\}", r"\1", cleaned)

    previous = None
    while previous != cleaned:
        previous = cleaned
        cleaned = re.sub(r"\{\{[^{}]*\}\}", " ", cleaned)

    cleaned = re.sub(r"\[\[([^\]|]+)\|([^\]]+)\]\]", r"\2", cleaned)
    cleaned = re.sub(r"\[\[([^\]]+)\]\]", r"\1", cleaned)
    cleaned = cleaned.replace("''", "")
    cleaned = re.sub(r"<[^>]+>", " ", cleaned)
    cleaned = html.unescape(cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def extract_move_description(raw_page: str) -> str:
    description_candidates: list[str] = []
    for line in raw_page.splitlines():
        stripped = line.strip()
        if not (stripped.startswith("{{movedesc/row|") and stripped.endswith("}}")):
            continue
        inner = stripped[len("{{movedesc/row|") : -2]
        args = split_template_args(inner)
        if args:
            description_candidates.append(args[-1])

    if description_candidates:
        final = clean_wikitext(description_candidates[-1])
        if final:
            return final

    for key in ("cdesc", "desc", "mdesc"):
        match = re.search(rf"\|{key}\s*=\s*([^\n]+)", raw_page)
        if not match:
            continue
        candidate = clean_wikitext(match.group(1))
        if candidate:
            return candidate

    return "Nessuna descrizione disponibile."


def load_move_slug_set(project_root: Path) -> set[str]:
    move_rows = json.loads((project_root / "backend" / "app" / "data" / "moves.json").read_text(encoding="utf-8"))
    return {str(row.get("name", "")).strip().lower() for row in move_rows if row.get("name")}


def load_ability_slug_set(project_root: Path) -> set[str]:
    pokemon_rows = json.loads(
        (project_root / "backend" / "app" / "data" / "pokemon.json").read_text(encoding="utf-8")
    )
    slugs: set[str] = set()
    for row in pokemon_rows:
        for ability in row.get("abilities", []):
            slug = str(ability.get("name", "")).strip().lower()
            if slug:
                slugs.add(slug)
    return slugs


def fetch_move_slug_to_id(scraper, move_slugs: set[str]) -> dict[str, int]:
    response = scraper.get(POKEAPI_MOVE_LIST, timeout=60)
    response.raise_for_status()
    payload = response.json()
    rows = payload.get("results", [])
    mapping: dict[str, int] = {}
    for row in rows:
        if not isinstance(row, dict):
            continue
        slug = str(row.get("name", "")).strip().lower()
        if not slug or slug not in move_slugs:
            continue
        url = str(row.get("url", ""))
        match = re.search(r"/move/(\d+)/?$", url)
        if match:
            mapping[slug] = int(match.group(1))
    return mapping


def fetch_move_index(scraper) -> dict[int, str]:
    response = scraper.get(POKEMONCENTRAL_RAW.format(title="Elenco_mosse"), timeout=60)
    response.raise_for_status()
    wikitext = response.text
    rows = re.findall(r"\{\{listmove\|(\d+)\|([^|}]+)", wikitext)
    return {int(move_id): title.strip() for move_id, title in rows}


def build_move_localizations(scraper, move_slugs: set[str]) -> dict[str, dict[str, str]]:
    slug_to_id = fetch_move_slug_to_id(scraper, move_slugs)
    id_to_title = fetch_move_index(scraper)
    localized: dict[str, dict[str, str]] = {}
    missing: list[str] = []

    for slug in sorted(move_slugs):
        move_id = slug_to_id.get(slug)
        if not move_id:
            missing.append(f"{slug}:missing_pokeapi_id")
            continue
        title = id_to_title.get(move_id)
        if not title:
            missing.append(f"{slug}:missing_pokemoncentral_title")
            continue
        response = scraper.get(
            POKEMONCENTRAL_RAW.format(title=quote(title)),
            timeout=60,
        )
        if response.status_code != 200:
            missing.append(f"{slug}:status_{response.status_code}")
            continue
        description = extract_move_description(response.text)
        localized[slug] = {
            "display_name": title,
            "description": description,
        }

    if missing:
        raise RuntimeError(
            "Missing move localizations:\n" + "\n".join(missing[:20])
        )
    return localized


def fetch_search_titles(scraper, query: str, limit: int = 5) -> list[str]:
    response = scraper.get(
        POKEMONCENTRAL_API,
        params={
            "action": "query",
            "list": "search",
            "srsearch": query,
            "srlimit": limit,
            "format": "json",
        },
        timeout=40,
    )
    response.raise_for_status()
    payload: dict[str, Any] = response.json()
    rows = payload.get("query", {}).get("search", [])
    return [str(row.get("title", "")).strip() for row in rows if row.get("title")]


def to_english_location_query(location_slug: str) -> str:
    base = location_slug.removesuffix("-area")
    if base.startswith("hoenn-route-"):
        route_number = base.split("-")[-1]
        return f"Route {route_number}"
    if base.startswith("hoenn-victory-road"):
        return "Victory Road Hoenn"
    if base.startswith("mt-pyre"):
        return "Mt. Pyre"
    return " ".join(segment.capitalize() for segment in base.split("-"))


def normalize_search_title(title: str) -> str:
    if title.endswith("(Hoenn)"):
        return title[:-7].strip()
    return title


def build_location_localizations(scraper, location_slugs: list[str]) -> dict[str, str]:
    localized: dict[str, str] = {}
    for slug in sorted(location_slugs):
        if slug in LOCATION_LABEL_OVERRIDES:
            localized[slug] = LOCATION_LABEL_OVERRIDES[slug]
            continue

        english_query = to_english_location_query(slug)
        titles = fetch_search_titles(scraper, english_query, limit=8)
        if not titles:
            continue

        picked = titles[0]
        if slug.startswith("hoenn-route-"):
            match = re.search(r"(\d+)", slug)
            if match:
                picked = f"Percorso {match.group(1)}"
        localized[slug] = normalize_search_title(picked)
    return localized


def clean_pokeapi_text(value: str) -> str:
    return re.sub(r"\s+", " ", value.replace("\n", " ").replace("\f", " ")).strip()


def build_ability_localizations(scraper, ability_slugs: set[str]) -> dict[str, dict[str, str]]:
    localized: dict[str, dict[str, str]] = {}
    missing: list[str] = []

    for slug in sorted(ability_slugs):
        response = scraper.get(POKEAPI_ABILITY_DETAIL.format(slug=quote(slug)), timeout=60)
        if response.status_code != 200:
            missing.append(f"{slug}:status_{response.status_code}")
            continue

        payload: dict[str, Any] = response.json()
        names = payload.get("names", [])
        display_name = next(
            (
                str(row.get("name", "")).strip()
                for row in names
                if row.get("language", {}).get("name") == "it" and row.get("name")
            ),
            "",
        )
        if not display_name:
            display_name = slug.replace("-", " ").title()

        flavor_entries = [
            clean_pokeapi_text(str(row.get("flavor_text", "")))
            for row in payload.get("flavor_text_entries", [])
            if row.get("language", {}).get("name") == "it" and row.get("flavor_text")
        ]
        flavor_entries = [entry for entry in flavor_entries if entry]
        description = max(flavor_entries, key=len) if flavor_entries else "Nessuna descrizione disponibile."

        localized[slug] = {
            "display_name": display_name,
            "description": description,
        }

    if missing:
        raise RuntimeError("Missing ability localizations:\n" + "\n".join(missing[:20]))
    return localized


def main() -> None:
    parser = argparse.ArgumentParser(description="Build Italian localization dataset from PokemonCentral.")
    parser.add_argument(
        "--output",
        default="backend/app/data/localization_it.json",
        help="Output JSON path",
    )
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[1]
    output_path = (project_root / args.output).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    location_rows = json.loads(
        (project_root / "backend" / "app" / "data" / "pokemmo_hoenn_locations.json").read_text(
            encoding="utf-8"
        )
    )
    location_slugs = sorted({str(row.get("name", "")).strip() for row in location_rows if row.get("name")})
    move_slugs = load_move_slug_set(project_root)
    ability_slugs = load_ability_slug_set(project_root)

    scraper = build_scraper()
    move_localizations = build_move_localizations(scraper, move_slugs)
    ability_localizations = build_ability_localizations(scraper, ability_slugs)
    location_localizations = build_location_localizations(scraper, location_slugs)

    payload = {
        "meta": {
            "source": "https://wiki.pokemoncentral.it/",
            "generated_at": datetime.now(UTC).isoformat(),
            "moves_total": len(move_localizations),
            "abilities_total": len(ability_localizations),
            "locations_total": len(location_localizations),
        },
        "moves": move_localizations,
        "abilities": ability_localizations,
        "locations": location_localizations,
    }
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote Italian localization file to {output_path}")
    print(f"Moves localized: {len(move_localizations)}")
    print(f"Abilities localized: {len(ability_localizations)}")
    print(f"Locations localized: {len(location_localizations)}")


if __name__ == "__main__":
    main()
