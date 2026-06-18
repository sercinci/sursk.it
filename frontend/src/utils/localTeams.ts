import { DAMAGE_EV, DAMAGE_IV } from "@/utils/pokemmoDamage";

export const STORED_TEAMS_KEY = "surskit.stored-teams.v1";
export const STORED_TEAM_MAX_MEMBERS = 12;
export const STORED_TEAM_MAX_MOVES = 4;

export const STORED_TEAM_STAT_ORDER = [
  "hp",
  "attack",
  "defense",
  "special-attack",
  "special-defense",
  "speed",
] as const;

export type StoredTeamStat = (typeof STORED_TEAM_STAT_ORDER)[number];
export type StoredStatValues = Record<StoredTeamStat, number>;

export interface StoredPokemonBuild {
  id: string;
  pokemonId: number;
  ivs: StoredStatValues;
  evs: StoredStatValues;
  nature: string | null;
  ability: string | null;
  moves: string[];
}

export interface StoredTeam {
  id: string;
  name: string;
  members: StoredPokemonBuild[];
  createdAt: number;
  updatedAt: number;
}

export interface StoredMemberRef {
  teamId: string;
  memberId: string;
}

function createLocalId(prefix: string): string {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) {
    return `${prefix}-${crypto.randomUUID()}`;
  }
  return `${prefix}-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 10)}`;
}

function defaultStatValues(value: number): StoredStatValues {
  return Object.fromEntries(STORED_TEAM_STAT_ORDER.map((stat) => [stat, value])) as StoredStatValues;
}

function clampWholeNumber(value: unknown, min: number, max: number, fallback: number): number {
  const numericValue = Number(value);
  if (!Number.isFinite(numericValue)) {
    return fallback;
  }
  return Math.min(max, Math.max(min, Math.trunc(numericValue)));
}

function normalizeStatValues(raw: unknown, min: number, max: number, fallback: number): StoredStatValues {
  const source = raw && typeof raw === "object" ? raw as Record<string, unknown> : {};
  return Object.fromEntries(
    STORED_TEAM_STAT_ORDER.map((stat) => [stat, clampWholeNumber(source[stat], min, max, fallback)])
  ) as StoredStatValues;
}

function normalizeMoves(raw: unknown): string[] {
  if (!Array.isArray(raw)) {
    return ["", "", "", ""];
  }
  const seen = new Set<string>();
  const moves = raw
    .map((move) => typeof move === "string" ? move.trim() : "")
    .filter((move) => {
      if (!move || seen.has(move)) {
        return false;
      }
      seen.add(move);
      return true;
    })
    .slice(0, STORED_TEAM_MAX_MOVES);
  return [...moves, ...Array(Math.max(0, STORED_TEAM_MAX_MOVES - moves.length)).fill("")];
}

export function createStoredPokemonBuild(pokemonId: number): StoredPokemonBuild {
  return {
    id: createLocalId("member"),
    pokemonId,
    ivs: defaultStatValues(DAMAGE_IV),
    evs: defaultStatValues(DAMAGE_EV),
    nature: null,
    ability: null,
    moves: ["", "", "", ""],
  };
}

export function normalizeStoredPokemonBuild(raw: unknown): StoredPokemonBuild | null {
  if (!raw || typeof raw !== "object") {
    return null;
  }
  const source = raw as Record<string, unknown>;
  const pokemonId = clampWholeNumber(source.pokemonId, 1, Number.MAX_SAFE_INTEGER, 0);
  if (pokemonId <= 0) {
    return null;
  }
  return {
    id: typeof source.id === "string" && source.id.trim() ? source.id : createLocalId("member"),
    pokemonId,
    ivs: normalizeStatValues(source.ivs, 0, 31, DAMAGE_IV),
    evs: normalizeStatValues(source.evs, 0, 252, DAMAGE_EV),
    nature: typeof source.nature === "string" && source.nature.trim() ? source.nature.trim() : null,
    ability: typeof source.ability === "string" && source.ability.trim() ? source.ability.trim() : null,
    moves: normalizeMoves(source.moves),
  };
}

