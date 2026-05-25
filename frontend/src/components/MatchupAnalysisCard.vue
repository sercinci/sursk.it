<template>
  <article class="card-surface overflow-hidden rounded-2xl">

    <!-- ── Header: overall advantage ─────────────────────────────────────── -->
    <div
      :class="[
        'border-b border-black/8 px-4 py-4 sm:px-5',
        analysis.overall_advantage === 'my_team'  ? 'bg-sky-50/60'   :
        analysis.overall_advantage === 'opponent' ? 'bg-amber-50/60' : 'bg-gray-50/60'
      ]"
    >
      <div class="flex flex-wrap items-center gap-3">
        <div class="flex min-w-0 flex-wrap items-center gap-2">
          <span class="font-mono text-xs uppercase tracking-widest text-accent">AI Analysis</span>
          <span class="max-w-full rounded-full px-3 py-0.5 text-xs font-bold" :class="
            analysis.overall_advantage === 'my_team'  ? 'bg-sky-500 text-white' :
            analysis.overall_advantage === 'opponent' ? 'bg-amber-500 text-white' : 'bg-gray-400 text-white'
          ">
            <template v-if="analysis.overall_advantage === 'my_team'">
              <span class="text-sky-100">My Team</span> has the advantage
            </template>
            <template v-else-if="analysis.overall_advantage === 'opponent'">
              <span class="text-amber-100">Opponent</span> has the advantage
            </template>
            <template v-else>Even Matchup</template>
          </span>
        </div>
        <p class="text-xs text-muted">{{ analysis.advantage_explanation }}</p>
      </div>
      <p class="mt-2 text-sm text-text">{{ analysis.summary }}</p>
    </div>

    <!-- ── Pool selection result (shown when my_pool > 6) ──────────────────── -->
    <div v-if="analysis.team_recommendation?.bench?.length > 0" class="border-b border-black/8 bg-sky-50/40 px-4 py-4 sm:px-5">
      <p class="mb-2.5 font-mono text-[10px] uppercase tracking-widest text-muted">Recommended Team from Your Pool</p>
      <div class="flex flex-wrap gap-2 mb-3">
        <div
          v-for="name in analysis.team_recommendation.selected"
          :key="name"
          class="flex min-w-0 items-center gap-1.5 rounded-xl border border-sky-200 bg-white px-2.5 py-1.5"
        >
          <img v-if="spriteFor(name, myTeam)" :src="spriteFor(name, myTeam)" :alt="name" class="h-7 w-7 object-contain" />
          <span class="min-w-0 truncate font-mono text-xs font-semibold capitalize text-sky-700">{{ name }}</span>
        </div>
      </div>
      <p class="mb-2 text-xs text-muted">{{ analysis.team_recommendation.selection_reason }}</p>
      <details v-if="analysis.team_recommendation.bench.length > 0">
        <summary class="select-none font-mono text-[9px] uppercase tracking-widest text-muted/60 hover:text-muted">
          {{ analysis.team_recommendation.bench.length }} benched ▾
        </summary>
        <div class="mt-2 space-y-1">
          <div v-for="b in analysis.team_recommendation.bench" :key="b.pokemon" class="flex items-start gap-2">
            <span class="w-24 shrink-0 font-mono text-[10px] font-semibold capitalize text-muted/70">{{ b.pokemon }}</span>
            <span class="text-[10px] leading-snug text-muted">{{ b.reason }}</span>
          </div>
        </div>
      </details>
    </div>

    <div class="divide-y divide-black/8">

      <!-- ── Lead + Strengths/Weaknesses row ─────────────────────────────── -->
      <div class="grid grid-cols-1 gap-0 divide-y divide-black/8 sm:grid-cols-3 sm:divide-x sm:divide-y-0">

        <!-- Lead recommendation -->
        <div class="p-4">
          <p class="mb-2 font-mono text-[10px] uppercase tracking-widest text-muted">Recommended Lead</p>
          <div class="flex items-start gap-2">
            <span class="mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-accent text-[10px] font-bold text-white">1</span>
            <div>
              <p class="text-sm font-semibold capitalize text-text">{{ analysis.lead_recommendation.pokemon }}</p>
              <p class="mt-0.5 text-xs text-muted">{{ analysis.lead_recommendation.reason }}</p>
            </div>
          </div>
        </div>

        <!-- Team strengths -->
        <div class="p-4">
          <p class="mb-2 font-mono text-[10px] uppercase tracking-widest text-muted">Team Strengths</p>
          <ul class="space-y-1">
            <li
              v-for="(s, i) in analysis.team_strengths"
              :key="i"
              class="flex items-start gap-1.5 text-xs text-text"
            >
              <span class="mt-0.5 h-1.5 w-1.5 shrink-0 rounded-full bg-green-500" />
              {{ s }}
            </li>
          </ul>
        </div>

        <!-- Team weaknesses -->
        <div class="p-4">
          <p class="mb-2 font-mono text-[10px] uppercase tracking-widest text-muted">Team Weaknesses</p>
          <ul class="space-y-1">
            <li
              v-for="(w, i) in analysis.team_weaknesses"
              :key="i"
              class="flex items-start gap-1.5 text-xs text-text"
            >
              <span class="mt-0.5 h-1.5 w-1.5 shrink-0 rounded-full bg-red-400" />
              {{ w }}
            </li>
          </ul>
        </div>
      </div>

      <!-- ── Head-to-Head matrix ───────────────────────────────────────────── -->
      <div class="p-3 sm:p-5">
        <div class="mb-3 flex flex-wrap items-center gap-x-4 gap-y-1.5">
          <div class="flex items-center gap-1.5">
            <span class="h-2 w-2 rounded-full bg-sky-500" />
            <span class="font-mono text-[10px] font-semibold uppercase tracking-widest text-sky-700">My Team</span>
          </div>
          <span class="font-mono text-[10px] text-muted">→ rows</span>
          <div class="flex items-center gap-1.5">
            <span class="h-2 w-2 rounded-full bg-amber-500" />
            <span class="font-mono text-[10px] font-semibold uppercase tracking-widest text-amber-700">Opponent</span>
          </div>
          <span class="font-mono text-[10px] text-muted">→ columns</span>
        </div>
        <div class="analysis-matrix-scroll overflow-x-auto">
          <div :style="gridStyle" class="grid gap-1 mb-1">

            <!-- Top-left spacer -->
            <div class="analysis-sticky-col" />

            <!-- Column headers: opponent Pokémon -->
            <div
              v-for="opp in oppTeam"
              :key="opp.id"
              class="flex flex-col items-center gap-0.5 px-1"
            >
              <img :src="pokemonSprite(opp)" :alt="opp.name" class="h-8 w-8 object-contain" />
              <span class="w-full truncate text-center font-mono text-[9px] capitalize leading-tight text-amber-600">{{ opp.name }}</span>
            </div>

            <!-- Rows: my Pokémon -->
            <template v-for="mine in myTeam" :key="mine.id">
              <!-- Row header -->
              <div class="analysis-sticky-col flex items-center gap-1.5 pr-2">
                <img :src="pokemonSprite(mine)" :alt="mine.name" class="h-8 w-8 shrink-0 object-contain" />
                <span class="min-w-0 truncate font-mono text-[9px] capitalize leading-tight text-sky-700">{{ mine.name }}</span>
              </div>

              <!-- Cells -->
              <button
                v-for="opp in oppTeam"
                :key="opp.id"
                :class="[
                  'flex flex-col items-center justify-center rounded-lg border py-1.5 transition',
                  cellClass(mine.name, opp.name),
                  selectedCell?.my === mine.name && selectedCell?.opp === opp.name
                    ? 'ring-2 ring-accent ring-offset-1'
                    : 'hover:ring-1 hover:ring-accent/40 hover:ring-offset-1'
                ]"
                @click="toggleCell(mine.name, opp.name)"
              >
                <span class="font-mono text-sm font-bold leading-none">{{ cellLabel(mine.name, opp.name) }}</span>
                <span class="mt-0.5 font-mono text-[8px] leading-none opacity-60">{{ cellConf(mine.name, opp.name) }}</span>
              </button>
            </template>
          </div>
        </div>

        <!-- Detail panel -->
        <Transition name="slide-down">
          <div
            v-if="selectedMatchup"
            class="mt-3 overflow-hidden rounded-xl border border-accent/20 bg-accent/5"
          >
            <!-- Header row -->
            <div class="flex flex-wrap items-center gap-2 border-b border-accent/10 px-4 py-2.5">
              <span class="font-mono text-xs font-semibold capitalize text-sky-700">{{ selectedMatchup.my_pokemon }}</span>
              <span class="font-mono text-[10px] text-muted">vs</span>
              <span class="font-mono text-xs font-semibold capitalize text-amber-700">{{ selectedMatchup.opponent_pokemon }}</span>
              <RouterLink
                v-if="idFor(selectedMatchup.my_pokemon, myTeam) && idFor(selectedMatchup.opponent_pokemon, oppTeam)"
                :to="`/compare?a=${idFor(selectedMatchup.my_pokemon, myTeam)}&b=${idFor(selectedMatchup.opponent_pokemon, oppTeam)}`"
                title="Open 1v1 comparison"
                class="rounded-md p-0.5 text-muted transition hover:bg-accent/10 hover:text-accent"
              >
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="h-3.5 w-3.5" aria-hidden="true">
                  <path d="m16 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z"/>
                  <path d="m2 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z"/>
                  <path d="M7 21h10"/>
                  <path d="M12 3v18"/>
                  <path d="M3 7h2c2 0 5-1 7-2 2 1 5 2 7 2h2"/>
                </svg>
              </RouterLink>
              <div class="ml-auto flex items-center gap-1.5">
                <span class="font-mono text-[9px] opacity-60">{{ cellConf(selectedMatchup.my_pokemon, selectedMatchup.opponent_pokemon) }}</span>
                <span
                  :class="[
                    'rounded-full px-2 py-0.5 font-mono text-[10px] font-bold',
                    selectedMatchup.outcome === 'win'  ? 'bg-green-100 text-green-800' :
                    selectedMatchup.outcome === 'lose' ? 'bg-red-100 text-red-700'    : 'bg-gray-100 text-gray-600'
                  ]"
                >{{ selectedMatchup.outcome.toUpperCase() }}</span>
              </div>
            </div>

            <!-- Schematic rows -->
            <div class="divide-y divide-accent/8">

              <!-- Speed -->
              <div v-if="selectedMatchup.speed_note" class="flex flex-col gap-1.5 px-4 py-2 sm:flex-row sm:items-start sm:gap-3">
                <span class="shrink-0 font-mono text-[9px] font-semibold uppercase tracking-wide text-muted sm:w-14 sm:pt-0.5">Speed</span>
                <div class="space-y-0.5">
                  <span class="block font-mono text-[11px] text-text">{{ selectedMatchup.speed_note }}</span>
                  <span
                    v-if="speedOvertakeNote(selectedMatchup.my_pokemon, selectedMatchup.opponent_pokemon)"
                    class="block font-mono text-[10px] text-muted/70"
                  >{{ speedOvertakeNote(selectedMatchup.my_pokemon, selectedMatchup.opponent_pokemon) }}</span>
                </div>
              </div>

              <!-- Key moves -->
              <div v-if="selectedMatchup.key_moves.length > 0" class="flex flex-col gap-1.5 px-4 py-2 sm:flex-row sm:items-start sm:gap-3">
                <span class="shrink-0 font-mono text-[9px] font-semibold uppercase tracking-wide text-muted sm:w-14 sm:pt-0.5">Use</span>
                <div class="flex flex-wrap gap-1">
                  <span
                    v-for="m in selectedMatchup.key_moves"
                    :key="typeof m === 'string' ? m : m.name"
                    class="flex items-center gap-1 rounded border border-sky-200 bg-sky-50 px-2 py-0.5 font-mono text-[10px] font-medium capitalize text-sky-700"
                  >
                    {{ typeof m === 'string' ? m : m.name }}
                    <span
                      v-if="typeof m !== 'string' && sourceLabel(m.source)"
                      class="rounded bg-sky-200/60 px-1 py-px font-mono text-[8px] font-bold uppercase not-italic text-sky-600"
                    >{{ sourceLabel(m.source) }}</span>
                  </span>
                </div>
              </div>

              <!-- Threats / abilities -->
              <div v-if="selectedMatchup.threats_to_watch.length > 0" class="flex flex-col gap-1.5 px-4 py-2 sm:flex-row sm:items-start sm:gap-3">
                <span class="shrink-0 font-mono text-[9px] font-semibold uppercase tracking-wide text-muted sm:w-14 sm:pt-0.5">Watch</span>
                <div class="flex flex-wrap gap-1">
                  <span
                    v-for="t in selectedMatchup.threats_to_watch"
                    :key="t"
                    class="rounded border border-amber-200 bg-amber-50 px-2 py-0.5 font-mono text-[10px] font-medium text-amber-700"
                  >{{ t }}</span>
                </div>
              </div>

              <!-- Reasoning note -->
              <div v-if="selectedMatchup.reasoning" class="flex flex-col gap-1.5 px-4 py-2 sm:flex-row sm:items-start sm:gap-3">
                <span class="shrink-0 font-mono text-[9px] font-semibold uppercase tracking-wide text-muted sm:w-14 sm:pt-0.5">Note</span>
                <p class="text-[11px] leading-snug text-text/80">{{ selectedMatchup.reasoning }}</p>
              </div>
            </div>
          </div>
        </Transition>
        <p class="mt-2 text-center font-mono text-[9px] text-muted/60">Click a cell to see details · W = win · L = lose · ≈ = neutral</p>
      </div>

      <!-- ── Key threats ────────────────────────────────────────────────────── -->
      <div v-if="analysis.key_threats.length > 0" class="p-4 sm:p-5">
        <p class="mb-3 font-mono text-[10px] uppercase tracking-widest text-muted">Key Threats</p>
        <div class="grid grid-cols-1 gap-2 sm:grid-cols-2 lg:grid-cols-3">
          <div
            v-for="threat in analysis.key_threats"
            :key="threat.opponent_pokemon"
            :class="[
              'rounded-xl border p-3',
              threat.threat_level === 'high'   ? 'border-red-200 bg-red-50'    :
              threat.threat_level === 'medium' ? 'border-amber-200 bg-amber-50' : 'border-gray-200 bg-gray-50'
            ]"
          >
            <div class="mb-1 flex items-center gap-2">
              <span
                :class="[
                  'rounded-full px-2 py-0.5 text-[10px] font-bold uppercase',
                  threat.threat_level === 'high'   ? 'bg-red-500 text-white'    :
                  threat.threat_level === 'medium' ? 'bg-amber-500 text-white'  : 'bg-gray-400 text-white'
                ]"
              >{{ threat.threat_level }}</span>
              <span class="font-semibold capitalize text-amber-700">{{ threat.opponent_pokemon }}</span>
            </div>
            <p class="text-xs text-muted">
              Counter with <span class="font-semibold capitalize text-sky-700">{{ threat.best_counter }}</span>:
              {{ threat.counter_strategy }}
            </p>
          </div>
        </div>
      </div>

      <!-- ── Game Plan ─────────────────────────────────────────────────────── -->
      <div class="p-4 sm:p-5">
        <p class="mb-3 font-mono text-[10px] uppercase tracking-widest text-muted">Game Plan</p>
        <div class="grid grid-cols-1 gap-3 sm:grid-cols-3">
          <div
            v-for="(phase, label) in phases"
            :key="label"
            class="rounded-xl border border-black/8 bg-white/60 p-3"
          >
            <p class="mb-1 font-mono text-[10px] font-bold uppercase tracking-wide text-accent">{{ label }}</p>
            <p class="text-xs text-text">{{ phase }}</p>
          </div>
        </div>
      </div>

      <!-- ── Switch Advice ─────────────────────────────────────────────────── -->
      <div v-if="analysis.switch_advice.length > 0" class="p-4 sm:p-5">
        <p class="mb-3 font-mono text-[10px] uppercase tracking-widest text-muted">Switch Guide</p>
        <div class="space-y-1.5">
          <div
            v-for="sw in analysis.switch_advice"
            :key="sw.opponent_pokemon"
            class="flex flex-wrap items-center gap-3 rounded-xl border border-black/8 bg-white/60 px-3 py-2 sm:flex-nowrap"
          >
            <!-- Opponent -->
            <div class="flex w-24 shrink-0 items-center gap-1.5 sm:w-28">
              <img
                v-if="spriteFor(sw.opponent_pokemon, oppTeam)"
                :src="spriteFor(sw.opponent_pokemon, oppTeam)"
                :alt="sw.opponent_pokemon"
                class="h-7 w-7 shrink-0 object-contain"
              />
              <span class="min-w-0 truncate font-mono text-[10px] font-semibold capitalize text-amber-700">{{ sw.opponent_pokemon }}</span>
            </div>

            <!-- Arrow -->
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="h-3.5 w-3.5 shrink-0 text-muted/50" aria-hidden="true">
              <path d="M5 12h14M12 5l7 7-7 7"/>
            </svg>

            <!-- My switch-in -->
            <div class="flex w-24 shrink-0 items-center gap-1.5 sm:w-28">
              <img
                v-if="spriteFor(sw.switch_to, myTeam)"
                :src="spriteFor(sw.switch_to, myTeam)"
                :alt="sw.switch_to"
                class="h-7 w-7 shrink-0 object-contain"
              />
              <span class="min-w-0 truncate font-mono text-[10px] font-semibold capitalize text-sky-700">{{ sw.switch_to }}</span>
            </div>

            <!-- Reason -->
            <p class="min-w-0 basis-full text-[11px] leading-snug text-muted sm:flex-1 sm:basis-auto">{{ sw.reason }}</p>
          </div>
        </div>
      </div>

    </div>
  </article>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import { RouterLink } from "vue-router";
