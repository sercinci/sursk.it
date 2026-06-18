import type { Pokemon, PokemonMove } from "@/types";
import { getAttackMultiplierForTypes } from "@/constants/typeEffectiveness";

export const DAMAGE_LEVEL = 50;
export const DAMAGE_IV = 31;
export const DAMAGE_EV = 0;
export const DAMAGE_STAGE = 0;

export type BattleWeather = "clear" | "sun" | "rain" | "sandstorm" | "hail";
export type PokemonStatus = "none" | "burn" | "paralysis" | "poison" | "toxic" | "sleep" | "freeze";
export type BattleAbility = string | null;

export interface EntryHazards {
  spikes: number;
  stealthRock: boolean;
}

export interface DamageSettings {
  level: number;
  iv: number;
  ev: number;
  stage?: number;
  nature?: NatureModifier | null;
  weather?: BattleWeather;
  status?: PokemonStatus;
  ability?: BattleAbility;
  weatherSuppressed?: boolean;
  applyStatusToStats?: boolean;
}

export interface NatureModifier {
  increasedStat: string | null;
  decreasedStat: string | null;
}

export interface DamageSideSettings {
  level: number;
  ivs: Record<string, number | undefined>;
  evs: Record<string, number | undefined>;
  stages: Record<string, number | undefined>;
  currentHpPercent?: number;
  nature?: NatureModifier | null;
  weather?: BattleWeather;
  status?: PokemonStatus;
  ability?: BattleAbility;
  hazards?: EntryHazards;
  weatherSuppressed?: boolean;
}

export interface DamageCalculationOptions {
  critical?: boolean;
}

export const DEFAULT_DAMAGE_SETTINGS: DamageSettings = {
  level: DAMAGE_LEVEL,
  iv: DAMAGE_IV,
  ev: DAMAGE_EV,
  stage: DAMAGE_STAGE,
  weather: "clear",
  status: "none",
  ability: null,
};

function createDefaultDamageSideSettings(): DamageSideSettings {
  return {
    level: DAMAGE_LEVEL,
    ivs: {},
    evs: {},
    stages: {},
    currentHpPercent: 100,
    weather: "clear",
    status: "none",
    ability: null,
    hazards: { spikes: 0, stealthRock: false },
  };
}

export const DEFAULT_DAMAGE_SIDE_SETTINGS: DamageSideSettings = createDefaultDamageSideSettings();

const RANDOM_ROLLS = Array.from({ length: 16 }, (_, index) => 85 + index);
const STAB_MODIFIER = 0x1800;
const MODIFIER_SCALE = 0x1000;
const MODIFIER_HALF = 0x800;

const SPECIAL_MOVES_USING_DEFENSE = new Set(["psyshock", "psystrike", "secret-sword"]);
const STAT_DAMAGING_STATUSES = new Set<PokemonStatus>(["burn", "paralysis", "poison", "toxic"]);
const POISON_STATUSES = new Set<PokemonStatus>(["poison", "toxic"]);
const WEATHER_SUPPRESSING_ABILITIES = new Set(["air-lock", "cloud-nine"]);
const MOLD_BREAKER_ABILITIES = new Set(["mold-breaker"]);
const CRITICAL_PREVENTING_ABILITIES = new Set(["battle-armor", "shell-armor"]);
const SANDSTORM_DAMAGE_IMMUNE_ABILITIES = new Set(["magic-guard", "overcoat", "sand-force", "sand-rush", "sand-veil"]);
const HAIL_DAMAGE_IMMUNE_ABILITIES = new Set(["ice-body", "magic-guard", "overcoat", "snow-cloak"]);
const ABILITY_TYPE_IMMUNITIES: Record<string, string> = {
  "dry-skin": "water",
  "flash-fire": "fire",
  "levitate": "ground",
  "lightning-rod": "electric",
  "motor-drive": "electric",
  "sap-sipper": "grass",
  "storm-drain": "water",
  "volt-absorb": "electric",
  "water-absorb": "water",
};
const STATUS_PREVENTING_ABILITIES: Partial<Record<PokemonStatus, Set<string>>> = {
  burn: new Set(["water-veil"]),
  paralysis: new Set(["limber"]),
  poison: new Set(["immunity"]),
  toxic: new Set(["immunity"]),
  sleep: new Set(["insomnia", "vital-spirit"]),
  freeze: new Set(["magma-armor"]),
};
const WIND_MOVE_NAMES = new Set(["gust", "hurricane", "twister", "icy-wind"]);
const SOUND_MOVE_NAMES = new Set([
  "bug-buzz",
  "chatter",
  "echoed-voice",
  "grass-whistle",
  "growl",
  "heal-bell",
  "hyper-voice",
  "metal-sound",
  "perish-song",
  "relic-song",
  "roar",
  "round",
  "screech",
  "sing",
  "snarl",
  "snore",
  "supersonic",
  "uproar",
]);
const WEATHER_BALL_TYPES: Partial<Record<BattleWeather, string>> = {
  sun: "fire",
  rain: "water",
  sandstorm: "rock",
  hail: "ice",
};