export function normalizeStoredTeam(raw: unknown): StoredTeam | null {
  if (!raw || typeof raw !== "object") {
    return null;
  }
  const source = raw as Record<string, unknown>;
  const members = Array.isArray(source.members)
    ? source.members.map(normalizeStoredPokemonBuild).filter((member): member is StoredPokemonBuild => member !== null)
    : [];
  const trimmedMembers = members.slice(0, STORED_TEAM_MAX_MEMBERS);
  if (!trimmedMembers.length) {
    return null;
  }
  const now = Date.now();
  const createdAt = clampWholeNumber(source.createdAt, 0, Number.MAX_SAFE_INTEGER, now);
  const updatedAt = clampWholeNumber(source.updatedAt, 0, Number.MAX_SAFE_INTEGER, createdAt);
  return {
    id: typeof source.id === "string" && source.id.trim() ? source.id : createLocalId("team"),
    name: typeof source.name === "string" && source.name.trim() ? source.name.trim() : "Saved team",
    members: trimmedMembers,
    createdAt,
    updatedAt,
  };
}

export function createStoredTeam(name: string, pokemonIds: number[]): StoredTeam {
  const now = Date.now();
  return {
    id: createLocalId("team"),
    name: name.trim() || "Saved team",
    members: pokemonIds.slice(0, STORED_TEAM_MAX_MEMBERS).map(createStoredPokemonBuild),
    createdAt: now,
    updatedAt: now,
  };
}

export function duplicateStoredTeam(team: StoredTeam, name: string): StoredTeam {
  const now = Date.now();
  return {
    id: createLocalId("team"),
    name: name.trim() || `${team.name} copy`,
    members: team.members.slice(0, STORED_TEAM_MAX_MEMBERS).map(member => ({
      ...member,
      id: createLocalId("member"),
      ivs: { ...member.ivs },
      evs: { ...member.evs },
      moves: [...member.moves],
    })),
    createdAt: now,
    updatedAt: now,
  };
}

export function loadStoredTeams(): StoredTeam[] {
  if (typeof localStorage === "undefined") {
    return [];
  }
  const stored = localStorage.getItem(STORED_TEAMS_KEY);
  if (!stored) {
    return [];
  }
  try {
    const parsed = JSON.parse(stored) as unknown;
    if (!Array.isArray(parsed)) {
      return [];
    }
    return parsed
      .map(normalizeStoredTeam)
      .filter((team): team is StoredTeam => team !== null)
      .sort((a, b) => b.updatedAt - a.updatedAt);
  } catch {
    return [];
  }
}

export function saveStoredTeams(teams: StoredTeam[]): void {
  if (typeof localStorage === "undefined") {
    return;
  }
  localStorage.setItem(STORED_TEAMS_KEY, JSON.stringify(teams));
}

export function touchStoredTeam(team: StoredTeam): StoredTeam {
  return { ...team, updatedAt: Date.now() };
}

export function encodeStoredMemberRef(teamId: string, memberId: string): string {
  return `${encodeURIComponent(teamId)}:${encodeURIComponent(memberId)}`;
}

export function decodeStoredMemberRef(raw: unknown): StoredMemberRef | null {
  if (typeof raw !== "string" || !raw.includes(":")) {
    return null;
  }
  const [teamId, memberId] = raw.split(":", 2).map((part) => {
    try {
      return decodeURIComponent(part);
    } catch {
      return "";
    }
  });
  if (!teamId || !memberId) {
    return null;
  }
  return { teamId, memberId };
}

export function findStoredMember(teams: StoredTeam[], ref: StoredMemberRef): StoredPokemonBuild | null {
  return teams
    .find((team) => team.id === ref.teamId)
    ?.members.find((member) => member.id === ref.memberId) ?? null;
}
