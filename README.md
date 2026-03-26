# cater.py

`cater.py` is a single-deploy Pokédex platform for Generation 3 data.

- Backend: FastAPI (authoritative API)
- Frontend: Vue 3 + Vite + TypeScript
- Data: pre-built JSON files (no runtime scraping)
- Deployment: Docker (Render primary, Koyeb fallback)
- Domain: `caterp.ie`

Recommended local Python: `3.14`.

## Monorepo Layout

- `backend/`: FastAPI app, schemas, services, providers, static JSON data
- `frontend/`: Vue app (Router, Pinia, Tailwind, TanStack Query)
- `scripts/build_data.py`: pre-build data pipeline from PokéAPI

## API Endpoints

All API responses use:

```json
{
  "data": {},
  "meta": {},
  "error": null
}
```

Available endpoints:

- `GET /api/pokemon?q=&type=&move=&limit=&offset=`
- `GET /api/pokemon/{id}`
- `GET /api/pokemon/{id}/moves`
- `GET /api/moves`
- `GET /api/moves/{name}`
- `GET /api/locations`
- `GET /api/locations/pokemmo/hoenn`
- `GET /api/locations/pokemmo/hoenn/{location_name}`
- `GET /api/meta/types`
- `GET /api/health`

Locale is selected without a path prefix:

- Query param override: `?lang=it` (or `?lang=en`)
- Fallback: `Accept-Language` header
- Default: English (`en`)

## Local Development

### 1) Backend

```bash
python3.14 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
cd backend
uvicorn app.main:app --reload
```

Backend runs on `http://localhost:8000`.

### 2) Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on `http://localhost:5173` and proxies `/api` to `localhost:8000`.

## Data Pipeline

Generate full Gen 3 JSON from PokéAPI:

```bash
python3 scripts/build_data.py
```

This writes:

- `backend/app/data/pokemon.json`
- `backend/app/data/moves.json`
- `backend/app/data/locations.json`

A small starter dataset is already committed so the app works out of the box.

Generate Italian localization data:

```bash
python3 scripts/build_it_localization.py
```

This writes `backend/app/data/localization_it.json` with:

- Moves and locations from [PokemonCentral](https://wiki.pokemoncentral.it/)
- Pokémon ability names/descriptions from PokéAPI

## Tests

```bash
python3.14 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements-dev.txt
pytest
```

## Docker

Build and run the full stack in one container:

```bash
docker build -t cater-py .
docker run --rm -p 8000:8000 cater-py
```

Then open `http://localhost:8000`.

## Deploy to Render + `caterp.ie`

1. Create a Render Web Service from this repository using Docker.
2. Render reads `render.yaml` and builds the container.
3. Add your custom domain `caterp.ie` in Render service settings.
4. Point DNS records from your registrar to Render as instructed in the Render dashboard.

## Koyeb Fallback

Use the same `Dockerfile` to deploy as a Koyeb Web Service and attach `caterp.ie` there if needed.