export interface DamageCalculation {
  level: number;
  attackerStat: number;
  defenderStat: number;
  defenderHp: number;
  defenderCurrentHp: number;
  defenderCurrentHpPercent: number;
  attackStatName: string;
  defenseStatName: string;
  effectivePower: number;
  effectiveType: string;
  weatherMultiplier: number;
  critical: boolean;
  criticalMultiplier: number;
  criticalBlockedBy: string | null;
  statusDamageMultiplier: number;
  abilityDamageModifiers: AbilityDamageModifier[];
  abilityBlockedBy: string | null;
  sturdyBlockedOhko: boolean;
  entryHazardDamage: number;
  spikesDamage: number;
  stealthRockDamage: number;
  spikesLayers: number;
  stealthRockMultiplier: number;
  spikesBlockedBy: string | null;
  stealthRockBlockedBy: string | null;
  weather: BattleWeather;
  weatherResidualDamage: number;
  weatherResidualBlockedBy: string | null;
  statusResidualDamage: number;
  abilityResidualDamage: number;
  attackerStatus: PokemonStatus;
  defenderStatus: PokemonStatus;
  attackerAbility: BattleAbility;
  defenderAbility: BattleAbility;
  stab: number;
  typeEffectiveness: number;
  rolls: number[];
  minDamage: number;
  maxDamage: number;
  minPercent: number;
  maxPercent: number;
  averageDamage: number;
  ohkoChance: number;
  twoHkoChance: number;
}

export interface AbilityDamageModifier {
  ability: string;
  side: "attacker" | "defender";
  multiplier: number;
  reason: "damage" | "type" | "immunity" | "ohko";
}

function floorDiv(numerator: number, denominator: number): number {
  return Math.floor(numerator / denominator);
}

function applyModifier(value: number, modifier: number): number {
  const scaled = value * modifier;
  const roundedDown = Math.floor(scaled / MODIFIER_SCALE);
  const remainder = scaled % MODIFIER_SCALE;
  return remainder > MODIFIER_HALF ? roundedDown + 1 : roundedDown;
}

function applyDecimalModifier(value: number, multiplier: number): number {
  return applyModifier(value, Math.round(multiplier * MODIFIER_SCALE));
}

function normalizeAbility(ability?: BattleAbility): string | null {
  return ability?.trim().toLowerCase() || null;
}

export function isWeatherSuppressedByAbility(ability?: BattleAbility): boolean {
  const normalizedAbility = normalizeAbility(ability);
  return normalizedAbility !== null && WEATHER_SUPPRESSING_ABILITIES.has(normalizedAbility);
}

export function getAbilityWeather(ability?: BattleAbility): BattleWeather | null {
  const normalizedAbility = normalizeAbility(ability);
  if (normalizedAbility === "drizzle") return "rain";
  if (normalizedAbility === "drought") return "sun";
  return null;
}

export function getEffectivePokemonStatus(status: PokemonStatus = "none", ability?: BattleAbility): PokemonStatus {
  const normalizedAbility = normalizeAbility(ability);
  if (!normalizedAbility || status === "none") {
    return status;
  }
  return STATUS_PREVENTING_ABILITIES[status]?.has(normalizedAbility) ? "none" : status;
}

function getBaseStat(pokemon: Pokemon, statName: string): number {
  return pokemon.stats?.[statName] ?? 0;
}

function hasType(pokemon: Pokemon, typeName: string): boolean {
  return pokemon.types.some((type) => type.toLowerCase() === typeName);
}

function getSideStatSettings(settings: DamageSideSettings, statName: string): DamageSettings {
  return {
    level: settings.level,
    iv: settings.ivs[statName] ?? DAMAGE_IV,
    ev: settings.evs[statName] ?? DAMAGE_EV,
    stage: settings.stages[statName] ?? DAMAGE_STAGE,
    nature: settings.nature,
    weather: settings.weather ?? "clear",
    status: settings.status ?? "none",
    ability: settings.ability ?? null,
    weatherSuppressed: settings.weatherSuppressed ?? false,
  };
}

function applyStatStage(statValue: number, stage: number, ability?: BattleAbility): number {
  const stageValue = normalizeAbility(ability) === "simple" ? stage * 2 : stage;
  const clampedStage = Math.min(6, Math.max(-6, Math.trunc(stageValue)));
  if (clampedStage >= 0) {
    return Math.floor(statValue * (2 + clampedStage) / 2);
  }
  return Math.floor(statValue * 2 / (2 - clampedStage));
}

