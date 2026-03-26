from __future__ import annotations

from pydantic import BaseModel, Field


class PokemonAbility(BaseModel):
    name: str
    display_name: str | None = None
    description: str


class Pokemon(BaseModel):
    id: int
    name: str
    types: list[str]
    abilities: list[PokemonAbility] = Field(default_factory=list)
    ev_yield: dict[str, int] = Field(default_factory=dict)
    stats: dict[str, int]
    moves: list[str]
    sprites: dict[str, str | None]
    locations: list[str] = Field(default_factory=list)


class PokemonListItem(BaseModel):
    id: int
    name: str
    types: list[str]
    sprite: str | None = None
    ev_yield: dict[str, int] = Field(default_factory=dict)


class MoveLearnMethod(BaseModel):
    method: str
    level: int | None = None


class Move(BaseModel):
    name: str
    display_name: str | None = None
    type: str | None = None
    category: str | None = None
    power: int | None = None
    pp: int | None = None
    accuracy: int | None = None


class PokemonMove(Move):
    description: str | None = None
    methods: list[MoveLearnMethod] = Field(default_factory=list)


class MoveLearner(BaseModel):
    pokemon_id: int
    pokemon_name: str
    pokemon_sprite: str | None = None
    methods: list[MoveLearnMethod] = Field(default_factory=list)


class MoveTmPurchaseOption(BaseModel):
    location: str
    price_pokeyen: int | None = None
    price_text: str | None = None


class MoveTmPurchase(MoveTmPurchaseOption):
    secondary: MoveTmPurchaseOption | None = None


class MoveDetail(BaseModel):
    name: str
    display_name: str | None = None
    description: str | None = None
    tm_purchase: MoveTmPurchase | None = None
    learners: list[MoveLearner] = Field(default_factory=list)


class Location(BaseModel):
    name: str
    display_name: str | None = None
    pokemon_ids: list[int] = Field(default_factory=list)


class LocationEncounter(BaseModel):
    pokemon_name: str
    pokemon_id: int | None = None
    sub_location: str | None = None
    level_range: str
    method: str
    rate: str
    period: str | None = None
    category: str


class LocationBirdviewImage(BaseModel):
    label: str | None = None
    image_url: str
    source_url: str | None = None


class LocationDetail(BaseModel):
    name: str
    display_name: str
    birdview_image_url: str | None = None
    birdview_source_url: str | None = None
    birdview_images: list[LocationBirdviewImage] = Field(default_factory=list)
    map_image_url: str | None = None
    map_source_url: str | None = None
    source_url: str | None = None
    encounters: list[LocationEncounter] = Field(default_factory=list)
