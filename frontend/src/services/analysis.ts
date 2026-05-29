import type { Pokemon, PokemonAbility, PokemonMove } from "@/types";
import { getAttackMultiplierForTypes } from "@/constants/typeEffectiveness";
import type { AIProvider } from "@/utils/crypto";

export interface AnalysisOptions {
  levelCap: number | null;
  excludeTutor: boolean;
  excludeEgg: boolean;
}

export const DEFAULT_OPTIONS: AnalysisOptions = {
  levelCap: null,
  excludeTutor: false,
  excludeEgg: false,
};

const PROVIDER_ENDPOINTS: Record<AIProvider, string> = {
  openai:   "https://api.openai.com/v1/chat/completions",
  deepseek: "https://api.deepseek.com/v1/chat/completions",
};

const PROVIDER_NAMES: Record<AIProvider, string> = {
  openai:   "OpenAI",
  deepseek: "DeepSeek",
};

// ── Response types ────────────────────────────────────────────────────────────

export interface KeyMove {
  name: string;
  source: "level-up" | "TM" | "level-up+TM" | "tutor" | "other";
}

export interface IndividualMatchup {
  my_pokemon: string;
  opponent_pokemon: string;
  outcome: "win" | "lose" | "neutral";
  confidence: "high" | "medium" | "low";
  speed_note: string;
  reasoning: string;
  key_moves: KeyMove[];
  threats_to_watch: string[];
}

export interface KeyThreat {
  opponent_pokemon: string;
  threat_level: "high" | "medium" | "low";
  best_counter: string;
  counter_strategy: string;
}

export interface SwitchAdvice {
  opponent_pokemon: string;
  switch_to: string;
  reason: string;
}

export interface TeamRecommendation {
  selected: string[];
  selection_reason: string;
  bench: Array<{ pokemon: string; reason: string }>;
}

export interface BenchSwapSuggestion {
  remove: string;
  bring_in: string;
  reason: string;
}

export interface Bo3Adjustment {
  opponent_game1_reads: string;
  recommended_swaps?: BenchSwapSuggestion[] | null;
  bench_matchup_notes?: Array<{
    bench_pokemon: string;
    triggers: string;
    replaces: string;
  }> | null;
}

export interface MatchupAnalysis {
  team_recommendation: TeamRecommendation;
  summary: string;
  overall_advantage: "my_team" | "opponent" | "even";
  advantage_explanation: string;
  lead_recommendation: {
    pokemon: string;
    reason: string;
  };
  individual_matchups: IndividualMatchup[];
  key_threats: KeyThreat[];
  switch_advice: SwitchAdvice[];
  strategy: {
    early_game: string;
    mid_game: string;
    late_game: string;
  };
  team_strengths: string[];
  team_weaknesses: string[];
  bo3_adjustments?: Bo3Adjustment | null;
}

// ── Ability immunity tables ───────────────────────────────────────────────────

// Abilities that grant full immunity to a specific move type
const ABILITY_TYPE_IMMUNITIES: Record<string, string> = {
  "levitate":      "ground",
  "flash-fire":    "fire",
  "volt-absorb":   "electric",
  "lightning-rod": "electric",
  "motor-drive":   "electric",
  "water-absorb":  "water",
  "dry-skin":      "water",
  "sap-sipper":    "grass",
  "storm-drain":   "water",
};

// Moves with the Gen 9 "wind" flag — blocked by Wind Rider
const WIND_MOVE_NAMES = new Set(["gust", "hurricane", "twister", "icy-wind"]);

// Returns the name of the ability that would block this move, or null
function abilityThatBlocks(
  moveName: string,
  moveType: string,
  ability: PokemonAbility,
): string | null {
  const immuneType = ABILITY_TYPE_IMMUNITIES[ability.name];
  if (immuneType && immuneType === moveType.toLowerCase()) return ability.name;
  if (ability.name === "wind-rider" && WIND_MOVE_NAMES.has(moveName.toLowerCase())) return ability.name;
  return null;
}

// ── Speed pre-computation ─────────────────────────────────────────────────────

function speedLv50(base: number) {
  // Gen 3–8 stat formula (non-HP): floor((2*Base + IV + floor(EV/4)) * Level/100) + 5) * Nature
  // Assumes max investment: 31 IVs, 252 EVs, Level 50
  const neutral = Math.floor((2 * base + 31 + Math.floor(252 / 4)) * 50 / 100) + 5;
  return {
    plus_nature:    Math.floor(neutral * 1.1),
    neutral_nature: neutral,
  };
}

// ── Serialization with pre-computed coverage ──────────────────────────────────

function learnSource(m: PokemonMove): KeyMove["source"] {
  const methods = m.methods.map(x => x.method);
  const isLevelUp = methods.some(x => x === "level-up");
  const isTM      = methods.some(x => x === "machine");
  const isTutor   = methods.some(x => x === "tutor");
  if (isLevelUp && (isTM || isTutor)) return "level-up+TM";
  if (isTutor)    return "tutor";
  if (isTM)       return "TM";
  if (isLevelUp)  return "level-up";
  return "other";
}

function isMethodValid(method: string, level: number | null, opts: AnalysisOptions): boolean {
  if (method === "level-up") return opts.levelCap === null || (level !== null && level <= opts.levelCap);
  if (method === "tutor")    return !opts.excludeTutor;
  if (method === "egg")      return !opts.excludeEgg;
  return true;
}

function isMoveAvailable(m: PokemonMove, opts: AnalysisOptions): boolean {
  return m.methods.some(lm => isMethodValid(lm.method, lm.level, opts));
}

