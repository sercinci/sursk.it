from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes import router as api_router
from app.core.config import APP_DOMAIN, APP_NAME, DATA_DIR, STATIC_DIR
from app.providers.repository import DataRepository
from app.schemas.common import failure, success
from app.services.pokemon_service import PokemonService


class SPAStaticFiles(StaticFiles):
    async def get_response(self, path: str, scope):
        if path == "api" or path.startswith("api/"):
            payload = failure(
                code="http_404",
                message=f"API route '/{path}' not found",
            ).model_dump()
            return JSONResponse(status_code=404, content=payload)

        response = await super().get_response(path, scope)
        if response.status_code == 404:
            return await super().get_response("index.html", scope)
        return response


@asynccontextmanager
async def lifespan(app: FastAPI):
    repository = DataRepository(data_dir=DATA_DIR)
    repository.load()
    app.state.pokemon_service = PokemonService(repository)
    yield


app = FastAPI(title=APP_NAME, version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(HTTPException)
async def http_exception_handler(_request: Request, exc: HTTPException) -> JSONResponse:
    payload = failure(
        code=f"http_{exc.status_code}",
        message=str(exc.detail),
    ).model_dump()
    return JSONResponse(status_code=exc.status_code, content=payload)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    _request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    payload = failure(
        code="validation_error",
        message="Request validation failed",
        details=exc.errors(),
    ).model_dump()
    return JSONResponse(status_code=422, content=payload)


app.include_router(api_router, prefix="/api", tags=["pokedex"])


if STATIC_DIR.exists():
    app.mount("/", SPAStaticFiles(directory=STATIC_DIR, html=True), name="spa")
else:

    @app.get("/", tags=["root"])
    def root():
        return success(
            data={
                "name": APP_NAME,
                "domain": APP_DOMAIN,
                "docs": "/docs",
                "message": "Frontend build not found. Run frontend build or use docker build.",
            }
        )