import type { Pokemon } from "@/types";
import type { MatchupAnalysis, IndividualMatchup, KeyMove } from "@/services/analysis";

const props = defineProps<{
  analysis: MatchupAnalysis;
  myTeam: Pokemon[];
  oppTeam: Pokemon[];
}>();

// ── Grid layout ───────────────────────────────────────────────────────────────

const gridStyle = computed(() => ({
  gridTemplateColumns: `var(--analysis-matrix-label, 128px) repeat(${props.oppTeam.length}, var(--analysis-matrix-cell, 72px))`,
}));

// ── Matchup lookup ────────────────────────────────────────────────────────────

const matchupMap = computed(() => {
  const map = new Map<string, IndividualMatchup>();
  for (const m of props.analysis.individual_matchups) {
    map.set(`${m.my_pokemon}|${m.opponent_pokemon}`, m);
  }
  return map;
});

function getMatchup(myName: string, oppName: string): IndividualMatchup | undefined {
  return matchupMap.value.get(`${myName}|${oppName}`);
}

function cellClass(myName: string, oppName: string): string {
  const m = getMatchup(myName, oppName);
  if (!m) return "border-gray-100 bg-gray-50 text-gray-400";
  const c = m.confidence;
  if (m.outcome === "win") {
    if (c === "high")   return "border-green-300 bg-green-100 text-green-800";
    if (c === "medium") return "border-green-200 bg-green-50 text-green-700";
    return "border-green-100 bg-green-50/50 text-green-600";
  }
  if (m.outcome === "lose") {
    if (c === "high")   return "border-red-300 bg-red-100 text-red-800";
    if (c === "medium") return "border-red-200 bg-red-50 text-red-700";
    return "border-red-100 bg-red-50/50 text-red-600";
  }
  return "border-gray-200 bg-gray-50 text-gray-500";
}