export function calculatePokemonStat(
  pokemon: Pokemon,
  statName: string,
  settings: DamageSettings = DEFAULT_DAMAGE_SETTINGS
): number {
  const baseStat = getBaseStat(pokemon, statName);
  const { level, iv, ev } = settings;

  if (statName === "hp") {
    if (baseStat === 1) {
      return 1;
    }
    return floorDiv((2 * baseStat + iv + floorDiv(ev, 4)) * level, 100) + level + 10;
  }

  const neutralStat = floorDiv((2 * baseStat + iv + floorDiv(ev, 4)) * level, 100) + 5;
  let modifiedStat = neutralStat;
  const ability = normalizeAbility(settings.ability);
  const effectiveStatus = getEffectivePokemonStatus(settings.status ?? "none", ability);
  const weather = settings.weatherSuppressed ? "clear" : settings.weather ?? "clear";
  if (settings.nature?.increasedStat === statName) {
    modifiedStat = Math.floor(modifiedStat * 1.1);
  } else if (settings.nature?.decreasedStat === statName) {
    modifiedStat = Math.floor(modifiedStat * 0.9);
  }

  modifiedStat = applyStatStage(modifiedStat, settings.stage ?? DAMAGE_STAGE, ability);

  if (statName === "special-defense" && weather === "sandstorm" && hasType(pokemon, "rock")) {
    modifiedStat = Math.floor(modifiedStat * 1.5);
  }

  if (statName === "attack") {
    if (ability === "huge-power" || ability === "pure-power") {
      modifiedStat *= 2;
    }
    if (ability === "guts" && isStatused(effectiveStatus)) {
      modifiedStat = Math.floor(modifiedStat * 1.5);
    }
  }

  if (statName === "defense" && ability === "marvel-scale" && isStatused(effectiveStatus)) {
    modifiedStat = Math.floor(modifiedStat * 1.5);
  }

  if (statName === "special-attack" && ability === "solar-power" && weather === "sun") {
    modifiedStat = Math.floor(modifiedStat * 1.5);
  }

  if (statName === "speed") {
    if (ability === "chlorophyll" && weather === "sun") {
      modifiedStat *= 2;
    } else if (ability === "swift-swim" && weather === "rain") {
      modifiedStat *= 2;
    } else if (ability === "quick-feet" && isStatused(effectiveStatus)) {
      modifiedStat = Math.floor(modifiedStat * 1.5);
    }
  }

  if (settings.applyStatusToStats ?? true) {
    if (statName === "attack" && effectiveStatus === "burn" && ability !== "guts") {
      modifiedStat = Math.floor(modifiedStat * 0.5);
    } else if (statName === "speed" && effectiveStatus === "paralysis") {
      modifiedStat = Math.floor(modifiedStat * 0.5);
    }
  }

  return modifiedStat;
}

function applyTypeEffectiveness(damage: number, typeEffectiveness: number): number {
  if (typeEffectiveness === 0) return 0;
  if (typeEffectiveness === 0.25) return floorDiv(damage, 4);
  if (typeEffectiveness === 0.5) return floorDiv(damage, 2);
  if (typeEffectiveness === 2) return damage * 2;
  if (typeEffectiveness === 4) return damage * 4;
  return Math.floor(damage * typeEffectiveness);
}

function getMoveStatNames(move: PokemonMove): {
  attackStatName: string;
  defenseStatName: string;
} | null {
  const category = move.category?.toLowerCase();
  const moveName = move.name.toLowerCase();

  if (moveName === "body-press") {
    return { attackStatName: "defense", defenseStatName: "defense" };
  }
  if (moveName === "foul-play") {
    return { attackStatName: "target-attack", defenseStatName: "defense" };
  }
  if (category === "physical") {
    return { attackStatName: "attack", defenseStatName: "defense" };
  }
  if (category === "special") {
    return {
      attackStatName: "special-attack",
      defenseStatName: SPECIAL_MOVES_USING_DEFENSE.has(moveName) ? "defense" : "special-defense",
    };
  }

  return null;
}

function getAttackerStat(
  attacker: Pokemon,
  defender: Pokemon,
  statName: string,
  attackerSettings: DamageSideSettings,
  defenderSettings: DamageSideSettings,
  critical: boolean
): number {
  const usesTargetStat = statName === "target-attack";
  const source = usesTargetStat ? defender : attacker;
  const sourceSettings = usesTargetStat ? defenderSettings : attackerSettings;
  const normalizedStatName = statName === "target-attack" ? "attack" : statName;
  const statSettings = getSideStatSettings(sourceSettings, normalizedStatName);
  if (critical && (statSettings.stage ?? DAMAGE_STAGE) < 0) {
    statSettings.stage = DAMAGE_STAGE;
  }
  return calculatePokemonStat(source, normalizedStatName, {
    ...statSettings,
    applyStatusToStats: false,
  });
}

function isStatused(status: PokemonStatus): boolean {
  return status !== "none";
}

