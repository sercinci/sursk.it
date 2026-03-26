interface TypeMatchup {
  double: string[];
  half: string[];
  zero?: string[];
}

export interface DamageModifierEntry {
  type: string;
  multiplier: number;
}

export interface DamageModifierGroup {
  multiplier: number;
  entries: DamageModifierEntry[];
}

export interface DefensiveDamageModifiers {
  weaknesses: DamageModifierEntry[];
  strengths: DamageModifierEntry[];
  immunities: DamageModifierEntry[];
}

const TYPE_CHART: Record<string, TypeMatchup> = {
  normal: { double: [], half: ["rock", "steel"], zero: ["ghost"] },
  fire: { double: ["grass", "ice", "bug", "steel"], half: ["fire", "water", "rock", "dragon"] },
  water: { double: ["fire", "ground", "rock"], half: ["water", "grass", "dragon"] },
  electric: { double: ["water", "flying"], half: ["electric", "grass", "dragon"], zero: ["ground"] },
  grass: {
    double: ["water", "ground", "rock"],
    half: ["fire", "grass", "poison", "flying", "bug", "dragon", "steel"]
  },
  ice: { double: ["grass", "ground", "flying", "dragon"], half: ["fire", "water", "ice", "steel"] },
  fighting: {
    double: ["normal", "ice", "rock", "dark", "steel"],
    half: ["poison", "flying", "psychic", "bug"],
    zero: ["ghost"]
  },
  poison: { double: ["grass"], half: ["poison", "ground", "rock", "ghost"], zero: ["steel"] },
  ground: { double: ["fire", "electric", "poison", "rock", "steel"], half: ["grass", "bug"], zero: ["flying"] },
  flying: { double: ["grass", "fighting", "bug"], half: ["electric", "rock", "steel"] },
  psychic: { double: ["fighting", "poison"], half: ["psychic", "steel"], zero: ["dark"] },
  bug: {
    double: ["grass", "psychic", "dark"],
    half: ["fire", "fighting", "poison", "flying", "ghost", "steel"]
  },
  rock: { double: ["fire", "ice", "flying", "bug"], half: ["fighting", "ground", "steel"] },
  ghost: { double: ["psychic", "ghost"], half: ["dark", "steel"], zero: ["normal"] },
  dragon: { double: ["dragon"], half: ["steel"] },
  dark: { double: ["psychic", "ghost"], half: ["fighting", "dark", "steel"] },
  steel: { double: ["ice", "rock"], half: ["fire", "water", "electric", "steel"] }
};

const ATTACK_TYPES = Object.keys(TYPE_CHART);
const TYPE_DISPLAY_ORDER = [
  "normal",
  "fighting",
  "flying",
  "poison",
  "ground",
  "rock",
  "bug",
  "ghost",
  "steel",
  "fire",
  "water",
  "grass",
  "electric",
  "psychic",
  "ice",
  "dragon",
  "dark"
];

function sortTypesByDisplayOrder(a: string, b: string) {
  const aIndex = TYPE_DISPLAY_ORDER.indexOf(a);
  const bIndex = TYPE_DISPLAY_ORDER.indexOf(b);
  if (aIndex === -1 || bIndex === -1) {
    return a.localeCompare(b);
  }
  return aIndex - bIndex;
}

function getAttackMultiplier(attackType: string, defendType: string): number {
  const matchup = TYPE_CHART[attackType];
  if (!matchup) {
    return 1;
  }
  if (matchup.zero?.includes(defendType)) {
    return 0;
  }
  if (matchup.double.includes(defendType)) {
    return 2;
  }
  if (matchup.half.includes(defendType)) {
    return 0.5;
  }
  return 1;
}

export function getDefensiveDamageModifiers(types: string[]): DefensiveDamageModifiers {
  const normalizedTypes = types.map((type) => type.toLowerCase());
  const weaknesses: DamageModifierEntry[] = [];
  const strengths: DamageModifierEntry[] = [];
  const immunities: DamageModifierEntry[] = [];

  for (const attackType of ATTACK_TYPES) {
    const multiplier = normalizedTypes.reduce(
      (acc, defendType) => acc * getAttackMultiplier(attackType, defendType),
      1
    );

    if (multiplier === 0) {
      immunities.push({ type: attackType, multiplier });
      continue;
    }
    if (multiplier > 1) {
      weaknesses.push({ type: attackType, multiplier });
      continue;
    }
    if (multiplier < 1) {
      strengths.push({ type: attackType, multiplier });
    }
  }

  weaknesses.sort((a, b) => b.multiplier - a.multiplier || a.type.localeCompare(b.type));
  strengths.sort((a, b) => a.multiplier - b.multiplier || a.type.localeCompare(b.type));
  immunities.sort((a, b) => a.type.localeCompare(b.type));

  return { weaknesses, strengths, immunities };
}

export function getOffensiveDamageGroups(types: string[]): DamageModifierGroup[] {
  const attackerTypes = types
    .map((type) => type.toLowerCase())
    .filter((type, index, all) => type in TYPE_CHART && all.indexOf(type) === index);

  const grouped = new Map<number, DamageModifierEntry[]>();

  for (const defendType of ATTACK_TYPES) {
    const multiplier =
      attackerTypes.length > 0
        ? Math.max(...attackerTypes.map((attackType) => getAttackMultiplier(attackType, defendType)))
        : 1;

    const current = grouped.get(multiplier) ?? [];
    current.push({ type: defendType, multiplier });
    grouped.set(multiplier, current);
  }

  return [...grouped.entries()]
    .sort((a, b) => b[0] - a[0])
    .map(([multiplier, entries]) => ({
      multiplier,
      entries: [...entries].sort((a, b) => sortTypesByDisplayOrder(a.type, b.type))
    }));
}

export function getDefensiveDamageGroups(types: string[]): DamageModifierGroup[] {
  const defenderTypes = types
    .map((type) => type.toLowerCase())
    .filter((type, index, all) => type in TYPE_CHART && all.indexOf(type) === index);

  const grouped = new Map<number, DamageModifierEntry[]>();

  for (const attackType of ATTACK_TYPES) {
    const multiplier =
      defenderTypes.length > 0
        ? defenderTypes.reduce(
            (acc, defendType) => acc * getAttackMultiplier(attackType, defendType),
            1
          )
        : 1;

    const current = grouped.get(multiplier) ?? [];
    current.push({ type: attackType, multiplier });
    grouped.set(multiplier, current);
  }

  return [...grouped.entries()]
    .sort((a, b) => b[0] - a[0])
    .map(([multiplier, entries]) => ({
      multiplier,
      entries: [...entries].sort((a, b) => sortTypesByDisplayOrder(a.type, b.type))
    }));
}
