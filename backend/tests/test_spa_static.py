from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.main import SPAStaticFiles


def test_spa_static_serves_index_for_client_side_routes(tmp_path: Path) -> None:
    index_file = tmp_path / "index.html"
    index_file.write_text("<!doctype html><title>Sursk.it</title><div id='app'></div>")

    app = FastAPI()
    app.mount("/", SPAStaticFiles(directory=tmp_path, html=True), name="spa")

    with TestClient(app) as client:
        response = client.get("/locations/ever-grande-city-area")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert "Sursk.it" in response.text


def test_spa_static_keeps_api_like_paths_as_json_404(tmp_path: Path) -> None:
    (tmp_path / "index.html").write_text("<!doctype html><div id='app'></div>")

    app = FastAPI()
    app.mount("/", SPAStaticFiles(directory=tmp_path, html=True), name="spa")

    with TestClient(app) as client:
        response = client.get("/api/missing")

    assert response.status_code == 404
    assert response.headers["content-type"].startswith("application/json")
    assert response.json()["error"]["code"] == "http_404"