function getEffectivePower(
  move: PokemonMove,
  weather: BattleWeather,
  attackerStatus: PokemonStatus = "none",
  defenderStatus: PokemonStatus = "none",
  attackerAbility?: BattleAbility,
  defenderAbility?: BattleAbility
): number | null {
  if (move.power === null) {
    return null;
  }

  const moveName = move.name.toLowerCase();
  let power = move.power;
  const effectiveAttackerStatus = getEffectivePokemonStatus(attackerStatus, attackerAbility);
  const effectiveDefenderStatus = getEffectivePokemonStatus(defenderStatus, defenderAbility);

  if (moveName === "dream-eater" && effectiveDefenderStatus !== "sleep") {
    return null;
  }

  if (moveName === "snore" && effectiveAttackerStatus !== "sleep") {
    return null;
  }

  if (moveName === "weather-ball" && weather !== "clear") {
    return 100;
  }

  if (moveName === "acrobatics") {
    power *= 2;
  }

  if (moveName === "facade" && STAT_DAMAGING_STATUSES.has(effectiveAttackerStatus)) {
    power *= 2;
  }

  if (moveName === "hex" && isStatused(effectiveDefenderStatus)) {
    power *= 2;
  }

  if (moveName === "venoshock" && POISON_STATUSES.has(effectiveDefenderStatus)) {
    power *= 2;
  }

  if ((moveName === "wake-up-slap" || moveName === "wakeup-slap") && effectiveDefenderStatus === "sleep") {
    power *= 2;
  }

  if ((moveName === "smelling-salts" || moveName === "smellingsalt") && effectiveDefenderStatus === "paralysis") {
    power *= 2;
  }

  return power;
}

function getEffectiveType(move: PokemonMove, weather: BattleWeather, attackerAbility?: BattleAbility): string | null {
  if (normalizeAbility(attackerAbility) === "normalize") {
    return "normal";
  }
  if (move.name.toLowerCase() === "weather-ball" && weather !== "clear") {
    return WEATHER_BALL_TYPES[weather] ?? move.type;
  }
  return move.type;
}

function getWeatherDamageMultiplier(move: PokemonMove, effectiveType: string, weather: BattleWeather): number {
  const moveName = move.name.toLowerCase();

  if (moveName === "solar-beam" || moveName === "solarbeam") {
    return weather !== "clear" && weather !== "sun" ? 0.5 : 1;
  }

  if (weather === "rain") {
    if (effectiveType === "water") return 1.5;
    if (effectiveType === "fire") return 0.5;
  }

  if (weather === "sun") {
    if (effectiveType === "fire") return 1.5;
    if (effectiveType === "water") return 0.5;
  }

  return 1;
}

export function getMoveDamageProfile(
  move: PokemonMove,
  weather: BattleWeather = "clear",
  attackerStatus: PokemonStatus = "none",
  defenderStatus: PokemonStatus = "none",
  attackerAbility?: BattleAbility,
  defenderAbility?: BattleAbility,
  weatherSuppressed = false
): { type: string | null; power: number | null; weatherMultiplier: number } {
  const effectiveWeather = weatherSuppressed ? "clear" : weather;
  const effectiveType = getEffectiveType(move, effectiveWeather, attackerAbility);
  const effectivePower = getEffectivePower(
    move,
    effectiveWeather,
    attackerStatus,
    defenderStatus,
    attackerAbility,
    defenderAbility
  );
  return {
    type: effectiveType,
    power: effectivePower,
    weatherMultiplier: effectiveType ? getWeatherDamageMultiplier(move, effectiveType, effectiveWeather) : 1,
  };
}

function calculateBaseDamage(power: number, attack: number, defense: number, level: number): number {
  const levelFactor = floorDiv(2 * level, 5) + 2;
  return floorDiv(floorDiv(levelFactor * power * attack, defense), 50) + 2;
}

function attackerBypassesDefenderAbility(attackerAbility?: BattleAbility): boolean {
  const normalizedAbility = normalizeAbility(attackerAbility);
  return normalizedAbility !== null && MOLD_BREAKER_ABILITIES.has(normalizedAbility);
}

function getCriticalBlockedBy(attackerAbility?: BattleAbility, defenderAbility?: BattleAbility): string | null {
  const normalizedDefenderAbility = normalizeAbility(defenderAbility);
  if (!normalizedDefenderAbility || attackerBypassesDefenderAbility(attackerAbility)) {
    return null;
  }
  return CRITICAL_PREVENTING_ABILITIES.has(normalizedDefenderAbility) ? normalizedDefenderAbility : null;
}

function getCriticalMultiplier(critical: boolean, attackerAbility?: BattleAbility): number {
  if (!critical) {
    return 1;
  }
  return normalizeAbility(attackerAbility) === "sniper" ? 2.25 : 1.5;
}

