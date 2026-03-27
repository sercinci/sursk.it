#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

REQUEST_TIMEOUT = 25
REQUEST_SLEEP_SECONDS = 0.03
USER_AGENT = "surskit/1.0 (pokemmo-hoenn-wiki-builder)"
WIKI_PARSE_API = "https://pokemmo.shoutwiki.com/w/api.php?action=parse&page={page}&prop=wikitext&format=json&formatversion=2"
WIKI_API = "https://pokemmo.shoutwiki.com/w/api.php"
POKEAPI_LOCATION_AREA_API = "https://pokeapi.co/api/v2/location-area/{name}"
POKEAPI_POKEMON_API = "https://pokeapi.co/api/v2/pokemon/{name}"
HOENN_CATEGORY_TITLE = "Category:Hoenn_locations"

RATE_LABELS = {
    "VC": "Very Common",
    "C": "Common",
    "U": "Uncommon",
    "R": "Rare",
    "VR": "Very Rare",
    "H": "Horde",
    "L": "Lure",
}

TIME_FIELDS = ("Morning", "Day", "Night")
ENCOUNTER_ICON_METHODS = {
    "long grass": "Grass",
    "cave": "Cave",
    "surfing": "Surfing",
    "underwater": "Underwater",
    "old rod": "Old Rod",
    "good rod": "Good Rod",
    "super rod": "Super Rod",
    "rock smash": "Rock Smash",
}
POKEAPI_METHOD_LABELS = {
    "walk": "Grass",
    "surf": "Surfing",
    "seaweed": "Underwater",
    "old-rod": "Old Rod",
    "good-rod": "Good Rod",
    "super-rod": "Super Rod",
    "rock-smash": "Rock Smash",
    "underwater": "Underwater",
}
NON_WILD_METHODS = {"gift", "unknown"}
NON_WILD_RATES = {"egg"}


def fetch_wikitext(page_title: str) -> str | None:
    page_slug = page_title.replace(" ", "_")
    request = Request(
        WIKI_PARSE_API.format(page=quote(page_slug)),
        headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
    )
    try:
        with urlopen(request, timeout=REQUEST_TIMEOUT) as response:
            payload = json.loads(response.read().decode("utf-8", "ignore"))
    except Exception:
        return None
    return payload.get("parse", {}).get("wikitext")


def fetch_json(url: str) -> dict | None:
    request = Request(
        url,
        headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
    )
    try:
        with urlopen(request, timeout=REQUEST_TIMEOUT) as response:
            return json.loads(response.read().decode("utf-8", "ignore"))
    except Exception:
        return None


def normalized_pokemon_name(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.lower())


def page_title_candidates(location_name: str, default_title: str) -> list[str]:
    route_match = re.search(r"hoenn-route-(\d+)-(area|underwater)$", location_name)
    if route_match:
        route = route_match.group(1)
        zone = route_match.group(2)
        if zone == "underwater":
            return [
                f"Hoenn Route {route} Underwater",
                f"Route {route} Underwater",
                f"Hoenn Route {route}",
                f"Route {route}",
            ]
        return [f"Hoenn Route {route}", f"Route {route}"]
    if location_name == "hoenn-victory-road-area":
        return ["Victory Road (Hoenn)", "Victory Road"]
    return [default_title]


def preferred_page_title(current: str, candidate: str) -> str:
    def score(value: str) -> tuple[int, int]:
        lowered = value.lower()
        if lowered.startswith("hoenn route "):
            return (4, -len(value))
        if lowered.startswith("route "):
            return (3, -len(value))
        if "underwater" in lowered:
            return (2, -len(value))
        return (1, -len(value))

    return candidate if score(candidate) > score(current) else current