function learnSourceFiltered(m: PokemonMove, opts: AnalysisOptions): KeyMove["source"] {
  const names = m.methods
    .filter(lm => isMethodValid(lm.method, lm.level, opts))
    .map(lm => lm.method);
  const isLevelUp = names.includes("level-up");
  const isTM      = names.includes("machine");
  const isTutor   = names.includes("tutor");
  if (isLevelUp && (isTM || isTutor)) return "level-up+TM";
  if (isTutor)    return "tutor";
  if (isTM)       return "TM";
  if (isLevelUp)  return "level-up";
  return "other";
}

function serializePokemon(
  p: Pokemon,
  moves: PokemonMove[],
  opponents: Pokemon[],
  opts: AnalysisOptions,
) {
  const availableMoves = moves.filter(m => isMoveAvailable(m, opts));
  const offensive = availableMoves.filter(
    m => m.type && m.category !== "status" && m.power && m.power > 0,
  );

  const coverage = opponents.map(opp => {
    const results = offensive.map(m => {
      const internalName   = m.name.toLowerCase();
      const moveType       = m.type!.toLowerCase();
      const typeMultiplier = getAttackMultiplierForTypes(m.type!, opp.types);
      const typeImmune     = typeMultiplier === 0;

      // Which of the opponent's abilities (if any) would block this move?
      const blockingAbilities = opp.abilities
        .map(a => abilityThatBlocks(internalName, moveType, a))
        .filter((x): x is string => x !== null);

      // Immunity is DEFINITE only if the type chart blocks it, OR every possible
      // ability the opponent can have would block it.
      const allAbilitiesBlock  = blockingAbilities.length > 0 &&
                                  blockingAbilities.length === opp.abilities.length;
      // Some (but not all) abilities block it → conditional on which ability is active
      const someAbilitiesBlock = blockingAbilities.length > 0 && !allAbilitiesBlock;

      return {
        name:              m.display_name ?? m.name,
        type:              m.type!,
        power:             m.power!,
        category:          m.category!,
        multiplier:        typeMultiplier,
        learn_source:      learnSourceFiltered(m, opts),
        typeImmune,
        allAbilitiesBlock,
        someAbilitiesBlock,
        blockingAbilities,
      };
    });

    // Definitely safe SE moves: SE by type chart, not type-immune, no ability blocks it
    // (includes moves where only SOME abilities block — those get a warning flag instead)
    const superEffective = results
      .filter(m => !m.typeImmune && !m.allAbilitiesBlock && m.multiplier >= 2)
      .sort((a, b) => b.multiplier - a.multiplier || b.power - a.power)
      .slice(0, 20)
      .map(m => ({
        name:         m.name,
        type:         m.type,
        power:        m.power,
        category:     m.category,
        multiplier:   m.multiplier,
        learn_source: m.learn_source,
        // Warn when this move is SE if opponent has one ability but blocked if they have another
        conditional_note: m.someAbilitiesBlock
          ? `blocked if opponent has ${m.blockingAbilities.join(" or ")}, SE otherwise`
          : undefined,
      }));

    // Definite immunities: blocked regardless of which ability the opponent has
    const immune_definite = results
      .filter(m => m.typeImmune || m.allAbilitiesBlock)
      .map(m => ({
        name:       m.name,
        type:       m.type,
        blocked_by: m.typeImmune ? "type-chart" : m.blockingAbilities.join("+"),
      }));

    // Per-ability immunity notes (to inform the AI of each ability's specific effect)
    const abilityImmunityNotes: { ability: string; certain: boolean; blocks: string }[] = [];
    const abilityChecks: [string, string][] = [
      ["levitate",      "all ground-type moves"],
      ["flash-fire",    "all fire-type moves"],
      ["volt-absorb",   "all electric-type moves"],
      ["lightning-rod", "all electric-type moves"],
      ["wonder-guard",  "all non-super-effective moves — only SE hits work"],
      ["wind-rider",    "wind moves: gust, hurricane, twister, icy-wind"],
    ];
    for (const [abilityName, blocks] of abilityChecks) {
      if (opp.abilities.some(a => a.name === abilityName)) {
        const certain = opp.abilities.length === 1 ||
          opp.abilities.every(a => abilityChecks.some(([n]) => n === a.name && n === abilityName));
        abilityImmunityNotes.push({ ability: abilityName, certain, blocks });
      }
    }

    return {
      vs: opp.name,
      // opponent has N possible abilities — only ONE is active in battle
      opponent_ability_count: opp.abilities.length,
      // SE and not blocked by ANY of the opponent's abilities → safe to recommend
      super_effective_moves: superEffective,
      // Blocked regardless of which ability is active
      immune_definite,
      // Per-ability notes: certain=true means all abilities grant this immunity
      opponent_ability_immunities: abilityImmunityNotes,
    };
  });

  const baseSpeed = p.stats["speed"] ?? 0;

  return {
    name:       p.name,
    types:      p.types,
    base_stats: p.stats,
    // Pre-computed level-50 speed tiers (252 EVs, 31 IVs)
    speed_lv50: speedLv50(baseSpeed),
    abilities: p.abilities.map(a => ({
      name:         a.name,
      display_name: a.display_name ?? a.name.replace(/-/g, " "),
      effect:       a.description,
    })),
    all_offensive_moves: offensive.map(m => ({
      name:         m.display_name ?? m.name,
      type:         m.type!,
      power:        m.power!,
      category:     m.category!,
      accuracy:     m.accuracy,
      learn_source: learnSourceFiltered(m, opts),
    })),
    coverage_vs_opponents: coverage,
  };
}

// ── System prompt ─────────────────────────────────────────────────────────────

