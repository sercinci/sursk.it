export interface ApiError {
  code: string;
  message: string;
  details?: unknown;
}

export interface ApiEnvelope<T> {
  data: T;
  meta: Record<string, unknown>;
  error: ApiError | null;
}

export interface PokemonListItem {
  id: number;
  name: string;
  types: string[];
  sprite: string | null;
  ev_yield: Record<string, number>;
}

export interface PokemonListQuery {
  q?: string;
  type?: string;
  ev_yield?: string;
  hoenn_only?: boolean;
  limit?: number;
  offset?: number;
}

export interface PokemonAbility {
  name: string;
  display_name?: string | null;
  description: string;
}

export interface Pokemon {
  id: number;
  name: string;
  types: string[];
  abilities: PokemonAbility[];
  ev_yield: Record<string, number>;
  stats: Record<string, number>;
  moves: string[];
  sprites: Record<string, string | null>;
  locations: string[];
}

export interface PokemonEvolutionStage {
  id: number | null;
  name: string;
  sprite: string | null;
}

export interface PokemonEvolutionMethod {
  trigger: string | null;
  min_level: number | null;
  item_name: string | null;
  item_sprite: string | null;
  held_item_name: string | null;
  held_item_sprite: string | null;
  min_happiness: number | null;
  min_beauty: number | null;
  min_affection: number | null;
  time_of_day: string | null;
  trade_species_name: string | null;
}

export interface PokemonEvolutionLink {
  pokemon: PokemonEvolutionStage;
  method: PokemonEvolutionMethod | null;
}

export interface PokemonEvolutionLine {
  previous_chain: PokemonEvolutionLink[];
  current: PokemonEvolutionStage;
  next_branches: PokemonEvolutionLink[][];
}

export interface Move {
  name: string;
  display_name: string | null;
  type: string | null;
  category: string | null;
  power: number | null;
  pp: number | null;
  accuracy: number | null;
}

export interface MoveLearnMethod {
  method: string;
  level: number | null;
}

export interface PokemonMove extends Move {
  description: string | null;
  methods: MoveLearnMethod[];
}

export interface MoveLearner {
  pokemon_id: number;
  pokemon_name: string;
  pokemon_sprite: string | null;
  methods: MoveLearnMethod[];
}

export interface MoveTmPurchaseOption {
  location: string;
  price_pokeyen: number | null;
  price_text: string | null;
}

export interface MoveTmPurchase extends MoveTmPurchaseOption {
  secondary: MoveTmPurchaseOption | null;
}

export interface MoveDetail {
  name: string;
  display_name: string | null;
  description: string | null;
  tm_purchase: MoveTmPurchase | null;
  learners: MoveLearner[];
}

export interface Location {
  name: string;
  display_name: string | null;
  pokemon_ids: number[];
}

export interface LocationEncounter {
  pokemon_name: string;
  pokemon_id: number | null;
  sub_location?: string | null;
  level_range: string;
  method: string;
  rate: string;
  period: string | null;
  category: string;
}

export interface LocationBirdviewImage {
  label: string | null;
  image_url: string;
  source_url: string | null;
}

export interface LocationDetail {
  name: string;
  display_name: string;
  birdview_image_url: string | null;
  birdview_source_url: string | null;
  birdview_images: LocationBirdviewImage[];
  map_image_url: string | null;
  map_source_url: string | null;
  source_url: string | null;
  encounters: LocationEncounter[];
}