function abilityBlocksMove(
  move: PokemonMove,
  effectiveType: string,
  typeEffectiveness: number,
  attackerAbility?: BattleAbility,
  defenderAbility?: BattleAbility
): string | null {
  const normalizedDefenderAbility = normalizeAbility(defenderAbility);
  if (!normalizedDefenderAbility || attackerBypassesDefenderAbility(attackerAbility)) {
    return null;
  }

  const moveName = move.name.toLowerCase();
  const immuneType = ABILITY_TYPE_IMMUNITIES[normalizedDefenderAbility];
  if (immuneType === effectiveType.toLowerCase()) {
    return normalizedDefenderAbility;
  }
  if (normalizedDefenderAbility === "wind-rider" && WIND_MOVE_NAMES.has(moveName)) {
    return normalizedDefenderAbility;
  }
  if (normalizedDefenderAbility === "soundproof" && SOUND_MOVE_NAMES.has(moveName)) {
    return normalizedDefenderAbility;
  }
  if (normalizedDefenderAbility === "wonder-guard" && typeEffectiveness <= 1) {
    return normalizedDefenderAbility;
  }
  return null;
}

export function getAbilityAdjustedTypeEffectiveness(
  move: PokemonMove,
  effectiveType: string,
  baseTypeEffectiveness: number,
  attackerAbility?: BattleAbility,
  defenderAbility?: BattleAbility
): number {
  const normalizedAttackerAbility = normalizeAbility(attackerAbility);
  let typeEffectiveness = baseTypeEffectiveness;

  if (
    normalizedAttackerAbility === "scrappy" &&
    typeEffectiveness === 0 &&
    (effectiveType === "normal" || effectiveType === "fighting")
  ) {
    typeEffectiveness = 1;
  }

  return abilityBlocksMove(move, effectiveType, typeEffectiveness, attackerAbility, defenderAbility)
    ? 0
    : typeEffectiveness;
}

function getAbilityDamageModifiers(
  move: PokemonMove,
  effectiveType: string,
  typeEffectiveness: number,
  weather: BattleWeather,
  attackerAbility?: BattleAbility,
  defenderAbility?: BattleAbility
): AbilityDamageModifier[] {
  const normalizedAttackerAbility = normalizeAbility(attackerAbility);
  const normalizedDefenderAbility = normalizeAbility(defenderAbility);
  const normalizedEffectiveType = effectiveType.toLowerCase();
  const modifiers: AbilityDamageModifier[] = [];
  if (normalizedAttackerAbility === "hustle" && move.category?.toLowerCase() === "physical") {
    modifiers.push({ ability: normalizedAttackerAbility, side: "attacker", multiplier: 1.5, reason: "damage" });
  }
  if (normalizedAttackerAbility === "tinted-lens" && typeEffectiveness > 0 && typeEffectiveness < 1) {
    modifiers.push({ ability: normalizedAttackerAbility, side: "attacker", multiplier: 2, reason: "damage" });
  }
  if (
    normalizedAttackerAbility === "sand-force" &&
    weather === "sandstorm" &&
    ["ground", "rock", "steel"].includes(normalizedEffectiveType)
  ) {
    modifiers.push({ ability: normalizedAttackerAbility, side: "attacker", multiplier: 1.3, reason: "damage" });
  }

  if (!attackerBypassesDefenderAbility(attackerAbility) && normalizedDefenderAbility) {
    if (normalizedDefenderAbility === "thick-fat" && (normalizedEffectiveType === "fire" || normalizedEffectiveType === "ice")) {
      modifiers.push({ ability: normalizedDefenderAbility, side: "defender", multiplier: 0.5, reason: "damage" });
    }
    if (normalizedDefenderAbility === "dry-skin" && normalizedEffectiveType === "fire") {
      modifiers.push({ ability: normalizedDefenderAbility, side: "defender", multiplier: 1.25, reason: "damage" });
    }
    if (normalizedDefenderAbility === "solid-rock" && typeEffectiveness > 1) {
      modifiers.push({ ability: normalizedDefenderAbility, side: "defender", multiplier: 0.75, reason: "damage" });
    }
  }

  return modifiers;
}

function calculateRollDamage(
  baseDamage: number,
  roll: number,
  hasStab: boolean,
  typeEffectiveness: number,
  weatherMultiplier: number,
  criticalMultiplier: number,
  statusDamageMultiplier: number,
  abilityDamageModifiers: AbilityDamageModifier[]
): number {
  if (typeEffectiveness === 0) {
    return 0;
  }

  let damage = baseDamage;
  if (weatherMultiplier === 1.5) {
    damage = applyModifier(damage, STAB_MODIFIER);
  } else if (weatherMultiplier === 0.5) {
    damage = applyModifier(damage, MODIFIER_HALF);
  }
  if (criticalMultiplier !== 1) {
    damage = applyDecimalModifier(damage, criticalMultiplier);
  }
  damage = floorDiv(damage * roll, 100);
  if (hasStab) {
    damage = applyModifier(damage, STAB_MODIFIER);
  }
  damage = applyTypeEffectiveness(damage, typeEffectiveness);
  if (statusDamageMultiplier === 0.5) {
    damage = applyModifier(damage, MODIFIER_HALF);
  }
  for (const modifier of abilityDamageModifiers) {
    damage = applyDecimalModifier(damage, modifier.multiplier);
  }
  return Math.max(1, damage);
}