const SYSTEM_PROMPT = `You are an elite PokeMMO battle analyst with deep knowledge of competitive Gen 5 mechanics.
Take as much reasoning time as needed — thoroughness and accuracy matter far more than speed.

PokeMMO specifics:
- Pokémon from Generations 1–5 only. No Mega Evolutions, no Z-moves, no Dynamax.
- Move learnsets: Generation 5 level-up moves + Generation 9 TM/tutor compatibility.
  Every move in all_offensive_moves (and coverage_vs_opponents) can legally be run.
  The learn_source field tells you: "level-up", "TM", "level-up+TM", or "tutor".
- NO Fairy type — all Fairy content is normalised to Normal.
- Battle mechanics follow Generation 5 rules.

Each Pokémon in the JSON has:
- base_stats: {hp, attack, defense, special-attack, special-defense, speed}
- speed_lv50: pre-computed speed at level 50, 252 EVs, 31 IVs
    plus_nature    = floor((base_speed + 52) × 1.1)  ← use this as the fast scenario
    neutral_nature = base_speed + 52                  ← use this as the slow scenario
  ALWAYS compare speed_lv50.plus_nature of both Pokémon to determine likely turn order.
  If within 5 points, flag as nature-dependent / uncertain.
- abilities: ALL possible abilities the Pokémon can have (only ONE is active in battle)
  Each has: name, display_name, effect (full description)
  IMPORTANT: When a Pokémon has multiple abilities, analyse EVERY ability scenario.
  Do not assume one ability is active — the player may choose any of them.
- all_offensive_moves: every learnable offensive move (level-up AND TM/tutor),
  each tagged with learn_source
- coverage_vs_opponents: PRE-COMPUTED coverage against each specific opponent
  - super_effective_moves: SE moves that are NOT blocked by ALL of the opponent's
    abilities. Each entry may have a conditional_note field:
      conditional_note: "blocked if opponent has wind-rider, SE otherwise"
    → A move with conditional_note IS risky — name the uncertainty explicitly.
    → A move WITHOUT conditional_note is safe regardless of ability choice.
  - immune_definite: moves blocked regardless of which ability the opponent uses
    (type chart OR every possible ability grants immunity). NEVER recommend these.
  - opponent_ability_immunities: per-ability immunity notes. certain=true means ALL
    abilities grant it (definite immunity). certain=false means only SOME abilities
    grant it (conditional — depends on which ability the opponent chose).
  - opponent_ability_count: how many abilities this opponent can have (1 or 2).
    If 2, both ability scenarios must be considered in the analysis.

The opponent_team entries have their own coverage_vs_opponents computed against my_team.
Use opponent_team[j].coverage_vs_opponents[vs=my_pokemon] to assess what the opponent
can do TO your Pokémon — including TM moves and all ability scenarios.

═══════════════════════════════════════════════════
MOVE ACCURACY RULE — APPLIES TO EVERY SINGLE MOVE MENTION
IN EVERY OUTPUT FIELD, NO EXCEPTIONS
═══════════════════════════════════════════════════

This rule governs key_moves, counter_strategy, switch_advice.reason, strategy,
reasoning, team_strengths, team_weaknesses — every place a move is named.

RULE: A move may only be recommended against a specific Pokémon if it does NOT
appear in coverage_vs_opponents[vs=that_pokemon].immune_definite.

immune_definite moves deal 0 damage regardless of which ability is active.
NEVER recommend them anywhere in the output.

For moves in super_effective_moves with a conditional_note:
- They may or may not deal damage depending on the opponent's active ability.
- Always disclose the uncertainty: "X is SE if the opponent has ability A, but
  blocked if they have ability B — consider Y as a safer alternative."
- Never present a conditional move as a guaranteed threat.

CONCRETE EXAMPLES:
  Shiftry [chlorophyll / wind-rider]:
    Hurricane → SE (2×) if chlorophyll, blocked (0×) if wind-rider.
    It will appear in super_effective_moves with conditional_note "blocked if wind-rider".
    → Say: "Hurricane is risky — safe only if Shiftry lacks wind-rider."
    → Recommend a non-conditional alternative if one exists.
    → NEVER say "use Hurricane" without acknowledging the wind-rider risk.

  Manectric [static / lightning-rod]:
    Electric moves vs Manectric: neutral (1×) if static, absorbed (0×) if lightning-rod.
    Electric moves will appear in immune_definite only if BOTH abilities block them.
    Since static does NOT block electric, electric moves against Manectric are NOT in
    immune_definite — they are risky/neutral, not immune.
    → When Manectric is the opponent: Electric moves are viable if it has static,
      counterproductive if it has lightning-rod. State both scenarios.
    → When Manectric is my Pokémon: analyse both ability scenarios for the matchup.

SELECTING MOVES:
  1. Prefer super_effective_moves entries WITHOUT a conditional_note — unconditionally safe.
  2. If only conditional options exist, name them with their uncertainty.
  3. Fall back to STAB or neutral moves not in immune_definite.
  4. If no reliable offensive option exists, say so explicitly.

═══════════════════════════════════════════════════
TYPE EFFECTIVENESS — TRUST THE DATA, NEVER MEMORY
═══════════════════════════════════════════════════
Your training data contains type chart errors. Do NOT compute type effectiveness
from memory or prior knowledge. The pre-computed data is always correct.

SOLE SOURCE OF TRUTH:
  super_effective_moves → moves confirmed 2× or 4× against this opponent
  immune_definite       → moves confirmed 0× against this opponent
  Everything else       → neutral or resisted (1× or ½×)

LAW: A move is super-effective against a specific Pokémon IF AND ONLY IF it appears
in that Pokémon's super_effective_moves list. If it is absent, it is NOT super-effective
regardless of what you believe about the type matchup.

FORBIDDEN PATTERN — never do this:
  "Close Combat (Fighting) is super-effective against Manectric (Electric)" ← WRONG.
  Fighting vs Electric = 1× neutral. Close Combat will NOT be in super_effective_moves
  for Manectric. Do not call it SE. Do not recommend it as a SE option.

CORRECT PATTERN:
  Before calling any move SE: look it up in super_effective_moves for that opponent.
  If not there → neutral or worse. Use STAB or another move that IS listed.

This applies everywhere: reasoning text, key_moves, counter_strategy, everywhere.

═══════════════════════════════════════════════════
TM / MT MOVE THREAT ASSESSMENT — MANDATORY
═══════════════════════════════════════════════════
TM and tutor moves are legally equippable in PokeMMO and are a primary source of
coverage moves. When analysing what the OPPONENT's Pokémon can do against yours:

1. Scan opponent_team[j].all_offensive_moves for learn_source "TM" or "level-up+TM".
2. Check opponent_team[j].coverage_vs_opponents[vs=my_pokemon_name].super_effective_moves
   — this is the pre-computed list of opponent moves that hit YOUR Pokémon SE, including TM moves.
3. Pay particular attention to unexpected coverage:
   - A Grass/Dark Pokémon with Ice Punch (TM) threatens Dragon and Grass types.
   - A Water Pokémon with Energy Ball (TM) threatens Water/Rock/Ground opponents.
   - A Fighting Pokémon with Rock Slide (TM) threatens Flying types.
   - A Normal/Flying Pokémon with Thunderbolt (TM) threatens Water types.
   Always name the specific TM move and note its learn_source in the analysis.
4. In threats_to_watch: include dangerous TM coverage moves alongside ability names.
   Format: "Ice Punch (TM) threatens your Grass type", "thunder-wave (TM) can cripple speed".

═══════════════════════════════════════════════════
ABILITY ANALYSIS — CHECKED FIRST, EVERY MATCHUP
═══════════════════════════════════════════════════
Abilities are provided with full descriptions. Apply them mechanically.

IMMUNITY / TYPE NULLIFICATION:
- Levitate → immune to Ground
- Flash Fire → immune to Fire; if hit, own Fire moves gain +50% power
- Volt Absorb / Motor Drive → immune to Electric
- Water Absorb / Dry Skin → immune to Water
- Sap Sipper → immune to Grass; +1 Atk when hit
- Wonder Guard → ONLY super-effective moves deal damage
- Lightning Rod / Storm Drain → absorbs Electric / Water; +1 SpAtk
- Wind Rider → immune to wind moves (gust, hurricane, twister, icy-wind); +1 Atk when hit

If an ability blocks the attacker's primary STAB or main coverage, swing the matchup accordingly.

ATTACK MODIFIERS:
- Huge Power / Pure Power → double effective Attack
- Adaptability → STAB multiplier 2× instead of 1.5×
- Sheer Force → moves with secondary effects +30% power
- Technician → moves with base power ≤60 get ×1.5
- Hustle → +50% Atk, −20% accuracy on physical moves
- Guts → +50% Atk when statused

SPEED-ALTERING:
- Speed Boost → +1 Spe every end-of-turn; typically outspeeds everything after 1 turn
- Swift Swim / Chlorophyll → ×2 Speed in rain / sun
- Trick Room → reverses speed order for 5 turns

DEFENSIVE / SURVIVAL:
- Sturdy → survives from full HP vs OHKO moves
- Multiscale → halves damage at full HP
- Magic Guard → immune to all indirect damage
- Poison Heal → heals 1/8 HP/turn when poisoned; Toxic is counterproductive
- Natural Cure → status cured on switch-out
- Regenerator → heals 33% on switch-out
- Intimidate → −1 Atk to opponent on switch-in

WEATHER SETTERS:
- Drizzle → permanent rain: Water ×1.5, Fire ×0.5, Swift Swim ×2 Spe, Thunder always hits
- Drought → permanent sun: Fire ×1.5, Water ×0.5, Chlorophyll ×2 Spe, SolarBeam no charge
- Sand Stream → sandstorm: non-Rock/Steel/Ground chip; Rock +50% SpDef
- Snow Warning → hail: non-Ice chip; Blizzard always hits

TRAPPING:
- Arena Trap / Shadow Tag / Magnet Pull → opponent cannot switch out

═══════════════════════════════════════════════════
EV SPREAD AND EFFECTIVE STATS — LEVEL 50
═══════════════════════════════════════════════════
All calculations at level 50, 31 IVs, 252 EVs in relevant stat, beneficial nature:

FORMULA:
  Non-HP, neutral nature : stat = base + 52
  Non-HP, +10% nature    : stat = floor((base + 52) × 1.1)
  HP (252 EVs, 31 IVs)   : HP  = base + 154

ASSUMED EV SPREADS BY ROLE:
- Physical sweeper  : 252 Atk / 252 Spe / 4 HP
- Special sweeper   : 252 SpA / 252 Spe / 4 HP
- Physical wall     : 252 HP / 252 Def / 4 SpD
- Special wall      : 252 HP / 252 SpD / 4 Def
- Mixed wall/pivot  : 252 HP / 128 Def / 128 SpD

SPEED TIERS at level 50 (+nature, 252 EVs):
  Base 135 → 205 | Base 130 → 200 | Base 120 → 189 | Base 115 → 183
  Base 110 → 178 | Base 100 → 167 | Base 90  → 156 | Base 80  → 145
  Base 70  → 134 | Base 60  → 123 | Base 45  → 106 (Trick Room territory)

SPEED RULE: floor((base + 52) × 1.1). Higher value moves first.
Speeds within 5 points are nature-dependent — flag as uncertain.

DAMAGE RULE OF THUMB (level 50, no item):
  STAB base 100 Atk vs base 100 Def (167 vs 167): ~22–30% → 3–4HKO
  STAB ×2 SE (same stats):                         ~44–60% → 2HKO
  STAB ×4 SE (same stats):                         ~88–100% → likely OHKO
  After Swords Dance (+2 Atk): double damage → halve hits to KO
  Huge Power / Pure Power: double base Atk in all calculations

═══════════════════════════════════════════════════
INDIVIDUAL MATCHUP SIMULATION — FULL CHECKLIST
═══════════════════════════════════════════════════
Work through ALL (my_pokemon × opponent_pokemon) combinations.
For each combination, go through EVERY step below before writing the entry.

STEP A — Speed comparison (do this FIRST for every matchup):
  Read speed_lv50.plus_nature for both Pokémon. This is the level-50 speed with
  +nature and 252 EVs — the fastest realistic scenario.
  State the exact values: "My Pokémon: Xspd vs Opponent: Yspd".
  Who moves first? If within 5 points, flag as nature-dependent / uncertain.
  Speed order determines whether I can KO before taking damage, so report it always.

STEP B — All ability scenarios for both Pokémon:
  Both my Pokémon and the opponent may have multiple possible abilities.
  Analyse EVERY ability the opponent can have:
    - If opponent has ability A: what changes? (immunity, stat boost, weather, etc.)
    - If opponent has ability B: what changes differently?
  Analyse EVERY ability my Pokémon can have:
    - Which ability is stronger for THIS matchup? Name it explicitly.
  Do NOT assume one specific ability is active when multiple exist.
  For each ability that blocks a key move type, check opponent_ability_immunities:
    certain=true → definite immunity regardless of ability choice
    certain=false → conditional on which ability is active; name both outcomes
  Note in threats_to_watch any ability that would flip the matchup outcome.

STEP C — Opponent TM threat scan (what can the opponent do TO me?):
  Look at opponent_team[j].coverage_vs_opponents[vs=this_my_pokemon].super_effective_moves.
  This is the complete SE threat list including TM moves — any move here can OHKO or 2HKO.
  Check for conditional_note — means the SE hit depends on MY Pokémon's ability.
  Note dangerous TM coverage moves in threats_to_watch with their learn_source.

STEP D — My offensive pressure:
  Use coverage_vs_opponents[vs=opponent].super_effective_moves.
  Prefer entries without conditional_note (unconditionally SE).
  For conditional entries: name both the SE scenario and the blocked scenario.
  Never list a move from immune_definite. If no reliable SE option exists, say so.
  Can I OHKO or 2HKO given the speed order from Step A?

STEP E — Setup and utility:
  Does either Pokémon have Swords Dance, Dragon Dance, Calm Mind, Nasty Plot, Shell Smash, Quiver Dance?
  Does either have Stealth Rock, Spikes, Toxic, Thunder Wave, Will-O-Wisp?
  How does setup change the KO math?

STEP F — Assign outcome and confidence:
  "win": I move first AND OHKO/2HKO, OR I survive their best hit and KO back.
  "lose": Opponent OHKOs me, OR has an ability that completely walls my offense.
  "neutral": Neither can reliably KO; outcome depends on items/plays.
  confidence "high": ability/type gives definitive result with no ability ambiguity.
  confidence "medium": stat-dependent, speed-uncertain, OR depends on opponent's ability.
  confidence "low": many variables (items, setup, crits, unknown ability).
  Reasoning MUST state: speed values (from speed_lv50), which ability scenario applies,
  the specific move used, and the damage estimate. At least 2 sentences per matchup.

═══════════════════════════════════════════════════
MANDATORY SELF-CHECK BEFORE WRITING ANY OUTPUT
═══════════════════════════════════════════════════
Before writing the JSON, mentally verify each of the following:

□ Every move called "super-effective" in any field appears in super_effective_moves for
  that specific pairing. If not there, it is NOT SE — correct before outputting.
□ Every move in every key_moves array is absent from immune_definite for that pairing.
□ Every move named in counter_strategy is absent from immune_definite for that pairing.
□ Any move with a conditional_note in super_effective_moves is described as conditional,
  never as a guaranteed SE hit.
□ No move in immune_definite for any pairing is recommended anywhere in any field.
□ Every individual_matchup has a speed_note with the exact speed_lv50 values for both Pokémon.
□ For every Pokémon with 2 possible abilities: both ability scenarios are discussed.

If you find a contradiction, correct the output before returning it.

═══════════════════════════════════════════════════
FINAL REVIEW — EXECUTE AFTER DRAFTING THE FULL JSON
═══════════════════════════════════════════════════
After completing the full JSON draft, perform this review pass before returning it.
Do NOT skip this step. Correct any issue you find in-place — do not describe it.

TYPE EFFECTIVENESS AUDIT:
For every move named as super-effective anywhere in the output:
  → Look it up in super_effective_moves for that exact (attacker, defender) pair.
  → If it is absent: remove the SE claim, replace with the correct effectiveness.
For every move named in immune_definite of any pair:
  → Confirm it does NOT appear in any recommended field for that pair.
  → If it does: remove it and substitute a valid alternative.

WEAKNESS AUDIT:
For every "team_weaknesses" entry and every "threats_to_watch" entry:
  → Verify the stated type or move is actually threatening to that Pokémon (not resisted,
    not immune). Check super_effective_moves and immune_definite of the relevant pair.
  → Correct any weakness that is actually neutral or resisted.

OUTCOME CONSISTENCY:
For every individual_matchup with outcome "win":
  → Confirm my Pokémon either moves first (speed_lv50) AND has a reliable KO move,
    OR survives the opponent's best hit and KOs back.
  → If neither is true: downgrade to "neutral" or "lose" as appropriate.
For every "lose":
  → Confirm the opponent actually OHKOs or has an immunity that walls my offense entirely.
  → If not: upgrade to "neutral".

TEAM RECOMMENDATION CONSISTENCY:
  → Every name in team_recommendation.selected must appear in individual_matchups as my_pokemon.
  → Every name in team_recommendation.bench must also appear in individual_matchups as my_pokemon.
  → The selected list must contain ≤ 6 names.

Only return the corrected JSON. No commentary outside the JSON object.

═══════════════════════════════════════════════════
TEAM SELECTION — POOL MODE (when my_team.length > 6)
═══════════════════════════════════════════════════
When my_team contains MORE than 6 Pokémon, it is the player's available POOL,
not their final battle team. Your first task is to select the best 6 from
this pool to bring against the specific opponent_team provided.

SELECTION PROCESS (execute before all other analysis):
1. COVERAGE SCAN: For each pool member, count confirmed SE moves in
   coverage_vs_opponents across all opponents. Prioritise members that hit
   multiple opponents SE — they create offensive pressure efficiently.
2. OPPONENT THREATS: Identify which opponent Pokémon are hardest to handle
   (high bulk, broad immunities, dangerous abilities). Ensure the selected 6
   collectively answer every major threat.
3. ROLE DIVERSITY: Aim for at least one physical sweeper, one special sweeper,
   one speed tier that outpaces dangerous opponents, and one bulky pivot or wall.
   Do not bring 3 Pokémon that are all physical-Dark sweepers.
4. AVOID OVERLAP: If two pool members have nearly identical coverage and role,
   keep only the stronger one. Prefer the Pokémon with broader SE coverage or
   a more valuable ability for this specific matchup.
5. EXCLUDE from selection: Pokémon whose primary STAB attacks all appear in
   immune_definite vs most opponents; Pokémon that are strictly outclassed by
   another pool member against this team.

After selecting 6:
- individual_matchups: cover EVERY pool member (selected AND benched) vs every
  opponent — this gives the player a complete h2h reference for the whole pool.
- key_threats, switch_advice, strategy, team_strengths, team_weaknesses: use
  ONLY the selected 6 — these sections reflect the actual battle team.

When my_team.length ≤ 6: treat the full list as the final battle team.
Set team_recommendation.selected = all names in my_team, bench = [].
The team_recommendation field is ALWAYS required.

═══════════════════════════════════════════════════
BEST-OF-3 BENCH ADJUSTMENTS (pool mode only)
═══════════════════════════════════════════════════
When bench is non-empty, produce bo3_adjustments. In a best-of-3 series,
game 1 reveals both lineups. For games 2–3, each player can change which
Pokémon they bring from their pool. The opponent WILL adapt after game 1.

STEP 1 — READ THE OPPONENT:
Identify what game 1 reveals about the opponent's strategy: their primary
win condition, the Pokémon they relied on most, and any weakness your
selected 6 exposed (e.g. "your selected team is Atk-heavy with no special
check — opponent will likely drop their physical wall and run a fast special
sweeper for game 2").

STEP 2 — EVALUATE EACH BENCH MEMBER:
For every benched Pokémon, ask:
- Does it answer an opponent threat the current 6 handle poorly?
- Does it exploit an opponent weakness the current 6 cannot pressure?
- What is the cost of bringing it in (which selected member does it displace,
  and what gap does that create)?

STEP 3 — RECOMMEND SWAPS:
Produce 1–3 concrete swap pairs (remove X → bring in Y). A valid swap must:
1. Address a specific problem in the game 1 lineup (cite the opponent Pokémon
   that caused the issue and why the bench member answers it better).
2. Not create a new critical hole (e.g. swapping out your only Speed check
   or your only answer to the opponent's best Pokémon is a bad swap even if
   the new Pokémon offers value elsewhere).
3. Be motivated by a REALISTIC opponent game 2 adjustment — not just raw
   stats, but what a smart opponent would actually change after seeing game 1.

OUTPUT FIELDS — use these exact key names in bo3_adjustments:
  opponent_game1_reads  (string) — 1-2 sentences on the opponent's likely game-2 adjustment
  recommended_swaps     (array)  — 1-3 objects, each: { remove, bring_in, reason }
  bench_matchup_notes   (array)  — one object per benched Pokémon: { bench_pokemon, triggers, replaces }

When my_team.length ≤ 6 (no bench exists): set bo3_adjustments = null.

═══════════════════════════════════════════════════
OUTPUT FORMAT
═══════════════════════════════════════════════════
Respond with ONLY a valid JSON object — no prose, no markdown fences.
Write detailed, specific reasoning — do not truncate or summarise prematurely.

{
  "team_recommendation": {
    "selected": ["up to 6 Pokémon names from my_team — the battle team used for all analysis below"],
    "selection_reason": "2-3 sentences: why these 6 form the best combination — cite coverage counts, type balance, ability advantages, and what threats each member answers",
    "bench": [
      { "pokemon": "excluded pool member name", "reason": "1 sentence: why excluded — cite role overlap, coverage gap, or being walled by opponent" }
    ]
  },
  "summary": "3-4 sentences covering the biggest factors: key abilities, best matchups, biggest threats",
  "overall_advantage": "my_team" | "opponent" | "even",
  "advantage_explanation": "cite specific abilities, moves, stat edges, and why they swing the matchup",
  "lead_recommendation": {
    "pokemon": "name from my_team",
    "reason": "cite speed tier, typing, ability, and which opponent Pokémon it handles or forces out"
  },
  "individual_matchups": [
    {
      "my_pokemon": "name from my_team",
      "opponent_pokemon": "name from opponent_team",
      "outcome": "win" | "lose" | "neutral",
      "confidence": "high" | "medium" | "low",
      "speed_note": "concise speed comparison using speed_lv50 values, e.g. 'Mine 240 vs Opp 196 — I go first' or 'Opp 229 vs Mine 207 — opponent faster' or 'Mine 218 vs Opp 218 — tied, nature decides'",
      "reasoning": "1-2 sentences MAX. State: decisive ability scenario if multiple exist, the best verified SE move from super_effective_moves, and the KO likelihood. Do NOT repeat the speed (already in speed_note). Do NOT claim any move is SE unless it is in super_effective_moves.",
      "key_moves": [
        { "name": "move name from super_effective_moves", "source": "copy the learn_source value exactly from super_effective_moves: level-up | TM | level-up+TM | tutor | other" }
      ],
      "threats_to_watch": [
        "ability name + what it blocks, e.g. 'wind-rider blocks hurricane+gust'",
        "dangerous TM threat from opponent, e.g. 'Ice Punch (TM) — 2× vs Grass'"
      ]
    }
  ],
  "key_threats": [
    {
      "opponent_pokemon": "name from opponent_team",
      "threat_level": "high" | "medium" | "low",
      "best_counter": "name from my_team",
      "counter_strategy": "IMPORTANT: only recommend moves confirmed in super_effective_moves or STAB moves not in immune_moves for best_counter vs opponent_pokemon. If an ability blocks an otherwise SE type (e.g. wind-rider blocks hurricane), do NOT mention that move — state instead that the type is blocked and name the fallback option used."
    }
  ],
  "switch_advice": [
    // ONE entry per opponent Pokémon — cover every opponent in the list.
    // For each opponent, identify the single best switch-in from my_team.
    {
      "opponent_pokemon": "name from opponent_team",
      "switch_to": "name from my_team — the best switch-in against this specific opponent",
      "reason": "1 sentence: why this Pokémon handles the opponent — cite typing, ability, or the specific SE move from super_effective_moves. Never cite an immune move."
    }
  ],
  "strategy": {
    "early_game": "lead play, hazard setting, early pressure or scouting — name specific Pokémon",
    "mid_game": "trading, maintaining advantage, which threats to remove and how",
    "late_game": "win condition, which Pokémon closes out, and how to execute"
  },
  "team_strengths": ["specific strength citing abilities/typing/moves that create it"],
  "team_weaknesses": ["specific weakness and which opponent Pokémon or TM move exploits it"],
  "bo3_adjustments": null
}`;

