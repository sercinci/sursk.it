import type {
  ApiEnvelope,
  Location,
  LocationDetail,
  Move,
  MoveDetail,
  PokemonEvolutionLink,
  PokemonEvolutionLine,
  PokemonEvolutionMethod,
  PokemonEvolutionStage,
  PokemonMove,
  Pokemon,
  PokemonListQuery,
  PokemonListItem
} from "@/types";
import { getCurrentLocale } from "@/i18n";

const API_BASE = import.meta.env.VITE_API_BASE ?? "/api";
const POKEAPI_BASE = import.meta.env.VITE_POKEAPI_BASE ?? "https://pokeapi.co/api/v2";
const POKEAPI_SPRITE_BASE =
  "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon";

interface PokeApiNamedResource {
  name: string;
  url: string;
}

interface PokeApiEvolutionDetail {
  trigger?: PokeApiNamedResource | null;
  min_level?: number | null;
  item?: PokeApiNamedResource | null;
  held_item?: PokeApiNamedResource | null;
  min_happiness?: number | null;
  min_beauty?: number | null;
  min_affection?: number | null;
  time_of_day?: string | null;
  trade_species?: PokeApiNamedResource | null;
}

interface PokeApiEvolutionChainNode {
  species: PokeApiNamedResource;
  evolves_to: PokeApiEvolutionChainNode[];
  evolution_details?: PokeApiEvolutionDetail[];
}

interface PokeApiPokemonSpecies {
  name: string;
  evolution_chain?: {
    url: string;
  };
}

interface PokeApiItem {
  sprites?: {
    default?: string | null;
  };
}

function toQuery<T extends object>(params: T) {
  const query = new URLSearchParams();
  for (const [key, value] of Object.entries(params as Record<string, unknown>)) {
    if (value === undefined || value === "" || value === null) {
      continue;
    }
    if (typeof value === "string" || typeof value === "number" || typeof value === "boolean") {
      query.set(key, String(value));
    }
  }
  const rendered = query.toString();
  return rendered ? `?${rendered}` : "";
}

async function request<T>(path: string): Promise<ApiEnvelope<T>> {
  const response = await fetch(`${API_BASE}${withLocale(path)}`);
  const payload = (await response.json()) as ApiEnvelope<T>;

  if (!response.ok || payload.error) {
    throw new Error(payload.error?.message ?? "Request failed");
  }

  return payload;
}

function withLocale(path: string): string {
  const locale = getCurrentLocale();
  if (/[?&]lang=/.test(path)) {
    return path;
  }
  const separator = path.includes("?") ? "&" : "?";
  return `${path}${separator}lang=${encodeURIComponent(locale)}`;
}

async function requestPokeApi<T>(pathOrUrl: string): Promise<T> {
  const endpoint = pathOrUrl.startsWith("http://") || pathOrUrl.startsWith("https://")
    ? pathOrUrl
    : `${POKEAPI_BASE}${pathOrUrl}`;
  const response = await fetch(endpoint);

  if (!response.ok) {
    throw new Error(`PokeAPI request failed (${response.status})`);
  }

  return (await response.json()) as T;
}

function getResourceId(resourceUrl: string, resourceName: "pokemon-species" | "item"): number | null {
  const match = resourceUrl.match(new RegExp(`/${resourceName}/(\\d+)/?$`));
  if (!match) {
    return null;
  }
  const value = Number(match[1]);
  return Number.isFinite(value) ? value : null;
}

function toEvolutionStage(node: PokeApiEvolutionChainNode): PokemonEvolutionStage {
  const id = getResourceId(node.species.url, "pokemon-species");
  return {
    id,
    name: node.species.name,
    sprite: id !== null ? `${POKEAPI_SPRITE_BASE}/${id}.png` : null
  };
}

function findEvolutionPath(
  node: PokeApiEvolutionChainNode,
  targetName: string,
  pathNodes: PokeApiEvolutionChainNode[] = [],
  pathMethods: Array<PokeApiEvolutionDetail | null> = []
): {
  nodes: PokeApiEvolutionChainNode[];
  methods: Array<PokeApiEvolutionDetail | null>;
} | null {
  const nextPathNodes = [...pathNodes, node];
  if (node.species.name === targetName) {
    return { nodes: nextPathNodes, methods: pathMethods };
  }

  for (const child of node.evolves_to) {
    const childMethod = child.evolution_details?.[0] ?? null;
    const childPath = findEvolutionPath(
      child,
      targetName,
      nextPathNodes,
      [...pathMethods, childMethod]
    );
    if (childPath) {
      return childPath;
    }
  }

  return null;
}