function getWeatherResidualDamage(pokemon: Pokemon, hp: number, weather: BattleWeather, ability?: BattleAbility): number {
  if (weather === "sandstorm" && !["rock", "ground", "steel"].some((typeName) => hasType(pokemon, typeName))) {
    if (getWeatherResidualBlocker(pokemon, weather, ability)) return 0;
    return Math.max(1, floorDiv(hp, 16));
  }
  if (weather === "hail" && !hasType(pokemon, "ice")) {
    if (getWeatherResidualBlocker(pokemon, weather, ability)) return 0;
    return Math.max(1, floorDiv(hp, 16));
  }
  return 0;
}

function getWeatherResidualBlocker(pokemon: Pokemon, weather: BattleWeather, ability?: BattleAbility): string | null {
  const normalizedAbility = normalizeAbility(ability);
  if (!normalizedAbility) {
    return null;
  }
  if (
    weather === "sandstorm" &&
    !["rock", "ground", "steel"].some((typeName) => hasType(pokemon, typeName)) &&
    SANDSTORM_DAMAGE_IMMUNE_ABILITIES.has(normalizedAbility)
  ) {
    return normalizedAbility;
  }
  if (
    weather === "hail" &&
    !hasType(pokemon, "ice") &&
    HAIL_DAMAGE_IMMUNE_ABILITIES.has(normalizedAbility)
  ) {
    return normalizedAbility;
  }
  return null;
}

function getStatusDamageMultiplier(move: PokemonMove, attackerStatus: PokemonStatus, attackerAbility?: BattleAbility): number {
  const moveName = move.name.toLowerCase();
  const normalizedAbility = normalizeAbility(attackerAbility);
  if (attackerStatus === "burn" && move.category?.toLowerCase() === "physical" && moveName !== "facade" && normalizedAbility !== "guts") {
    return 0.5;
  }
  return 1;
}

function getStatusResidualDamage(hp: number, status: PokemonStatus, ability?: BattleAbility): number {
  const normalizedAbility = normalizeAbility(ability);
  if (normalizedAbility === "magic-guard") {
    return 0;
  }
  if (normalizedAbility === "poison-heal" && POISON_STATUSES.has(status)) {
    return -Math.max(1, floorDiv(hp, 8));
  }
  if (status === "burn") {
    return Math.max(1, floorDiv(hp, 16));
  }
  if (status === "poison") {
    return Math.max(1, floorDiv(hp, 8));
  }
  if (status === "toxic") {
    return Math.max(1, floorDiv(hp, 16));
  }
  return 0;
}

function getAbilityResidualDamage(hp: number, weather: BattleWeather, ability?: BattleAbility): number {
  const normalizedAbility = normalizeAbility(ability);
  if (weather === "rain" && normalizedAbility === "rain-dish") {
    return -Math.max(1, floorDiv(hp, 16));
  }
  if (weather === "rain" && normalizedAbility === "dry-skin") {
    return -Math.max(1, floorDiv(hp, 8));
  }
  if (weather === "hail" && normalizedAbility === "ice-body") {
    return -Math.max(1, floorDiv(hp, 16));
  }
  if (weather === "sun" && normalizedAbility === "dry-skin") {
    return Math.max(1, floorDiv(hp, 8));
  }
  if (weather === "sun" && normalizedAbility === "solar-power") {
    return Math.max(1, floorDiv(hp, 8));
  }
  return 0;
}

function normalizeHazards(hazards?: EntryHazards): EntryHazards {
  return {
    spikes: Math.min(3, Math.max(0, Math.trunc(Number(hazards?.spikes) || 0))),
    stealthRock: Boolean(hazards?.stealthRock),
  };
}

function getSpikesBlocker(pokemon: Pokemon, layers: number, ability?: BattleAbility): string | null {
  if (layers <= 0) {
    return null;
  }
  const normalizedAbility = normalizeAbility(ability);
  if (normalizedAbility === "magic-guard") {
    return normalizedAbility;
  }
  if (hasType(pokemon, "flying")) {
    return "flying";
  }
  if (normalizedAbility === "levitate") {
    return normalizedAbility;
  }
  return null;
}

function getStealthRockBlocker(stealthRock: boolean, ability?: BattleAbility): string | null {
  if (!stealthRock) {
    return null;
  }
  return normalizeAbility(ability) === "magic-guard" ? "magic-guard" : null;
}