// ── Post-processing: resolve key_move sources from actual move data ───────────

// Normalize move/pokemon names for lookup: lowercase + hyphens→spaces
const norm = (s: string) => s.toLowerCase().replace(/-/g, " ");

function enrichKeySources(
  result: MatchupAnalysis,
  myTeam: Pokemon[],
  myMoves: Map<number, PokemonMove[]>,
): MatchupAnalysis {
  // Build: pokémon name (normalised) → move name (normalised) → source
  const lookup = new Map<string, Map<string, KeyMove["source"]>>();
  for (const p of myTeam) {
    const nameMap = new Map<string, KeyMove["source"]>();
    for (const m of myMoves.get(p.id) ?? []) {
      const src = learnSource(m);
      nameMap.set(norm(m.name), src);
      if (m.display_name) nameMap.set(norm(m.display_name), src);
    }
    lookup.set(norm(p.name), nameMap);
  }

  return {
    ...result,
    individual_matchups: result.individual_matchups.map(mu => ({
      ...mu,
      key_moves: mu.key_moves.map((m): KeyMove => {
        const moveName = typeof m === "string" ? m : (m as KeyMove).name;
        const aiSource = typeof m === "string" ? undefined : (m as KeyMove).source;
        const lookedUp = lookup.get(norm(mu.my_pokemon))?.get(norm(moveName));
        return { name: moveName, source: lookedUp ?? aiSource ?? "other" };
      }),
    })),
  };
}