function cellLabel(myName: string, oppName: string): string {
  const m = getMatchup(myName, oppName);
  if (!m) return "?";
  if (m.outcome === "win")  return "W";
  if (m.outcome === "lose") return "L";
  return "≈";
}

function cellConf(myName: string, oppName: string): string {
  const m = getMatchup(myName, oppName);
  if (!m) return "";
  if (m.confidence === "high")   return "●●●";
  if (m.confidence === "medium") return "●●○";
  return "●○○";
}

// ── Cell selection ────────────────────────────────────────────────────────────

const selectedCell = ref<{ my: string; opp: string } | null>(null);

const selectedMatchup = computed(() =>
  selectedCell.value
    ? getMatchup(selectedCell.value.my, selectedCell.value.opp)
    : undefined
);

function toggleCell(myName: string, oppName: string) {
  if (selectedCell.value?.my === myName && selectedCell.value?.opp === oppName) {
    selectedCell.value = null;
  } else {
    selectedCell.value = { my: myName, opp: oppName };
  }
}

// ── Helpers ───────────────────────────────────────────────────────────────────

const phases = computed(() => ({
  "Early Game": props.analysis.strategy.early_game,
  "Mid Game":   props.analysis.strategy.mid_game,
  "Late Game":  props.analysis.strategy.late_game,
}));

