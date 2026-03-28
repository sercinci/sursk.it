from fastapi.testclient import TestClient

from app.main import app


def test_healthcheck_shape() -> None:
    with TestClient(app) as client:
        response = client.get("/api/health")
        assert response.status_code == 200
        payload = response.json()
        assert payload["error"] is None
        assert payload["data"]["status"] == "ok"


def test_pokemon_search_by_number() -> None:
    with TestClient(app) as client:
        response = client.get("/api/pokemon", params={"q": "#252", "limit": 100})
        assert response.status_code == 200
        payload = response.json()
        results = payload["data"]
        assert any(entry["id"] == 252 for entry in results)
        treecko = next(entry for entry in results if entry["id"] == 252)
        assert treecko["ev_yield"] == {"speed": 1}


def test_pokemon_search_includes_hoenn_capturable_gen1_gen2() -> None:
    with TestClient(app) as client:
        response = client.get("/api/pokemon", params={"q": "#025", "limit": 100})
        assert response.status_code == 200
        payload = response.json()
        results = payload["data"]
        assert any(entry["id"] == 25 for entry in results)
        pikachu = next(entry for entry in results if entry["id"] == 25)
        assert pikachu["name"] == "pikachu"


def test_pokemon_detail_includes_abilities() -> None:
    with TestClient(app) as client:
        response = client.get("/api/pokemon/252")
        assert response.status_code == 200
        payload = response.json()
        pokemon = payload["data"]
        abilities = pokemon["abilities"]
        assert [ability["name"] for ability in abilities] == ["overgrow"]
        assert "unburden" not in [ability["name"] for ability in abilities]
        assert all(ability["description"] for ability in abilities)
        assert pokemon["ev_yield"] == {"speed": 1}


def test_pokemon_detail_localizes_abilities_for_italian() -> None:
    with TestClient(app) as client:
        response = client.get("/api/pokemon/252", params={"lang": "it"})
        assert response.status_code == 200
        payload = response.json()
        pokemon = payload["data"]
        abilities = pokemon["abilities"]
        assert abilities
        assert abilities[0]["name"] == "overgrow"
        assert abilities[0]["display_name"] == "Erbaiuto"
        assert "type Grass" not in abilities[0]["description"]
        assert abilities[0]["description"]


def test_pokemon_detail_uses_legacy_gen_2_5_types() -> None:
    with TestClient(app) as client:
        gardevoir_response = client.get("/api/pokemon/282")
        assert gardevoir_response.status_code == 200
        gardevoir = gardevoir_response.json()["data"]
        assert gardevoir["types"] == ["psychic"]

        jigglypuff_response = client.get("/api/pokemon/39")
        assert jigglypuff_response.status_code == 200
        jigglypuff = jigglypuff_response.json()["data"]
        assert jigglypuff["types"] == ["normal"]


def test_meta_types_excludes_fairy() -> None:
    with TestClient(app) as client:
        response = client.get("/api/meta/types")
        assert response.status_code == 200
        payload = response.json()
        assert "fairy" not in payload["data"]


def test_pokemon_search_filter_by_type() -> None:
    with TestClient(app) as client:
        response = client.get("/api/pokemon", params={"type": "fire", "limit": 100})
        assert response.status_code == 200
        payload = response.json()
        results = payload["data"]
        assert results
        assert all("fire" in [pokemon_type.lower() for pokemon_type in entry["types"]] for entry in results)


def test_pokemon_search_filter_by_multiple_types() -> None:
    with TestClient(app) as client:
        response = client.get("/api/pokemon", params={"type": "grass,poison", "limit": 100})
        assert response.status_code == 200
        payload = response.json()
        results = payload["data"]
        assert results
        assert all(
            {"grass", "poison"}.issubset({pokemon_type.lower() for pokemon_type in entry["types"]})
            for entry in results
        )


def test_pokemon_search_filter_by_ev_yield() -> None:
    with TestClient(app) as client:
        response = client.get("/api/pokemon", params={"ev_yield": "speed", "limit": 100})
        assert response.status_code == 200
        payload = response.json()
        results = payload["data"]
        assert results
        assert all(int(entry["ev_yield"].get("speed", 0)) > 0 for entry in results)


def test_pokemon_search_filter_by_hoenn_only() -> None:
    with TestClient(app) as client:
        response = client.get("/api/pokemon", params={"q": "#025", "hoenn_only": "true", "limit": 100})
        assert response.status_code == 200
        payload = response.json()
        assert payload["data"] == []


def test_move_detail_localized_with_lang_query() -> None:
    with TestClient(app) as client:
        response = client.get("/api/moves/tackle", params={"lang": "it"})
        assert response.status_code == 200
        payload = response.json()
        move = payload["data"]
        assert move["name"] == "tackle"
        assert move["display_name"] == "Azione"
        assert move["description"]
        assert move["description"] != "Inflicts regular damage with no additional effect."


def test_move_detail_localized_with_accept_language_header() -> None:
    with TestClient(app) as client:
        response = client.get(
            "/api/moves/tackle",
            headers={"Accept-Language": "it-IT,it;q=0.9,en;q=0.8"},
        )
        assert response.status_code == 200
        payload = response.json()
        move = payload["data"]
        assert move["display_name"] == "Azione"


def test_lang_query_overrides_accept_language() -> None:
    with TestClient(app) as client:
        response = client.get(
            "/api/moves/tackle",
            params={"lang": "en"},
            headers={"Accept-Language": "it-IT,it;q=0.9,en;q=0.8"},
        )
        assert response.status_code == 200
        payload = response.json()
        move = payload["data"]
        assert move["display_name"] is None
        assert move["description"] == "Inflicts regular damage with no additional effect."


def test_fairy_moves_are_mapped_to_legacy_normal_type() -> None:
    with TestClient(app) as client:
        response = client.get("/api/moves")
        assert response.status_code == 200
        payload = response.json()
        moves = payload["data"]
        moonblast = next(move for move in moves if move["name"] == "moonblast")
        assert moonblast["type"] == "normal"
        assert all(move["type"] != "fairy" for move in moves if move.get("type"))


def test_selected_move_detail_stays_localized_in_italian() -> None:
    with TestClient(app) as client:
        move_list_response = client.get("/api/moves", params={"lang": "it"})
        assert move_list_response.status_code == 200
        move_list_payload = move_list_response.json()
        moonblast_row = next(move for move in move_list_payload["data"] if move["name"] == "moonblast")
        assert moonblast_row["display_name"] == "Forza Lunare"
        assert moonblast_row["type"] == "normal"

        detail_response = client.get("/api/moves/moonblast", params={"lang": "it"})
        assert detail_response.status_code == 200
        detail_payload = detail_response.json()
        detail = detail_payload["data"]
        assert detail["display_name"] == "Forza Lunare"
        assert detail["description"]
        assert "the target" not in detail["description"].lower()
        assert "inflicts" not in detail["description"].lower()


def test_hoenn_location_localized_with_lang_query() -> None:
    with TestClient(app) as client:
        response = client.get("/api/locations/pokemmo/hoenn/dewford-town-area", params={"lang": "it"})
        assert response.status_code == 200
        payload = response.json()
        location = payload["data"]
        assert location["display_name"] == "Bluruvia"
        assert location["encounters"]
        assert any(
            encounter["method"] in {"Amo Vecchio", "Amo Buono", "Super Amo"}
            for encounter in location["encounters"]
        )