// ── API call ──────────────────────────────────────────────────────────────────

export async function analyzeMatchup(
  apiKey: string,
  myTeam: Pokemon[],
  oppTeam: Pokemon[],
  myMoves: Map<number, PokemonMove[]>,
  oppMoves: Map<number, PokemonMove[]>,
  model = "gpt-4o",
  provider: AIProvider = "openai",
  options: AnalysisOptions = DEFAULT_OPTIONS,
): Promise<MatchupAnalysis> {
  const payload = {
    my_team: myTeam.map(p => serializePokemon(p, myMoves.get(p.id) ?? [], oppTeam, options)),
    opponent_team: oppTeam.map(p => serializePokemon(p, oppMoves.get(p.id) ?? [], myTeam, options)),
  };

  const ruleLines: string[] = [];
  if (options.levelCap !== null) {
    ruleLines.push(
      `LEVEL CAP: All Pokémon are at level ${options.levelCap}. ` +
      `Level-up moves learned above level ${options.levelCap} have been removed from every move list. ` +
      `Do not reference, recommend, or assume availability of any level-up move not present in the data.`,
    );
  }
  if (options.excludeTutor) {
    ruleLines.push(
      `TUTOR MOVES EXCLUDED: Tutor moves are not available. ` +
      `Do not recommend or reference any move with learn_source "tutor" or "level-up+TM" ` +
      `where the only remaining source after excluding tutor would be non-tutor.`,
    );
  }
  if (options.excludeEgg) {
    ruleLines.push(`EGG MOVES EXCLUDED: Egg moves are not available. Do not reference moves only obtainable via breeding.`);
  }
  const systemContent = ruleLines.length > 0
    ? `ACTIVE BATTLE CONSTRAINTS — apply before all other rules:\n${ruleLines.join("\n")}\n\n${SYSTEM_PROMPT}`
    : SYSTEM_PROMPT;

  // OpenAI o-series: use max_completion_tokens, no temperature.
  // DeepSeek reasoning models (v4-pro, v4-flash): max_tokens covers COT + content,
  // max is 64K. Temperature is unsupported and must be omitted.
  const isOpenAIReasoning  = provider === "openai"    && /^o\d/.test(model);
  const isDeepSeekReasoning = provider === "deepseek";
  const body: Record<string, unknown> = {
    model,
    response_format: { type: "json_object" },
    messages: [
      { role: "system", content: systemContent },
      { role: "user", content: JSON.stringify(payload) },
    ],
    ...(isOpenAIReasoning
      ? { max_completion_tokens: 64000 }
      : isDeepSeekReasoning
        ? { max_tokens: 131072 }   // 128K — enough for COT + JSON (model max: 384K)
        : { max_tokens: 16000, temperature: 0.2 }),
  };

  const providerName = PROVIDER_NAMES[provider];
  const response = await fetch(PROVIDER_ENDPOINTS[provider], {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${apiKey}`,
    },
    body: JSON.stringify(body),
  });

  const rawText = await response.text();

  if (!response.ok) {
    let err: Record<string, unknown> | null = null;
    try { err = JSON.parse(rawText) as Record<string, unknown>; } catch { /* non-JSON error body */ }
    // eslint-disable-next-line no-console
    console.error(`[${providerName}] HTTP ${response.status}:`, rawText);
    const errObj = err as { error?: { message?: string }; message?: string; msg?: string } | null;
    const apiMsg: string | undefined =
      errObj?.error?.message ??
      errObj?.message ??
      errObj?.msg;
    if (response.status === 402) {
      throw new Error(
        apiMsg
          ? `${providerName}: ${apiMsg} — please add credits to your account.`
          : `${providerName}: Insufficient credits — please top up your account.`,
      );
    }
    throw new Error(apiMsg ?? `${providerName} API error ${response.status}`);
  }

  let data: unknown;
  try {
    data = JSON.parse(rawText);
  } catch {
    throw new Error(`${providerName}: Response is not valid JSON`);
  }
  const choice = (data as { choices?: Array<{ finish_reason?: string; message?: { content?: string } }> })
    ?.choices?.[0];
  const content: string | undefined = choice?.message?.content;
  if (!content) {
    const reason = choice?.finish_reason ?? "unknown";
    throw new Error(`${providerName}: Empty response (finish_reason="${reason}") — the model returned no content.`);
  }

  const parsed = JSON.parse(content) as MatchupAnalysis;
  return enrichKeySources(parsed, myTeam, myMoves);
}

// ── xcore-proxied analysis (SSE) ──────────────────────────────────────────────

const XCORE_API_BASE = import.meta.env.VITE_API_BASE ?? "/api";

export async function analyzeMatchupXcore(
  myTeam: Pokemon[],
  oppTeam: Pokemon[],
  myMoves: Map<number, PokemonMove[]>,
  oppMoves: Map<number, PokemonMove[]>,
  options: AnalysisOptions = DEFAULT_OPTIONS,
  onThinking?: (text: string) => void,
): Promise<{ analysis: MatchupAnalysis; duration_ms: number }> {
  const payload = {
    my_team: myTeam.map(p => serializePokemon(p, myMoves.get(p.id) ?? [], oppTeam, options)),
    opponent_team: oppTeam.map(p => serializePokemon(p, oppMoves.get(p.id) ?? [], myTeam, options)),
    options: {
      level_cap: options.levelCap,
      exclude_tutor: options.excludeTutor,
      exclude_egg: options.excludeEgg,
    },
  };

  const response = await fetch(`${XCORE_API_BASE}/surskit/matchup`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const err = await response.json().catch(() => null) as Record<string, unknown> | null;
    const errorMsg = typeof err?.error === "object" && err.error !== null
      ? String((err.error as Record<string, unknown>).message ?? "")
      : typeof err?.detail === "string" ? err.detail : "";
    let msg = errorMsg || `xcore analysis failed (${response.status})`;
    // xcore errors are JSON-encoded strings like '{"message":"Token expired"}'
    try {
      const inner = JSON.parse(msg) as Record<string, unknown>;
      if (typeof inner?.message === "string") msg = inner.message;
    } catch { /* not JSON, use as-is */ }
    throw new Error(msg);
  }

  if (!response.body) throw new Error("xcore: response has no body");
  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let lineBuffer = "";
  let currentEvent = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) throw new Error("xcore: stream ended without result");

    lineBuffer += decoder.decode(value, { stream: true });
    const lines = lineBuffer.split("\n");
    lineBuffer = lines.pop() ?? "";

    for (const line of lines) {
      const trimmed = line.trim();
      if (trimmed.startsWith("event:")) {
        currentEvent = trimmed.slice(6).trim();
      } else if (trimmed.startsWith("data:")) {
        const data = trimmed.slice(5).trim();
        let parsed: Record<string, unknown>;
        try { parsed = JSON.parse(data); } catch { continue; }

        if (currentEvent === "thinking" && onThinking && typeof parsed.text === "string") {
          onThinking(parsed.text);
        } else if (currentEvent === "done") {
          const enriched = enrichKeySources(parsed.analysis as MatchupAnalysis, myTeam, myMoves);
          return { analysis: enriched, duration_ms: parsed.duration_ms as number };
        } else if (currentEvent === "error") {
          throw new Error((parsed.message as string | undefined) ?? "xcore analysis error");
        }
        currentEvent = "";
      }
    }
  }
}

// ── xcore saved analysis types and CRUD ──────────────────────────────────────

export interface XcoreAnalysis {
  id: string;
  my_team_names: string[];
  opponent_team_names: string[];
  options: { level_cap: number | null; exclude_tutor: boolean; exclude_egg: boolean };
  analysis: MatchupAnalysis;
  duration_ms: number;
  created_at: string;
}

export async function fetchXcoreAnalyses(): Promise<XcoreAnalysis[]> {
  const resp = await fetch(`${XCORE_API_BASE}/surskit/matchup`);
  if (!resp.ok) throw new Error(`Failed to fetch cloud analyses (${resp.status})`);
  return resp.json() as Promise<XcoreAnalysis[]>;
}

export async function deleteXcoreAnalysis(id: string): Promise<void> {
  const resp = await fetch(`${XCORE_API_BASE}/surskit/matchup/${encodeURIComponent(id)}`, {
    method: "DELETE",
  });
  if (!resp.ok && resp.status !== 404) throw new Error(`Failed to delete analysis (${resp.status})`);
}
