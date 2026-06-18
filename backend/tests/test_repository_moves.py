from pathlib import Path

from app.providers.repository import DataRepository


def load_repository() -> DataRepository:
    repository = DataRepository(Path(__file__).resolve().parents[1] / "app" / "data")
    repository.load()
    return repository


def test_renamed_move_stats_resolve_for_pokemon_rows() -> None:
    repository = load_repository()

    psyduck_moves = {move.name: move for move in repository.list_pokemon_moves(54)}
    snowscape = psyduck_moves["snowscape"]
    assert snowscape.type == "ice"
    assert snowscape.category == "status"
    assert snowscape.power is None
    assert snowscape.pp == 10
    assert snowscape.accuracy is None

    vulpix_moves = {move.name: move for move in repository.list_pokemon_moves(37)}
    faint_attack = vulpix_moves["faint-attack"]
    assert faint_attack.type == "dark"
    assert faint_attack.category == "physical"
    assert faint_attack.power == 60
    assert faint_attack.pp == 20
    assert faint_attack.accuracy is None


def test_missing_move_catalog_rows_are_available_with_stats() -> None:
    repository = load_repository()

    pikachu_moves = {move.name: move for move in repository.list_pokemon_moves(25)}
    follow_me = pikachu_moves["follow-me"]
    assert follow_me.type == "normal"
    assert follow_me.category == "status"
    assert follow_me.power is None
    assert follow_me.pp == 20
    assert follow_me.accuracy is None

    volt_tackle = pikachu_moves["volt-tackle"]
    assert volt_tackle.type == "electric"
    assert volt_tackle.category == "physical"
    assert volt_tackle.power == 120
    assert volt_tackle.pp == 15
    assert volt_tackle.accuracy == 100


def test_legacy_move_slugs_alias_to_pokemmo_names() -> None:
    repository = load_repository()

    assert repository.get_move_detail("feint-attack").name == "faint-attack"
    assert repository.get_move_detail("self-destruct").name == "selfdestruct"
    assert repository.get_move_detail("smokescreen").name == "smoke-screen"


def test_pokemon_move_rows_include_all_locale_names() -> None:
    repository = load_repository()

    machop_moves = {move.name: move for move in repository.list_pokemon_moves(66, locale="en")}
    close_combat = machop_moves["close-combat"]

    assert close_combat.display_name is None
    assert close_combat.localized_names["en"] == "Close Combat"
    assert close_combat.localized_names["it"] == "Zuffa"

    machop_moves_it = {move.name: move for move in repository.list_pokemon_moves(66, locale="it")}
    assert machop_moves_it["close-combat"].display_name == "Zuffa"