def normalized_location_name_from_page_title(page_title: str) -> str:
    title = page_title.strip()
    route_match = re.fullmatch(r"(?:Hoenn\s+)?Route\s+(\d+)(?:\s+Underwater)?", title, flags=re.IGNORECASE)
    if route_match:
        route = route_match.group(1)
        suffix = "underwater" if "underwater" in title.lower() else "area"
        return f"hoenn-route-{route}-{suffix}"
    if title.lower() in {"victory road", "victory road (hoenn)"}:
        return "hoenn-victory-road-area"

    base = re.sub(r"\s*\([^)]*\)\s*", " ", title).strip()
    base = (
        base.replace("’", "'")
        .replace("&", " and ")
        .replace("é", "e")
        .replace("É", "E")
    )
    slug = re.sub(r"[^a-z0-9]+", "-", base.lower()).strip("-")
    slug = re.sub(r"-+", "-", slug)
    if slug.endswith("-area"):
        return slug
    return f"{slug}-area"


def fetch_hoenn_location_titles() -> list[str]:
    titles: list[str] = []
    continuation: str | None = None
    while True:
        params = {
            "action": "query",
            "list": "categorymembers",
            "cmtitle": HOENN_CATEGORY_TITLE,
            "cmnamespace": 0,
            "cmlimit": "max",
            "format": "json",
            "formatversion": 2,
        }
        if continuation:
            params["cmcontinue"] = continuation
        payload = fetch_json(f"{WIKI_API}?{urlencode(params)}") or {}
        members = payload.get("query", {}).get("categorymembers", [])
        for member in members:
            title = str(member.get("title", "")).strip()
            if title:
                titles.append(title)

        continuation = payload.get("continue", {}).get("cmcontinue")
        if not continuation:
            break

    return sorted(set(titles))


def extract_infobox_image_filename(wikitext: str) -> str | None:
    match = re.search(r"^\s*\|image\s*=\s*([^\n|]+)", wikitext, flags=re.IGNORECASE | re.MULTILINE)
    if not match:
        return None
    value = match.group(1).strip()
    if not value:
        return None
    return value.replace(" ", "_")


def build_file_image_entry(filename: str, label: str, repository) -> dict:
    normalized_filename = filename.replace(" ", "_")
    return {
        "label": label,
        "image_url": repository._mediawiki_upload_url(  # noqa: SLF001
            "https://images.shoutwiki.com/pokemmo", normalized_filename
        ),
        "source_url": (
            "https://pokemmo.shoutwiki.com/wiki/"
            f"{quote(f'File:{normalized_filename}')}"
        ),
    }


def parse_template_params(template_line: str) -> dict[str, str]:
    params: dict[str, str] = {}
    body = template_line
    if body.startswith("{{List/Catch|"):
        body = body[len("{{List/Catch|") :]
    if body.endswith("}}"):
        body = body[:-2]
    for part in body.split("|"):
        if "=" not in part:
            continue
        key, value = part.split("=", 1)
        params[key.strip()] = value.strip()
    return params


def parse_pokemon_id_from_url(url: str) -> int | None:
    match = re.search(r"/pokemon/(\d+)/?$", url)
    if not match:
        return None
    return int(match.group(1))


def pokemon_slug_candidates(name: str) -> list[str]:
    base = name.lower().strip()
    base = base.replace(" ", "-").replace(".", "").replace("'", "")
    base = base.replace("♀", "-f").replace("♂", "-m")
    base = re.sub(r"[^a-z0-9-]", "", base)
    candidates = [base]
    if "-" in base:
        candidates.append(base.replace("-", ""))
    return [candidate for candidate in candidates if candidate]


def resolve_pokemon_id(
    pokemon_name: str,
    pokemon_id_by_name: dict[str, int],
    cache: dict[str, int | None],
) -> int | None:
    normalized = normalized_pokemon_name(pokemon_name)
    if normalized in pokemon_id_by_name:
        return pokemon_id_by_name[normalized]
    if normalized in cache:
        return cache[normalized]

    resolved: int | None = None
    for slug in pokemon_slug_candidates(pokemon_name):
        payload = fetch_json(POKEAPI_POKEMON_API.format(name=quote(slug)))
        if not payload:
            continue
        pokemon_id = payload.get("id")
        if isinstance(pokemon_id, int):
            resolved = pokemon_id
            break
    cache[normalized] = resolved
    return resolved


