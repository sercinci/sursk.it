# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

**Backend** (from repo root, venv must be active):
```bash
source .venv/bin/activate
pip install -r backend/requirements-dev.txt
cd backend && uvicorn app.main:app --reload   # http://localhost:8000
# or via Makefile:
make backend
```

**Frontend** (second terminal):
```bash
cd frontend && npm install && npm run dev     # http://localhost:5173
# or:
make frontend
```

**Tests** (from repo root, venv active):
```bash
pytest                  # runs backend/tests/
pytest backend/tests/test_api_smoke.py        # single test file
```

**Build frontend for production**:
```bash
cd frontend && npm run build    # outputs to frontend/dist/
# In Docker the dist is copied to backend/static/ automatically
```

**Regenerate data** (run in order, calls external APIs):
```bash
python3 scripts/build_data.py
python3 scripts/build_pokemmo_hoenn_locations.py
python3 scripts/augment_hoenn_crossgen_pokemon.py
python3 scripts/build_it_localization.py
```

## Architecture

This is a monorepo with a FastAPI backend and a Vue 3 frontend deployed as a single Docker container.

### Backend (`backend/`)

- **Startup**: `DataRepository` loads all JSON files from `backend/app/data/` into memory and builds indexes by id, name, type, and move. A single `PokemonService` instance (stored on `app.state`) wraps the repository.
- **Layers**: `api/routes.py` → `services/pokemon_service.py` → `providers/repository.py` → `app/data/*.json`
- **API envelope**: All responses use `ApiEnvelope[T]` with `data`, `meta`, and `error` fields. Use `success()` / `failure()` helpers from `app/schemas/common.py` — never return raw dicts from route handlers.
- **Locale**: Resolved per-request in `app/core/locale.py` via `?lang=` query param or `Accept-Language` header; passed as a dependency to routes and down to the service/repository.
- **SPA serving**: In production, if `backend/static/` exists, FastAPI mounts it as an SPA (all unknown paths → `index.html`) via the custom `SPAStaticFiles` class in `main.py`.

### Frontend (`frontend/src/`)

- **Stack**: Vue 3, TypeScript, Vite, TailwindCSS, TanStack Vue Query (data fetching), Pinia (filters state), vue-router.
- **`@` alias** resolves to `frontend/src/`.
- **API client** (`src/api/client.ts`): All calls go through `request<T>()` which hits `VITE_API_BASE` (default `/api`) and appends `?lang=` automatically. Evolution chains are the only data fetched directly from PokeAPI (client-side), not from the backend.
- **Types** (`src/types.ts`): Single source of truth for all API response shapes; mirrors Pydantic schemas in `backend/app/schemas/domain.py`.
- **Dev proxy**: Vite proxies `/api` → `http://localhost:8000`, so no CORS issues during development.

### Data pipeline

Pre-generated JSON files in `backend/app/data/` are committed and served directly — no database, no runtime scraping. Scripts in `scripts/` regenerate these files from PokeAPI and PokeMMO wiki sources. Commit regenerated data together with any code changes that depend on it.

### PokeMMO game settings

The data targets PokeMMO with these specific settings, which determine which Pokemon, moves, and TMs are valid:

- **Pokemon types**: generation 2–5 (i.e. types introduced up to Gen 5 are present; Fairy type from Gen 6 is normalized to Normal for PokeMMO compatibility)
- **Leveling move set**: generation 5 (moves learned by level-up use Gen 5 learnsets)
- **TM learn set**: generation 9 (TM compatibility uses Gen 9 learnsets)

Primary data sources: [PokeMMO ShoutWiki – Hoenn](https://pokemmo.shoutwiki.com/wiki/Hoenn), [PokeMMO Hub Pokédex](https://pokemmohub.com/tools/pokedex/)

### Deployment

Single Docker image: Node stage builds frontend, Python stage installs backend deps, `frontend/dist` is copied to `backend/static/`, FastAPI serves both. Deployed on Render via `render.yaml`.
