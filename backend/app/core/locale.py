from __future__ import annotations

SUPPORTED_LOCALES = {"en", "it"}
DEFAULT_LOCALE = "en"


def normalize_locale(value: str | None) -> str | None:
    if not value:
        return None
    token = value.strip().lower().replace("_", "-")
    if not token:
        return None
    base = token.split("-", 1)[0]
    if base in SUPPORTED_LOCALES:
        return base
    return None


def resolve_locale(preferred: str | None, accept_language: str | None) -> str:
    direct = normalize_locale(preferred)
    if direct:
        return direct

    if accept_language:
        for part in accept_language.split(","):
            language = part.split(";", 1)[0]
            resolved = normalize_locale(language)
            if resolved:
                return resolved

    return DEFAULT_LOCALE