function getSpikesDamage(pokemon: Pokemon, hp: number, layers: number, ability?: BattleAbility): number {
  if (layers <= 0 || getSpikesBlocker(pokemon, layers, ability)) {
    return 0;
  }
  if (layers === 1) {
    return Math.max(1, floorDiv(hp, 8));
  }
  if (layers === 2) {
    return Math.max(1, floorDiv(hp, 6));
  }
  return Math.max(1, floorDiv(hp, 4));
}

function getStealthRockDamage(pokemon: Pokemon, hp: number, stealthRock: boolean, ability?: BattleAbility): number {
  if (!stealthRock || getStealthRockBlocker(stealthRock, ability)) {
    return 0;
  }
  const rockMultiplier = getAttackMultiplierForTypes("rock", pokemon.types);
  if (rockMultiplier <= 0) {
    return 0;
  }
  return Math.max(1, Math.floor((hp * rockMultiplier) / 8));
}

function getDamageAfterResidual(currentDamage: number, defenderHp: number, residualDamage: number): number {
  if (currentDamage >= defenderHp) {
    return defenderHp;
  }
  return Math.min(defenderHp, Math.max(0, currentDamage + residualDamage));
}

function getCurrentHpFromPercent(maxHp: number, currentHpPercent?: number): { hp: number; percent: number } {
  const numericPercent = Number(currentHpPercent);
  const percent = Number.isFinite(numericPercent)
    ? Math.min(100, Math.max(1, numericPercent))
    : 100;
  return {
    hp: Math.max(1, Math.floor((maxHp * percent) / 100)),
    percent,
  };
}