async function getItemSprite(
  resource: PokeApiNamedResource | null | undefined,
  cache: Map<string, string | null>
): Promise<string | null> {
  if (!resource?.url) {
    return null;
  }
  const cached = cache.get(resource.url);
  if (cached !== undefined) {
    return cached;
  }

  const itemId = getResourceId(resource.url, "item");
  const fallbackSprite = itemId !== null
    ? `https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/${itemId}.png`
    : null;

  try {
    const itemPayload = await requestPokeApi<PokeApiItem>(resource.url);
    const sprite = itemPayload.sprites?.default ?? fallbackSprite;
    cache.set(resource.url, sprite);
    return sprite;
  } catch {
    cache.set(resource.url, fallbackSprite);
    return fallbackSprite;
  }
}

async function toEvolutionMethod(
  detail: PokeApiEvolutionDetail | null,
  itemSpriteCache: Map<string, string | null>
): Promise<PokemonEvolutionMethod | null> {
  if (!detail) {
    return null;
  }

  const [itemSprite, heldItemSprite] = await Promise.all([
    getItemSprite(detail.item, itemSpriteCache),
    getItemSprite(detail.held_item, itemSpriteCache)
  ]);

  return {
    trigger: detail.trigger?.name ?? null,
    min_level: detail.min_level ?? null,
    item_name: detail.item?.name ?? null,
    item_sprite: itemSprite,
    held_item_name: detail.held_item?.name ?? null,
    held_item_sprite: heldItemSprite,
    min_happiness: detail.min_happiness ?? null,
    min_beauty: detail.min_beauty ?? null,
    min_affection: detail.min_affection ?? null,
    time_of_day: detail.time_of_day ?? null,
    trade_species_name: detail.trade_species?.name ?? null
  };
}

async function toEvolutionBranches(
  node: PokeApiEvolutionChainNode,
  itemSpriteCache: Map<string, string | null>
): Promise<PokemonEvolutionLink[][]> {
  if (!node.evolves_to.length) {
    return [];
  }

  const branches = await Promise.all(
    node.evolves_to.map(async (child) => {
      const method = await toEvolutionMethod(child.evolution_details?.[0] ?? null, itemSpriteCache);
      const currentLink: PokemonEvolutionLink = {
        pokemon: toEvolutionStage(child),
        method
      };
      const childBranches = await toEvolutionBranches(child, itemSpriteCache);
      if (!childBranches.length) {
        return [[currentLink]];
      }
      return childBranches.map((branch) => [currentLink, ...branch]);
    })
  );

  return branches.flat();
}

export function fetchPokemonList(params: PokemonListQuery) {
  return request<PokemonListItem[]>(`/pokemon${toQuery(params)}`);
}

export function fetchPokemon(id: number) {
  return request<Pokemon>(`/pokemon/${id}`);
}

export function fetchPokemonMoves(id: number) {
  return request<PokemonMove[]>(`/pokemon/${id}/moves`);
}

export function fetchMoves() {
  return request<Move[]>("/moves");
}

export function fetchMoveDetail(name: string) {
  return request<MoveDetail>(`/moves/${encodeURIComponent(name)}`);
}

export function fetchLocations() {
  return request<Location[]>("/locations");
}

export function fetchPokemmoHoennLocations() {
  return request<Location[]>("/locations/pokemmo/hoenn");
}

export function fetchPokemmoHoennLocation(locationName: string) {
  return request<LocationDetail>(`/locations/pokemmo/hoenn/${encodeURIComponent(locationName)}`);
}

export function fetchTypes() {
  return request<string[]>("/meta/types");
}

export async function fetchPokemonEvolutionLine(pokemonId: number): Promise<PokemonEvolutionLine | null> {
  const species = await requestPokeApi<PokeApiPokemonSpecies>(`/pokemon-species/${pokemonId}`);
  const chainUrl = species.evolution_chain?.url;
  if (!chainUrl) {
    return null;
  }

  const evolutionChain = await requestPokeApi<{ chain: PokeApiEvolutionChainNode }>(chainUrl);
  const path = findEvolutionPath(evolutionChain.chain, species.name);
  if (!path || !path.nodes.length) {
    return null;
  }

  const currentNode = path.nodes[path.nodes.length - 1];
  const itemSpriteCache = new Map<string, string | null>();
  const previous_chain = await Promise.all(
    path.nodes.slice(0, -1).map(async (node, index) => ({
      pokemon: toEvolutionStage(node),
      method: await toEvolutionMethod(path.methods[index] ?? null, itemSpriteCache)
    }))
  );
  const next_branches = await toEvolutionBranches(currentNode, itemSpriteCache);

  return {
    previous_chain,
    current: toEvolutionStage(currentNode),
    next_branches
  };
}
