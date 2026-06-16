export type NatureAffectedStat = "attack" | "defense" | "special-attack" | "special-defense" | "speed";

export interface PokemonNature {
  id: string;
  names: {
    en: string;
    it: string;
  };
  increasedStat: NatureAffectedStat | null;
  decreasedStat: NatureAffectedStat | null;
}

export const POKEMON_NATURES: PokemonNature[] = [
  { id: "hardy", names: { en: "Hardy", it: "Ardita" }, increasedStat: null, decreasedStat: null },
  { id: "lonely", names: { en: "Lonely", it: "Schiva" }, increasedStat: "attack", decreasedStat: "defense" },
  { id: "brave", names: { en: "Brave", it: "Audace" }, increasedStat: "attack", decreasedStat: "speed" },
  { id: "adamant", names: { en: "Adamant", it: "Decisa" }, increasedStat: "attack", decreasedStat: "special-attack" },
  { id: "naughty", names: { en: "Naughty", it: "Birbona" }, increasedStat: "attack", decreasedStat: "special-defense" },
  { id: "bold", names: { en: "Bold", it: "Sicura" }, increasedStat: "defense", decreasedStat: "attack" },
  { id: "docile", names: { en: "Docile", it: "Docile" }, increasedStat: null, decreasedStat: null },
  { id: "relaxed", names: { en: "Relaxed", it: "Placida" }, increasedStat: "defense", decreasedStat: "speed" },
  { id: "impish", names: { en: "Impish", it: "Scaltra" }, increasedStat: "defense", decreasedStat: "special-attack" },
  { id: "lax", names: { en: "Lax", it: "Fiacca" }, increasedStat: "defense", decreasedStat: "special-defense" },
  { id: "timid", names: { en: "Timid", it: "Timida" }, increasedStat: "speed", decreasedStat: "attack" },
  { id: "hasty", names: { en: "Hasty", it: "Lesta" }, increasedStat: "speed", decreasedStat: "defense" },
  { id: "serious", names: { en: "Serious", it: "Seria" }, increasedStat: null, decreasedStat: null },
  { id: "jolly", names: { en: "Jolly", it: "Allegra" }, increasedStat: "speed", decreasedStat: "special-attack" },
  { id: "naive", names: { en: "Naive", it: "Ingenua" }, increasedStat: "speed", decreasedStat: "special-defense" },
  { id: "modest", names: { en: "Modest", it: "Modesta" }, increasedStat: "special-attack", decreasedStat: "attack" },
  { id: "mild", names: { en: "Mild", it: "Mite" }, increasedStat: "special-attack", decreasedStat: "defense" },
  { id: "quiet", names: { en: "Quiet", it: "Quieta" }, increasedStat: "special-attack", decreasedStat: "speed" },
  { id: "bashful", names: { en: "Bashful", it: "Ritrosa" }, increasedStat: null, decreasedStat: null },
  { id: "rash", names: { en: "Rash", it: "Ardente" }, increasedStat: "special-attack", decreasedStat: "special-defense" },
  { id: "calm", names: { en: "Calm", it: "Calma" }, increasedStat: "special-defense", decreasedStat: "attack" },
  { id: "gentle", names: { en: "Gentle", it: "Gentile" }, increasedStat: "special-defense", decreasedStat: "defense" },
  { id: "sassy", names: { en: "Sassy", it: "Vivace" }, increasedStat: "special-defense", decreasedStat: "speed" },
  { id: "careful", names: { en: "Careful", it: "Cauta" }, increasedStat: "special-defense", decreasedStat: "special-attack" },
  { id: "quirky", names: { en: "Quirky", it: "Furba" }, increasedStat: null, decreasedStat: null },
];

export function getNatureById(id: string | null): PokemonNature | null {
  if (!id) {
    return null;
  }
  return POKEMON_NATURES.find((nature) => nature.id === id) ?? null;
}