def normalize_rate(rate_value: str) -> str:
    if not rate_value:
        return "Unknown"
    token = rate_value.strip()
    upper = token.upper()
    if upper in RATE_LABELS:
        return RATE_LABELS[upper]
    return token


def normalize_sub_location(raw_heading: str, default_sub_location: str) -> str:
    cleaned = raw_heading.strip()
    cleaned = re.sub(r"^Wild Encounters\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"^Pok[ée]mon\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = cleaned.strip(" -")
    return cleaned or default_sub_location


def normalize_method(raw_method: str) -> str:
    value = raw_method.strip()
    if not value:
        return "Unknown"
    lowered = value.lower()
    if lowered in {"tall grass", "long grass"}:
        return "Grass"
    if lowered == "rocks":
        return "Rock Smash"
    if lowered == "water":
        return "Surfing"
    return value


def is_wild_encounter_row(row: dict) -> bool:
    method = str(row.get("method", "")).strip().lower()
    if method in NON_WILD_METHODS:
        return False
    rate = str(row.get("rate", "")).strip().lower()
    if rate in NON_WILD_RATES:
        return False
    return True


def classify_category(rate_label: str) -> str:
    lowered = rate_label.lower()
    if "horde" in lowered:
        return "Horde"
    if "lure" in lowered:
        return "Lure"
    return "Wild"


def fallback_rate_label(chance: int) -> str:
    if chance >= 50:
        return "Very Common"
    if chance >= 25:
        return "Common"
    if chance >= 10:
        return "Uncommon"
    if chance >= 5:
        return "Rare"
    return "Very Rare"


def fallback_emerald_encounters_for_location_area(
    location_area_name: str,
    sub_location: str,
    pokemon_id_by_name: dict[str, int],
) -> list[dict]:
    payload = fetch_json(POKEAPI_LOCATION_AREA_API.format(name=quote(location_area_name)))
    if not payload:
        return []

    rows: list[dict] = []
    for pokemon_row in payload.get("pokemon_encounters", []):
        species_name = str(pokemon_row.get("pokemon", {}).get("name", "")).strip()
        species_url = str(pokemon_row.get("pokemon", {}).get("url", "")).strip()
        if not species_name:
            continue

        pokemon_id = pokemon_id_by_name.get(normalized_pokemon_name(species_name))
        if pokemon_id is None:
            pokemon_id = parse_pokemon_id_from_url(species_url)

        for version_detail in pokemon_row.get("version_details", []):
            if version_detail.get("version", {}).get("name") != "emerald":
                continue
            for encounter_detail in version_detail.get("encounter_details", []):
                method_key = str(encounter_detail.get("method", {}).get("name", "")).strip().lower()
                chance = int(encounter_detail.get("chance", 0))
                min_level = int(encounter_detail.get("min_level", 0))
                max_level = int(encounter_detail.get("max_level", 0))
                if min_level <= 0 or max_level <= 0:
                    continue
                level_range = str(min_level) if min_level == max_level else f"{min_level}-{max_level}"
                rows.append(
                    {
                        "pokemon_name": " ".join(part.capitalize() for part in species_name.split("-") if part),
                        "pokemon_id": pokemon_id,
                        "sub_location": sub_location,
                        "level_range": level_range,
                        "method": POKEAPI_METHOD_LABELS.get(method_key, method_key.replace("-", " ").title()),
                        "rate": fallback_rate_label(chance),
                        "period": None,
                        "category": "Wild",
                    }
                )
    return rows


def parse_table_fallback_encounters(
    wikitext: str,
    default_sub_location: str,
    pokemon_id_by_name: dict[str, int],
) -> list[dict]:
    rows: list[dict] = []
    pokemon_section = extract_heading_section(wikitext, r"Pok[ée]mon")
    if not pokemon_section:
        return rows
    row_blocks = re.findall(r"\|-\s*\n(.*?)(?=\n\|-|\n\|})", pokemon_section, flags=re.DOTALL)
    for block in row_blocks:
        pokemon_match = re.search(r"\{\{pkmn\|([^}|]+)", block, flags=re.IGNORECASE)
        if not pokemon_match:
            continue
        pokemon_name = pokemon_match.group(1).strip()
        pokemon_id = pokemon_id_by_name.get(normalized_pokemon_name(pokemon_name))

        cells: list[str] = []
        for raw_line in block.splitlines():
            if not raw_line.lstrip().startswith("|"):
                continue
            content = raw_line.lstrip().lstrip("|").strip()
            if not content:
                continue
            for segment in content.split("||"):
                value = segment.strip()
                if value:
                    cells.append(value)

        method = "Unknown"
        level_range = "Unknown"
        rate = "Unknown"

        for cell in cells:
            item_match = re.search(r"\{\{it\|([^}|]+)\}\}", cell, flags=re.IGNORECASE)
            if item_match:
                candidate = item_match.group(1).strip()
                if candidate.lower() in {"old rod", "good rod", "super rod"}:
                    method = candidate.title()

            icon_candidates = re.findall(r"\{\{([^}|]+?)\s+icon\}\}", cell, flags=re.IGNORECASE)
            for icon_name in reversed(icon_candidates):
                normalized_icon = icon_name.strip().lower()
                if normalized_icon in ENCOUNTER_ICON_METHODS:
                    method = ENCOUNTER_ICON_METHODS[normalized_icon]
                    break

            if method == "Unknown":
                simple_method = normalize_method(re.sub(r"\{\{.*?\}\}", "", cell).strip())
                if simple_method.lower() in {value.lower() for value in ENCOUNTER_ICON_METHODS.values()}:
                    method = simple_method

            level_match = re.fullmatch(r"(?:Lv\.)?\s*([0-9?]+(?:-[0-9?]+)?)", cell, flags=re.IGNORECASE)
            if level_match:
                level_range = level_match.group(1)
                continue

            rate_match = re.search(
                r"\b(Very Common|Common|Uncommon|Rare|Very Rare|Horde|Lure)\b",
                cell,
                flags=re.IGNORECASE,
            )
            if rate_match:
                rate = normalize_rate(rate_match.group(1))
                continue

        rows.append(
            {
                "pokemon_name": pokemon_name,
                "pokemon_id": pokemon_id,
                "sub_location": default_sub_location,
                "level_range": level_range,
                "method": method,
                "rate": rate,
                "period": None,
                "category": classify_category(rate),
            }
        )
    return rows


def extract_heading_section(wikitext: str, heading_pattern: str) -> str | None:
    lines = wikitext.splitlines()
    heading_regex = re.compile(r"^(=+)\s*(.*?)\s*\1\s*$")
    target_regex = re.compile(rf"^{heading_pattern}$", flags=re.IGNORECASE)

    start_index = None
    heading_level = None
    for index, line in enumerate(lines):
        match = heading_regex.match(line.strip())
        if not match:
            continue
        title = match.group(2).strip()
        if not target_regex.match(title):
            continue
        start_index = index + 1
        heading_level = len(match.group(1))
        break

    if start_index is None or heading_level is None:
        return None

    collected: list[str] = []
    for line in lines[start_index:]:
        match = heading_regex.match(line.strip())
        if match and len(match.group(1)) <= heading_level:
            break
        collected.append(line)
    return "\n".join(collected)


def extract_layout_labels_and_images(
    wikitext: str,
    default_sub_location: str,
    repository,
) -> tuple[list[str], list[dict]]:
    layout_section = extract_heading_section(wikitext, r"Layout")
    if not layout_section:
        block_match = re.search(
            r"\{\{List/Header\|Name=Layout[^\n]*\}\}([\s\S]*?)\{\{List/Footer\}\}",
            wikitext,
            flags=re.IGNORECASE,
        )
        if block_match:
            layout_section = block_match.group(1)
    if not layout_section:
        return [], []

    layout_labels: list[str] = []
    birdview_images: list[dict] = []
    pending_labels: list[tuple[str, str | None]] = []
    current_context: str | None = None

    def normalize_context(value: str | None) -> str | None:
        if not value:
            return None
        token = value.strip()
        if not token:
            return None
        lowered = token.lower()
        if lowered in {"layout"}:
            return None
        return token

    for line in layout_section.splitlines():
        header_match = re.search(
            r"\{\{List/Header\|Name=([^|\}\n]+)",
            line,
            flags=re.IGNORECASE,
        )
        if header_match:
            current_context = normalize_context(header_match.group(1))

        for raw_label in re.findall(r"'''([^\n]+?)'''", line):
            normalized = normalize_sub_location(raw_label, default_sub_location).strip()
            if not normalized or normalized.lower() == "layout":
                continue
            if normalized not in layout_labels:
                layout_labels.append(normalized)
            pending_labels.append((normalized, current_context))

        for filename in re.findall(r"\[\[File:([^|\]]+)", line, flags=re.IGNORECASE):
            normalized_filename = filename.strip()
            if not normalized_filename:
                continue

            resolved_label = default_sub_location
            if pending_labels:
                base_label, context = pending_labels.pop(0)
                if context and context.lower() in {"high tide", "low tide"}:
                    resolved_label = f"{context} {base_label}"
                else:
                    resolved_label = base_label

            birdview_images.append(
                build_file_image_entry(normalized_filename, resolved_label, repository)
            )

    deduped_by_url: dict[str, dict] = {}
    for row in birdview_images:
        image_url = row.get("image_url")
        if not image_url:
            continue
        deduped_by_url[image_url] = row

    return layout_labels, list(deduped_by_url.values())


def parse_encounters(
    wikitext: str,
    default_sub_location: str,
    pokemon_id_by_name: dict[str, int],
) -> list[dict]:
    pokemon_section = extract_heading_section(wikitext, r"Pok[ée]mon")
    if not pokemon_section:
        pokemon_section = wikitext

    current_sub_location = default_sub_location
    rows: list[dict] = []

    heading_pattern = re.compile(r"^\s*===+\s*(.*?)\s*===+\s*$")
    catch_pattern = re.compile(r"\{\{List/Catch\|[^\n]*\}\}")
    wildentry_pattern = re.compile(r"\{\{wildentry\s*\|[^\n]*\}\}", flags=re.IGNORECASE)

    for line in pokemon_section.splitlines():
        heading_match = heading_pattern.match(line)
        if heading_match:
            current_sub_location = normalize_sub_location(
                heading_match.group(1), default_sub_location
            )
            continue

        for template in catch_pattern.findall(line):
            params = parse_template_params(template)
            pokemon_name = params.get("Pokemon", "").strip()
            if not pokemon_name:
                continue
            level_range = params.get("Level", "").strip() or "Unknown"
            method = normalize_method(params.get("Location", "Unknown"))
            pokemon_id = pokemon_id_by_name.get(normalized_pokemon_name(pokemon_name))

            emitted = False
            all_rate = params.get("All") or params.get("Rarity")
            if all_rate:
                rate = normalize_rate(all_rate)
                rows.append(
                    {
                        "pokemon_name": pokemon_name,
                        "pokemon_id": pokemon_id,
                        "sub_location": current_sub_location,
                        "level_range": level_range,
                        "method": method,
                        "rate": rate,
                        "period": None,
                        "category": classify_category(rate),
                    }
                )
                emitted = True

            for field in TIME_FIELDS:
                field_value = params.get(field)
                if not field_value:
                    continue
                rate = normalize_rate(field_value)
                rows.append(
                    {
                        "pokemon_name": pokemon_name,
                        "pokemon_id": pokemon_id,
                        "sub_location": current_sub_location,
                        "level_range": level_range,
                        "method": method,
                        "rate": rate,
                        "period": field,
                        "category": classify_category(rate),
                    }
                )
                emitted = True

            if not emitted:
                rows.append(
                    {
                        "pokemon_name": pokemon_name,
                        "pokemon_id": pokemon_id,
                        "sub_location": current_sub_location,
                        "level_range": level_range,
                        "method": method,
                        "rate": "Unknown",
                        "period": None,
                        "category": "Wild",
                    }
                )

        for template in wildentry_pattern.findall(line):
            body = template
            body = re.sub(r"^\{\{wildentry\s*\|", "", body, flags=re.IGNORECASE).rstrip("}")
            fields = [part.strip() for part in body.split("|")]
            if len(fields) < 6:
                continue
            pokemon_name = fields[0]
            method = normalize_method(fields[3])
            level_range = fields[4] or "Unknown"
            rate = normalize_rate(fields[5])
            pokemon_id = pokemon_id_by_name.get(normalized_pokemon_name(pokemon_name))
            rows.append(
                {
                    "pokemon_name": pokemon_name,
                    "pokemon_id": pokemon_id,
                    "sub_location": current_sub_location,
                    "level_range": level_range,
                    "method": method,
                    "rate": rate,
                    "period": None,
                    "category": classify_category(rate),
                }
                )

    rows.extend(
        parse_table_fallback_encounters(
            wikitext,
            default_sub_location=default_sub_location,
            pokemon_id_by_name=pokemon_id_by_name,
        )
    )

    deduped = {
        (
            row["pokemon_name"],
            row["pokemon_id"],
            row["sub_location"],
            row["level_range"],
            row["method"],
            row["rate"],
            row["period"],
            row["category"],
        ): row
        for row in rows
    }

    return [
        deduped[key]
        for key in sorted(
            deduped.keys(),
            key=lambda item: (
                str(item[0]).lower(),
                str(item[4]).lower(),
                str(item[2]).lower(),
                str(item[3]).lower(),
                str(item[5]).lower(),
                str(item[6] or "").lower(),
            ),
        )
    ]


def apply_layout_sub_location_fallback(
    encounters: list[dict],
    layout_labels: list[str],
    default_sub_location: str,
) -> list[dict]:
    if not encounters:
        return encounters

    normalized_labels: list[str] = []
    for label in layout_labels:
        cleaned = str(label).strip()
        if not cleaned:
            continue
        if cleaned.lower() == "layout":
            continue
        if cleaned not in normalized_labels:
            normalized_labels.append(cleaned)

    if not normalized_labels:
        return encounters

    explicit_sub_locations = {
        str(row.get("sub_location") or "").strip()
        for row in encounters
        if str(row.get("sub_location") or "").strip()
        not in {"", default_sub_location, "Layout", "layout"}
    }

    expanded_rows: list[dict] = []
    for row in encounters:
        sub_location = str(row.get("sub_location") or "").strip()
        if not sub_location:
            sub_location = default_sub_location

        # "Layout" is never a valid sub-area label.
        if sub_location.lower() == "layout":
            sub_location = default_sub_location

        # If no explicit sub-area is present in encounter rows, apply layout labels.
        if not explicit_sub_locations and sub_location == default_sub_location:
            for label in normalized_labels:
                expanded_rows.append({**row, "sub_location": label})
            continue

        expanded_rows.append({**row, "sub_location": sub_location})

    return expanded_rows


def dedupe_sort_encounters(rows: list[dict]) -> list[dict]:
    deduped = {
        (
            row.get("pokemon_name"),
            row.get("pokemon_id"),
            row.get("sub_location"),
            row.get("level_range"),
            row.get("method"),
            row.get("rate"),
            row.get("period"),
            row.get("category"),
        ): row
        for row in rows
    }
    return [
        deduped[key]
        for key in sorted(
            deduped.keys(),
            key=lambda item: (
                str(item[0]).lower(),
                str(item[4]).lower(),
                str(item[2]).lower(),
                str(item[3]).lower(),
                str(item[5]).lower(),
                str(item[6] or "").lower(),
            ),
        )
    ]


def resolve_missing_pokemon_ids(
    rows: list[dict],
    pokemon_id_by_name: dict[str, int],
    cache: dict[str, int | None],
) -> list[dict]:
    for row in rows:
        if row.get("pokemon_id") is not None:
            continue
        pokemon_name = str(row.get("pokemon_name", "")).strip()
        if not pokemon_name:
            continue
        row["pokemon_id"] = resolve_pokemon_id(pokemon_name, pokemon_id_by_name, cache)
    return rows


def build_dataset() -> list[dict]:
    project_root = Path(__file__).resolve().parents[1]
    backend_root = project_root / "backend"
    if str(backend_root) not in sys.path:
        sys.path.insert(0, str(backend_root))

    from app.providers.repository import (  # pylint: disable=import-outside-toplevel
        NON_CAPTURABLE_POKEMON_IDS,
        DataRepository,
    )

    repository = DataRepository(backend_root / "app" / "data")
    repository.load()
    category_titles = fetch_hoenn_location_titles()
    seeds_by_name: dict[str, str] = {}
    for page_title in category_titles:
        normalized_name = normalized_location_name_from_page_title(page_title)
        existing = seeds_by_name.get(normalized_name)
        if not existing:
            seeds_by_name[normalized_name] = page_title
            continue
        seeds_by_name[normalized_name] = preferred_page_title(existing, page_title)
    location_seeds = sorted(seeds_by_name.items(), key=lambda item: item[0])

    pokemon_id_by_name = {
        normalized_pokemon_name(pokemon.name): pokemon.id for pokemon in repository.pokemon
    }
    pokemon_id_resolution_cache: dict[str, int | None] = {}

    output_rows: list[dict] = []
    for index, (normalized_name, source_page_title) in enumerate(location_seeds, start=1):
        default_title = repository._hoenn_page_title(normalized_name)  # noqa: SLF001
        candidates = [source_page_title, *page_title_candidates(normalized_name, default_title)]
        deduped_candidates: list[str] = []
        for candidate in candidates:
            if candidate not in deduped_candidates:
                deduped_candidates.append(candidate)
        candidates = deduped_candidates

        selected_title = None
        selected_wikitext = None
        for candidate in candidates:
            wikitext = fetch_wikitext(candidate)
            if wikitext:
                selected_title = candidate
                selected_wikitext = wikitext
                break

        if not selected_wikitext:
            print(f"[WARN] failed to fetch wiki page for {normalized_name} (tried {candidates})")
            selected_title = default_title
            selected_wikitext = ""

        default_sub_location = repository._format_location_display_name(normalized_name)  # noqa: SLF001
        layout_labels, layout_birdview_images = extract_layout_labels_and_images(
            selected_wikitext,
            default_sub_location=default_sub_location,
            repository=repository,
        )
        encounters = parse_encounters(
            selected_wikitext,
            default_sub_location=default_sub_location,
            pokemon_id_by_name=pokemon_id_by_name,
        )
        encounters = apply_layout_sub_location_fallback(
            encounters,
            layout_labels=layout_labels,
            default_sub_location=default_sub_location,
        )
        encounters = resolve_missing_pokemon_ids(
            encounters,
            pokemon_id_by_name=pokemon_id_by_name,
            cache=pokemon_id_resolution_cache,
        )
        if normalized_name.endswith("-underwater"):
            encounters = [
                row
                for row in encounters
                if str(row.get("method", "")).strip().lower() == "underwater"
            ]
        elif re.search(r"hoenn-route-\d+-area$", normalized_name):
            encounters = [
                row
                for row in encounters
                if str(row.get("method", "")).strip().lower() != "underwater"
            ]
            encounters = [
                row
                for row in encounters
                if row["pokemon_id"] is None
                or int(row["pokemon_id"]) not in NON_CAPTURABLE_POKEMON_IDS
            ]
        if not encounters:
            for source_name in repository._expand_location_aliases(normalized_name):  # noqa: SLF001
                source_label = repository._format_location_display_name(source_name)  # noqa: SLF001
                encounters.extend(
                    fallback_emerald_encounters_for_location_area(
                        source_name,
                        source_label,
                        pokemon_id_by_name=pokemon_id_by_name,
                    )
                )
            encounters = resolve_missing_pokemon_ids(
                encounters,
                pokemon_id_by_name=pokemon_id_by_name,
                cache=pokemon_id_resolution_cache,
            )
            encounters = apply_layout_sub_location_fallback(
                encounters,
                layout_labels=layout_labels,
                default_sub_location=default_sub_location,
            )
            if normalized_name.endswith("-underwater"):
                encounters = [
                    row
                    for row in encounters
                    if str(row.get("method", "")).strip().lower() == "underwater"
                ]
            elif re.search(r"hoenn-route-\d+-area$", normalized_name):
                encounters = [
                    row
                    for row in encounters
                    if str(row.get("method", "")).strip().lower() != "underwater"
                ]
            encounters = [
                row
                for row in encounters
                if row["pokemon_id"] is None
                or int(row["pokemon_id"]) not in NON_CAPTURABLE_POKEMON_IDS
            ]
        encounters = [
            row
            for row in encounters
            if row["pokemon_id"] is None
            or int(row["pokemon_id"]) not in NON_CAPTURABLE_POKEMON_IDS
        ]
        encounters = [row for row in encounters if is_wild_encounter_row(row)]
        encounters = dedupe_sort_encounters(encounters)
        if not encounters:
            continue

        image_filename = extract_infobox_image_filename(selected_wikitext)
        visuals = repository._build_location_visuals(normalized_name)  # noqa: SLF001
        birdview_images: list[dict] = []
        if image_filename:
            birdview_images.append(
                build_file_image_entry(image_filename, default_sub_location, repository)
            )
        birdview_images.extend(layout_birdview_images)
        if not birdview_images:
            fallback_image_url = visuals.get("birdview_image_url")
            if isinstance(fallback_image_url, str) and fallback_image_url:
                birdview_images.append(
                    {
                        "label": default_sub_location,
                        "image_url": fallback_image_url,
                        "source_url": visuals.get("birdview_source_url"),
                    }
                )

        deduped_birdview_by_url: dict[str, dict] = {}
        for image in birdview_images:
            image_url = image.get("image_url")
            if not image_url:
                continue
            deduped_birdview_by_url[image_url] = image
        birdview_images = list(deduped_birdview_by_url.values())

        birdview_image_url = birdview_images[0]["image_url"] if birdview_images else visuals.get("birdview_image_url")
        birdview_source_url = (
            birdview_images[0].get("source_url") if birdview_images else visuals.get("birdview_source_url")
        )

        page_url = (
            "https://pokemmo.shoutwiki.com/wiki/"
            f"{quote(selected_title.replace(' ', '_'))}"
        )

        output_rows.append(
            {
                "name": normalized_name,
                "display_name": repository._format_location_display_name(normalized_name),  # noqa: SLF001
                "birdview_image_url": birdview_image_url,
                "birdview_source_url": birdview_source_url,
                "birdview_images": birdview_images,
                "map_image_url": visuals.get("map_image_url"),
                "map_source_url": visuals.get("map_source_url"),
                "source_url": page_url,
                "encounters": encounters,
            }
        )

        if index % 10 == 0:
            print(f"Processed {index}/{len(location_seeds)} Hoenn locations...")
        time.sleep(REQUEST_SLEEP_SECONDS)

    output_rows.sort(key=lambda row: str(row["name"]))
    return output_rows


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    output_path = project_root / "backend" / "app" / "data" / "pokemmo_hoenn_locations.json"
    rows = build_dataset()
    output_path.write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")
    with_encounters = sum(1 for row in rows if row.get("encounters"))
    print(f"Wrote {len(rows)} rows to {output_path}")
    print(f"Rows with encounter data: {with_encounters}/{len(rows)}")


if __name__ == "__main__":
    main()