function pokemonSprite(p: Pokemon): string {
  return p.sprites?.official_artwork ?? p.sprites?.front_default ?? "";
}

function spriteFor(name: string, team: Pokemon[]): string {
  const p = team.find(t => t.name.toLowerCase() === name.toLowerCase());
  return p ? pokemonSprite(p) : "";
}

function idFor(name: string, team: Pokemon[]): number | null {
  return team.find(t => t.name.toLowerCase() === name.toLowerCase())?.id ?? null;
}

// Returns minimum positive speed stages needed for the slower Pokémon to overtake the faster one.
// Uses Gen 5 stage multipliers: +n → (2+n)/2. Same number also applies for the faster one to drop -n.
function stagesNeeded(slowerSpeed: number, fasterSpeed: number): number | null {
  for (let n = 1; n <= 6; n++) {
    if (slowerSpeed * (2 + n) > fasterSpeed * 2) return n;
  }
  return null;
}

function speedOvertakeNote(myName: string, oppName: string): string | null {
  const mine = props.myTeam.find(p => p.name.toLowerCase() === myName.toLowerCase());
  const opp  = props.oppTeam.find(p => p.name.toLowerCase() === oppName.toLowerCase());
  if (!mine || !opp) return null;

  // Neutral nature, 252 EVs, level 50 (matches speed_lv50.neutral_nature in the prompt)
  const mySpd  = (mine.stats["speed"]  ?? 0) + 52;
  const oppSpd = (opp.stats["speed"]   ?? 0) + 52;

  if (mySpd === oppSpd) return null;

  const cap = (s: string) => s.charAt(0).toUpperCase() + s.slice(1);
  const [fasterSpd, slowerSpd, slowerName] =
    mySpd > oppSpd
      ? [mySpd,  oppSpd, cap(opp.name)]
      : [oppSpd, mySpd,  cap(mine.name)];

  const n = stagesNeeded(slowerSpd, fasterSpd);
  if (n === null) return `${slowerName} cannot overtake even at +6 Speed`;
  return `${slowerName} needs +${n} Speed stage${n === 1 ? "" : "s"} to overtake`;
}

function sourceLabel(source: KeyMove["source"]): string {
  if (source === "level-up")     return "Lv";
  if (source === "TM")           return "MT";
  if (source === "level-up+TM")  return "Lv/MT";
  if (source === "tutor")        return "Tutor";
  return "";
}
</script>

<style scoped>
.slide-down-enter-active,
.slide-down-leave-active {
  transition: all 0.2s ease;
}
.slide-down-enter-from,
.slide-down-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}

@media (max-width: 640px) {
  .analysis-matrix-scroll {
    --analysis-matrix-label: 96px;
    --analysis-matrix-cell: 50px;
    margin-inline: -0.25rem;
    padding-inline: 0.25rem;
  }

  .analysis-sticky-col {
    position: sticky;
    left: 0;
    z-index: 1;
    min-width: 0;
    background: rgba(248, 253, 255, 0.96);
    box-shadow: 8px 0 12px -12px rgba(18, 48, 61, 0.35);
  }
}
</style>