export function calculateMoveDamage(
  attacker: Pokemon,
  defender: Pokemon,
  move: PokemonMove,
  typeEffectiveness: number,
  attackerSettings: DamageSideSettings = createDefaultDamageSideSettings(),
  defenderSettings: DamageSideSettings = createDefaultDamageSideSettings(),
  options: DamageCalculationOptions = {}
): DamageCalculation | null {
  const weather = attackerSettings.weather ?? "clear";
  const weatherSuppressed = attackerSettings.weatherSuppressed || defenderSettings.weatherSuppressed || false;
  const effectiveWeather = weatherSuppressed ? "clear" : weather;
  const attackerAbility = attackerSettings.ability ?? null;
  const defenderAbility = defenderSettings.ability ?? null;
  const criticalBlockedBy = options.critical
    ? getCriticalBlockedBy(attackerAbility, defenderAbility)
    : null;
  const critical = Boolean(options.critical && !criticalBlockedBy);
  const criticalMultiplier = getCriticalMultiplier(critical, attackerAbility);
  const attackerStatus = getEffectivePokemonStatus(attackerSettings.status ?? "none", attackerAbility);
  const defenderStatus = getEffectivePokemonStatus(defenderSettings.status ?? "none", defenderAbility);
  const moveProfile = getMoveDamageProfile(
    move,
    weather,
    attackerStatus,
    defenderStatus,
    attackerAbility,
    defenderAbility,
    weatherSuppressed
  );
  const effectivePower = moveProfile.power;
  const effectiveType = moveProfile.type;
  if (effectivePower === null || effectiveType === null) {
    return null;
  }

  const statNames = getMoveStatNames(move);
  if (!statNames) {
    return null;
  }

  const attackerStat = getAttackerStat(
    attacker,
    defender,
    statNames.attackStatName,
    attackerSettings,
    defenderSettings,
    critical
  );
  const defenderStatSettings = getSideStatSettings(defenderSettings, statNames.defenseStatName);
  if (critical && (defenderStatSettings.stage ?? DAMAGE_STAGE) > 0) {
    defenderStatSettings.stage = DAMAGE_STAGE;
  }
  const defenderStat = calculatePokemonStat(
    defender,
    statNames.defenseStatName,
    {
      ...defenderStatSettings,
      applyStatusToStats: false,
    }
  );
  const defenderHp = calculatePokemonStat(defender, "hp", getSideStatSettings(defenderSettings, "hp"));
  if (attackerStat <= 0 || defenderStat <= 0 || defenderHp <= 0) {
    return null;
  }
  const defenderCurrentHpState = getCurrentHpFromPercent(defenderHp, defenderSettings.currentHpPercent);
  const defenderCurrentHp = defenderCurrentHpState.hp;
  const defenderCurrentHpPercent = defenderCurrentHpState.percent;

  const hasStab = attacker.types.some((type) => type.toLowerCase() === effectiveType.toLowerCase());
  const adjustedTypeEffectiveness = getAbilityAdjustedTypeEffectiveness(
    move,
    effectiveType,
    typeEffectiveness,
    attackerAbility,
    defenderAbility
  );
  const baseDamage = calculateBaseDamage(effectivePower, attackerStat, defenderStat, attackerSettings.level);
  const statusDamageMultiplier = getStatusDamageMultiplier(move, attackerStatus, attackerAbility);
  const abilityDamageModifiers = getAbilityDamageModifiers(
    move,
    effectiveType,
    adjustedTypeEffectiveness,
    effectiveWeather,
    attackerAbility,
    defenderAbility
  );
  const abilityBlockedBy = abilityBlocksMove(
    move,
    effectiveType,
    typeEffectiveness,
    attackerAbility,
    defenderAbility
  );
  const weatherResidualDamage = getWeatherResidualDamage(defender, defenderHp, effectiveWeather, defenderAbility);
  const weatherResidualBlockedBy = getWeatherResidualBlocker(defender, effectiveWeather, defenderAbility);
  const statusResidualDamage = getStatusResidualDamage(defenderHp, defenderStatus, defenderAbility);
  const abilityResidualDamage = getAbilityResidualDamage(defenderHp, effectiveWeather, defenderAbility);
  const hazards = normalizeHazards(defenderSettings.hazards);
  const spikesLayers = hazards.spikes;
  const stealthRockEnabled = hazards.stealthRock;
  const spikesDamage = getSpikesDamage(defender, defenderHp, spikesLayers, defenderAbility);
  const stealthRockDamage = getStealthRockDamage(defender, defenderHp, stealthRockEnabled, defenderAbility);
  const entryHazardDamage = Math.min(defenderCurrentHp, spikesDamage + stealthRockDamage);
  const spikesBlockedBy = getSpikesBlocker(defender, spikesLayers, defenderAbility);
  const stealthRockBlockedBy = getStealthRockBlocker(stealthRockEnabled, defenderAbility);
  const stealthRockMultiplier = stealthRockEnabled ? getAttackMultiplierForTypes("rock", defender.types) : 1;
  const rolls = RANDOM_ROLLS.map((roll) =>
    calculateRollDamage(
      baseDamage,
      roll,
      hasStab,
      adjustedTypeEffectiveness,
      moveProfile.weatherMultiplier,
      criticalMultiplier,
      statusDamageMultiplier,
      abilityDamageModifiers
    )
  );
  const minDamage = Math.min(...rolls);
  const maxDamage = Math.max(...rolls);
  const defenderHpAfterEntryHazards = Math.max(0, defenderCurrentHp - entryHazardDamage);
  const sturdyBlockedOhko = normalizeAbility(defenderAbility) === "sturdy" &&
    defenderCurrentHp === defenderHp &&
    entryHazardDamage === 0 &&
    !attackerBypassesDefenderAbility(attackerAbility) &&
    rolls.some((damage) => damage >= defenderHp);
  const ohkoRolls = defenderHpAfterEntryHazards <= 0
    ? rolls.length
    : sturdyBlockedOhko
      ? 0
      : rolls.filter((damage) => damage >= defenderHpAfterEntryHazards).length;
  let twoHkoRolls = 0;
  for (const firstRoll of rolls) {
    for (const secondRoll of rolls) {
      const firstHitDamage = sturdyBlockedOhko && firstRoll >= defenderHp ? defenderHp - 1 : firstRoll;
      const residualAfterFirstHit = weatherResidualDamage + statusResidualDamage + abilityResidualDamage;
      const firstTurnDamage = getDamageAfterResidual(entryHazardDamage + firstHitDamage, defenderCurrentHp, residualAfterFirstHit);
      if (firstTurnDamage + secondRoll >= defenderCurrentHp) {
        twoHkoRolls += 1;
      }
    }
  }

  return {
    level: attackerSettings.level,
    attackerStat,
    defenderStat,
    defenderHp,
    defenderCurrentHp,
    defenderCurrentHpPercent,
    attackStatName: statNames.attackStatName === "target-attack" ? "attack" : statNames.attackStatName,
    defenseStatName: statNames.defenseStatName,
    effectivePower,
    effectiveType,
    weatherMultiplier: moveProfile.weatherMultiplier,
    critical,
    criticalMultiplier,
    criticalBlockedBy,
    statusDamageMultiplier,
    abilityDamageModifiers,
    abilityBlockedBy,
    sturdyBlockedOhko,
    entryHazardDamage,
    spikesDamage,
    stealthRockDamage,
    spikesLayers,
    stealthRockMultiplier,
    spikesBlockedBy,
    stealthRockBlockedBy,
    weather: effectiveWeather,
    weatherResidualDamage,
    weatherResidualBlockedBy,
    statusResidualDamage,
    abilityResidualDamage,
    attackerStatus,
    defenderStatus,
    attackerAbility,
    defenderAbility,
    stab: hasStab ? 1.5 : 1,
    typeEffectiveness: adjustedTypeEffectiveness,
    rolls,
    minDamage,
    maxDamage,
    minPercent: (minDamage / defenderHp) * 100,
    maxPercent: (maxDamage / defenderHp) * 100,
    averageDamage: rolls.reduce((sum, damage) => sum + damage, 0) / rolls.length,
    ohkoChance: (ohkoRolls / rolls.length) * 100,
    twoHkoChance: (twoHkoRolls / (rolls.length * rolls.length)) * 100,
  };
}
