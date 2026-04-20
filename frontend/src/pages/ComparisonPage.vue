<template>
  <div class="mx-auto max-w-5xl space-y-5 px-4 py-6">
    <!-- Page header -->
    <header class="space-y-1">
      <p class="font-mono text-xs uppercase tracking-widest text-accent">{{ t("compare.eyebrow") }}</p>
      <h1 class="font-display text-3xl font-bold text-text">{{ t("compare.title") }}</h1>
      <p class="text-sm text-muted">{{ t("compare.subtitle") }}</p>
    </header>

    <!-- Pokemon selectors -->
    <div class="relative z-10 grid grid-cols-1 items-center gap-3 md:grid-cols-[1fr_56px_1fr]">
      <!-- ── Picker A ── -->
      <div class="card-surface min-h-[88px] rounded-2xl p-4">
        <!-- Loading -->
        <div v-if="idA && pokemonAQuery.isPending.value" class="flex animate-pulse items-center gap-3">
          <div class="h-14 w-14 shrink-0 rounded-xl bg-black/10" />
          <div class="flex-1 space-y-2">
            <div class="h-3 w-20 rounded bg-black/10" />
            <div class="h-4 w-28 rounded bg-black/10" />
          </div>
        </div>
        <!-- Selected display -->
        <div v-else-if="pokemonA && !isEditingA" class="flex items-center gap-3">
          <RouterLink :to="`/pokemon/${pokemonA.id}`" class="group flex min-w-0 flex-1 items-center gap-3">
            <div class="flex h-14 w-14 shrink-0 items-center justify-center rounded-xl border border-black/10 bg-white/80 p-1 transition group-hover:border-accent/30">
              <img v-if="spriteA" :src="spriteA" :alt="pokemonA.name" class="h-full w-full object-contain transition group-hover:scale-105" />
              <div v-else class="h-10 w-10 rounded bg-black/5" />
            </div>
            <div class="min-w-0">
              <p class="font-mono text-xs text-muted">#{{ formatId(pokemonA.id) }}</p>
              <h3 class="truncate font-display text-base font-semibold capitalize text-text transition group-hover:text-accent">{{ pokemonA.name }}</h3>
              <div class="mt-0.5 flex flex-wrap gap-1">
                <span
                  v-for="type in pokemonA.types"
                  :key="type"
                  :style="getTypeChipStyle(type)"
                  class="rounded-full border px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide"
                >{{ labelType(type) }}</span>
              </div>
            </div>
          </RouterLink>
          <button
            class="ml-auto shrink-0 rounded-full bg-accent/10 px-3 py-1 text-xs font-medium text-accent transition hover:bg-accent/20"
            @click="startEditA"
          >
            {{ t("compare.change") }}
          </button>
        </div>
        <!-- Search -->
        <div v-else class="space-y-2">
          <p class="text-[10px] font-semibold uppercase tracking-widest text-muted">{{ t("compare.pick_pokemon") }}</p>
          <div class="relative">
            <input
              ref="inputRefA"
              v-model="searchA"
              type="text"
              :placeholder="t('compare.search_placeholder')"
              class="w-full rounded-xl border border-accent/20 bg-white/80 px-3 py-2 text-sm text-text outline-none placeholder:text-muted/50 focus:border-accent/50 focus:ring-1 focus:ring-accent/20"
              @focus="showDropA = true"
              @blur="onBlurA"
            />
            <div
              v-if="showDropA && searchResultsA.length > 0"
              class="absolute left-0 right-0 top-full z-50 mt-1 max-h-56 overflow-y-auto rounded-xl border border-accent/15 bg-white shadow-lg"
            >
              <button
                v-for="p in searchResultsA"
                :key="p.id"
                class="flex w-full items-center gap-2 px-3 py-2 text-left transition hover:bg-accent/10"
                @mousedown.prevent="selectA(p)"
              >
                <img v-if="p.sprite" :src="p.sprite" :alt="p.name" class="h-8 w-8 shrink-0 object-contain" />
                <div v-else class="h-8 w-8 shrink-0 rounded bg-black/5" />
                <span class="shrink-0 font-mono text-xs text-muted">#{{ formatId(p.id) }}</span>
                <span class="min-w-0 truncate text-sm font-medium capitalize">{{ p.name }}</span>
                <div class="ml-auto flex shrink-0 gap-1">
                  <span
                    v-for="type in p.types"
                    :key="type"
                    :style="getTypeChipStyle(type)"
                    class="rounded-full border px-1.5 py-0.5 text-[10px] font-semibold uppercase"
                  >{{ labelType(type) }}</span>
                </div>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- VS badge + swap -->
      <div class="flex flex-col items-center justify-center gap-1.5">
        <span class="select-none rounded-full bg-sun/25 px-3 py-1.5 font-display text-base font-bold text-text shadow-soft">VS</span>
        <button
          class="rounded-full p-1 text-muted transition hover:bg-black/8 hover:text-text"
          :title="t('compare.swap')"
          @click="swapPokemon"
        >
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="h-4 w-4" aria-hidden="true">
            <path d="M8 3 4 7l4 4"/>
            <path d="M4 7h16"/>
            <path d="m16 21 4-4-4-4"/>
            <path d="M20 17H4"/>
          </svg>
        </button>
      </div>

      <!-- ── Picker B ── -->
      <div class="card-surface min-h-[88px] rounded-2xl p-4">
        <!-- Loading -->
        <div v-if="idB && pokemonBQuery.isPending.value" class="flex animate-pulse items-center gap-3">
          <div class="h-14 w-14 shrink-0 rounded-xl bg-black/10" />
          <div class="flex-1 space-y-2">
            <div class="h-3 w-20 rounded bg-black/10" />
            <div class="h-4 w-28 rounded bg-black/10" />
          </div>
        </div>
        <!-- Selected display -->
        <div v-else-if="pokemonB && !isEditingB" class="flex items-center gap-3">
          <RouterLink :to="`/pokemon/${pokemonB.id}`" class="group flex min-w-0 flex-1 items-center gap-3">
            <div class="flex h-14 w-14 shrink-0 items-center justify-center rounded-xl border border-black/10 bg-white/80 p-1 transition group-hover:border-accent/30">
              <img v-if="spriteB" :src="spriteB" :alt="pokemonB.name" class="h-full w-full object-contain transition group-hover:scale-105" />
              <div v-else class="h-10 w-10 rounded bg-black/5" />
            </div>
            <div class="min-w-0">
              <p class="font-mono text-xs text-muted">#{{ formatId(pokemonB.id) }}</p>
              <h3 class="truncate font-display text-base font-semibold capitalize text-text transition group-hover:text-accent">{{ pokemonB.name }}</h3>
              <div class="mt-0.5 flex flex-wrap gap-1">
                <span
                  v-for="type in pokemonB.types"
                  :key="type"
                  :style="getTypeChipStyle(type)"
                  class="rounded-full border px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide"
                >{{ labelType(type) }}</span>
              </div>
            </div>
          </RouterLink>
          <button
            class="ml-auto shrink-0 rounded-full bg-accent/10 px-3 py-1 text-xs font-medium text-accent transition hover:bg-accent/20"
            @click="startEditB"
          >
            {{ t("compare.change") }}
          </button>
        </div>
        <!-- Search -->
        <div v-else class="space-y-2">
          <p class="text-[10px] font-semibold uppercase tracking-widest text-muted">{{ t("compare.pick_pokemon") }}</p>
          <div class="relative">
            <input
              ref="inputRefB"
              v-model="searchB"
              type="text"
              :placeholder="t('compare.search_placeholder')"
              class="w-full rounded-xl border border-accent/20 bg-white/80 px-3 py-2 text-sm text-text outline-none placeholder:text-muted/50 focus:border-accent/50 focus:ring-1 focus:ring-accent/20"
              @focus="showDropB = true"
              @blur="onBlurB"
            />
            <div
              v-if="showDropB && searchResultsB.length > 0"
              class="absolute left-0 right-0 top-full z-50 mt-1 max-h-56 overflow-y-auto rounded-xl border border-accent/15 bg-white shadow-lg"
            >
              <button
                v-for="p in searchResultsB"
                :key="p.id"
                class="flex w-full items-center gap-2 px-3 py-2 text-left transition hover:bg-accent/10"
                @mousedown.prevent="selectB(p)"
              >
                <img v-if="p.sprite" :src="p.sprite" :alt="p.name" class="h-8 w-8 shrink-0 object-contain" />
                <div v-else class="h-8 w-8 shrink-0 rounded bg-black/5" />
                <span class="shrink-0 font-mono text-xs text-muted">#{{ formatId(p.id) }}</span>
                <span class="min-w-0 truncate text-sm font-medium capitalize">{{ p.name }}</span>
                <div class="ml-auto flex shrink-0 gap-1">
                  <span
                    v-for="type in p.types"
                    :key="type"
                    :style="getTypeChipStyle(type)"
                    class="rounded-full border px-1.5 py-0.5 text-[10px] font-semibold uppercase"
                  >{{ labelType(type) }}</span>
                </div>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Placeholder -->
    <div v-if="!pokemonA || !pokemonB" class="card-surface rounded-2xl px-6 py-10 text-center text-sm text-muted">
      {{ t("compare.select_prompt") }}
    </div>

    <template v-else>
      <!-- ══ Section 1: Statistics ══ -->
      <article class="card-surface overflow-hidden rounded-2xl">
        <div class="border-b border-black/8 px-5 py-3.5">
          <h2 class="font-display font-semibold text-text">{{ t("compare.section.statistics") }}</h2>
        </div>
        <div class="p-5">
          <!-- Column headers -->
          <div class="mb-3 grid grid-cols-[1fr_48px_1fr] items-center gap-2">
            <p class="truncate text-right font-mono text-xs font-bold capitalize text-sky-600">{{ pokemonA.name }}</p>
            <div />
            <p class="truncate font-mono text-xs font-bold capitalize text-amber-600">{{ pokemonB.name }}</p>
          </div>

          <!-- Stat rows -->
          <div class="space-y-1.5">
            <div v-for="row in statRows" :key="row.stat" class="grid grid-cols-[1fr_48px_1fr] items-center gap-2">
              <!-- A: value + bar (right-to-left) -->
              <div class="flex items-center justify-end gap-2">
                <span :class="['w-8 text-right font-mono text-sm font-bold', row.aWins ? 'text-sky-600' : 'text-slate-300']">{{ row.a }}</span>
                <div class="h-2 flex-1 overflow-hidden rounded-full bg-black/8">
                  <div
                    class="ml-auto h-full rounded-full bg-sky-500 transition-all duration-300"
                    :style="{ width: statBarPct(row.a) + '%' }"
                  />
                </div>
              </div>
              <!-- Stat label -->
              <div class="text-center">
                <span class="font-mono text-[11px] font-bold uppercase text-muted">{{ labelStatShort(row.stat) }}</span>
              </div>
              <!-- B: bar + value (left-to-right) -->
              <div class="flex items-center gap-2">
                <div class="h-2 flex-1 overflow-hidden rounded-full bg-black/8">
                  <div
                    class="h-full rounded-full bg-amber-400 transition-all duration-300"
                    :style="{ width: statBarPct(row.b) + '%' }"
                  />
                </div>
                <span :class="['w-8 font-mono text-sm font-bold', row.bWins ? 'text-amber-600' : 'text-slate-300']">{{ row.b }}</span>
              </div>
            </div>
          </div>

          <!-- Offense vs Defense cross-comparison -->
          <div class="mt-5 space-y-2 border-t border-black/8 pt-4">
            <p class="mb-3 text-[10px] font-semibold uppercase tracking-widest text-muted">{{ t("compare.offense_vs_defense") }}</p>

            <!-- Physical: A.Atk → B.Def  |  B.Atk → A.Def -->
            <div class="grid grid-cols-[1fr_52px_1fr] items-center gap-2 text-xs sm:grid-cols-[1fr_80px_1fr] sm:gap-3">
              <div class="flex items-center justify-end gap-1.5">
                <span class="text-muted"><span class="hidden sm:inline">{{ labelStatShort("attack") }}&nbsp;</span>{{ physicalA.atk }}&nbsp;→&nbsp;<span class="hidden sm:inline">Def&nbsp;</span>{{ physicalA.def }}</span>
                <span :class="['rounded-full border px-1.5 py-0.5 text-[11px] font-bold', diffBadgeClass(physicalA.diff)]">{{ formatSignedDiff(physicalA.diff) }}</span>
              </div>
              <div class="text-center text-[10px] font-semibold uppercase tracking-wide text-muted">{{ t("compare.physical") }}</div>
              <div class="flex items-center gap-1.5">
                <span :class="['rounded-full border px-1.5 py-0.5 text-[11px] font-bold', diffBadgeClass(physicalB.diff)]">{{ formatSignedDiff(physicalB.diff) }}</span>
                <span class="text-muted"><span class="hidden sm:inline">{{ labelStatShort("attack") }}&nbsp;</span>{{ physicalB.atk }}&nbsp;→&nbsp;<span class="hidden sm:inline">Def&nbsp;</span>{{ physicalB.def }}</span>
              </div>
            </div>

            <!-- Special: A.SpA → B.SpD  |  B.SpA → A.SpD -->
            <div class="grid grid-cols-[1fr_52px_1fr] items-center gap-2 text-xs sm:grid-cols-[1fr_80px_1fr] sm:gap-3">
              <div class="flex items-center justify-end gap-1.5">
                <span class="text-muted"><span class="hidden sm:inline">{{ labelStatShort("special-attack") }}&nbsp;</span>{{ specialA.spa }}&nbsp;→&nbsp;<span class="hidden sm:inline">SpD&nbsp;</span>{{ specialA.spd }}</span>
                <span :class="['rounded-full border px-1.5 py-0.5 text-[11px] font-bold', diffBadgeClass(specialA.diff)]">{{ formatSignedDiff(specialA.diff) }}</span>
              </div>
              <div class="text-center text-[10px] font-semibold uppercase tracking-wide text-muted">{{ t("compare.special") }}</div>
              <div class="flex items-center gap-1.5">
                <span :class="['rounded-full border px-1.5 py-0.5 text-[11px] font-bold', diffBadgeClass(specialB.diff)]">{{ formatSignedDiff(specialB.diff) }}</span>
                <span class="text-muted"><span class="hidden sm:inline">{{ labelStatShort("special-attack") }}&nbsp;</span>{{ specialB.spa }}&nbsp;→&nbsp;<span class="hidden sm:inline">SpD&nbsp;</span>{{ specialB.spd }}</span>
              </div>
            </div>
          </div>
        </div>
      </article>

      <!-- ══ Section 2: STAB vs Type ══ -->
      <article class="card-surface overflow-hidden rounded-2xl">
        <div class="border-b border-black/8 px-5 py-3.5">
          <h2 class="font-display font-semibold text-text">{{ t("compare.section.type_matchup") }}</h2>
        </div>
        <div class="grid grid-cols-1 divide-y divide-black/8 md:grid-cols-2 md:divide-x md:divide-y-0">
          <!-- A STAB vs B -->
          <div class="space-y-3 p-5">
            <p class="text-[11px] font-semibold uppercase tracking-widest text-muted">
              {{ t("compare.stab_vs", { name: capitalize(pokemonB.name) }) }}
            </p>
            <div class="space-y-2">
              <div v-for="entry in stabMatchupAvsB" :key="entry.type" class="flex items-center gap-2">
                <span
                  :style="getTypeChipStyle(entry.type)"
                  class="rounded-full border px-2.5 py-0.5 text-xs font-semibold uppercase tracking-wide"
                >{{ labelType(entry.type) }}</span>
                <span class="text-xs text-muted">→</span>
                <span :class="['rounded-full border px-2 py-0.5 text-xs font-bold', multiplierBadgeClass(entry.multiplier)]">{{ formatMultiplier(entry.multiplier) }}</span>
                <span v-if="entry.multiplier === 0" class="text-xs italic text-muted">{{ t("compare.immune") }}</span>
              </div>
            </div>
          </div>
          <!-- B STAB vs A -->
          <div class="space-y-3 p-5">
            <p class="text-[11px] font-semibold uppercase tracking-widest text-muted">
              {{ t("compare.stab_vs", { name: capitalize(pokemonA.name) }) }}
            </p>
            <div class="space-y-2">
              <div v-for="entry in stabMatchupBvsA" :key="entry.type" class="flex items-center gap-2">
                <span
                  :style="getTypeChipStyle(entry.type)"
                  class="rounded-full border px-2.5 py-0.5 text-xs font-semibold uppercase tracking-wide"
                >{{ labelType(entry.type) }}</span>
                <span class="text-xs text-muted">→</span>
                <span :class="['rounded-full border px-2 py-0.5 text-xs font-bold', multiplierBadgeClass(entry.multiplier)]">{{ formatMultiplier(entry.multiplier) }}</span>
                <span v-if="entry.multiplier === 0" class="text-xs italic text-muted">{{ t("compare.immune") }}</span>
              </div>
            </div>
          </div>
        </div>
      </article>

      <!-- ══ Section 3: Move Effectiveness ══ -->
      <article class="card-surface overflow-hidden rounded-2xl">
        <div class="border-b border-black/8 px-5 py-3.5">
          <h2 class="font-display font-semibold text-text">{{ t("compare.section.moves") }}</h2>
        </div>
        <div class="grid grid-cols-1 divide-y divide-black/8 md:grid-cols-2 md:divide-x md:divide-y-0">
          <!-- A moves vs B -->
          <div class="flex flex-col p-5">
            <p class="mb-3 text-[11px] font-semibold uppercase tracking-widest text-muted">
              {{ t("compare.moves_vs", { name: capitalize(pokemonB.name) }) }}
            </p>
            <p v-if="movesAQuery.isPending.value" class="text-xs text-muted">{{ t("compare.loading_moves") }}</p>
            <p v-else-if="!damageMovesAvsB.length" class="text-xs text-muted">{{ t("compare.no_damage_moves") }}</p>
            <div v-else class="max-h-64 space-y-0.5 overflow-y-auto pr-1 md:max-h-96">
              <div
                v-for="move in damageMovesAvsB"
                :key="move.name"
                class="flex items-center gap-1.5 rounded-lg px-2 py-1.5 transition"
                :class="move.multiplier !== 1 ? 'hover:bg-black/5' : 'opacity-35'"
              >
                <span
                  v-if="move.type"
                  :style="getTypeChipStyle(move.type)"
                  class="shrink-0 rounded-full border px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide"
                >{{ labelType(move.type) }}</span>
                <RouterLink
                  :to="`/moves?move=${encodeURIComponent(move.name)}`"
                  class="min-w-0 flex-1 truncate text-xs capitalize text-text underline-offset-2 hover:underline"
                >{{ move.display_name ?? move.name }}</RouterLink>
                <div class="flex shrink-0 gap-0.5">
                  <span
                    v-for="(methodLabel, index) in getLearnMethodBadges(move.methods)"
                    :key="`${move.name}-a-${methodLabel}-${index}`"
                    class="rounded border border-black/10 bg-black/5 px-1 py-0.5 font-mono text-[9px] text-muted"
                  >{{ methodLabel }}</span>
                </div>
                <span
                  v-if="getMoveCategoryIcon(move.category)"
                  class="inline-flex h-5 w-5 shrink-0 items-center justify-center rounded border border-black/10 bg-white/90"
                  :title="labelMoveCategory(move.category)"
                >
                  <img
                    :src="getMoveCategoryIcon(move.category) ?? ''"
                    :alt="labelMoveCategory(move.category)"
                    class="h-[11px] w-auto"
                  />
                </span>
                <span class="w-7 shrink-0 text-right font-mono text-xs text-muted">{{ move.power }}</span>
                <span :class="['shrink-0 rounded-full border px-1.5 py-0.5 text-[11px] font-bold', multiplierBadgeClass(move.multiplier)]">{{ formatMultiplier(move.multiplier) }}</span>
              </div>
            </div>
          </div>
          <!-- B moves vs A -->
          <div class="flex flex-col p-5">
            <p class="mb-3 text-[11px] font-semibold uppercase tracking-widest text-muted">
              {{ t("compare.moves_vs", { name: capitalize(pokemonA.name) }) }}
            </p>
            <p v-if="movesBQuery.isPending.value" class="text-xs text-muted">{{ t("compare.loading_moves") }}</p>
            <p v-else-if="!damageMovesBvsA.length" class="text-xs text-muted">{{ t("compare.no_damage_moves") }}</p>
            <div v-else class="max-h-64 space-y-0.5 overflow-y-auto pr-1 md:max-h-96">
              <div
                v-for="move in damageMovesBvsA"
                :key="move.name"
                class="flex items-center gap-1.5 rounded-lg px-2 py-1.5 transition"
                :class="move.multiplier !== 1 ? 'hover:bg-black/5' : 'opacity-35'"
              >
                <span
                  v-if="move.type"
                  :style="getTypeChipStyle(move.type)"
                  class="shrink-0 rounded-full border px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide"
                >{{ labelType(move.type) }}</span>
                <RouterLink
                  :to="`/moves?move=${encodeURIComponent(move.name)}`"
                  class="min-w-0 flex-1 truncate text-xs capitalize text-text underline-offset-2 hover:underline"
                >{{ move.display_name ?? move.name }}</RouterLink>
                <div class="flex shrink-0 gap-0.5">
                  <span
                    v-for="(methodLabel, index) in getLearnMethodBadges(move.methods)"
                    :key="`${move.name}-b-${methodLabel}-${index}`"
                    class="rounded border border-black/10 bg-black/5 px-1 py-0.5 font-mono text-[9px] text-muted"
                  >{{ methodLabel }}</span>
                </div>
                <span
                  v-if="getMoveCategoryIcon(move.category)"
                  class="inline-flex h-5 w-5 shrink-0 items-center justify-center rounded border border-black/10 bg-white/90"
                  :title="labelMoveCategory(move.category)"
                >
                  <img
                    :src="getMoveCategoryIcon(move.category) ?? ''"
                    :alt="labelMoveCategory(move.category)"
                    class="h-[11px] w-auto"
                  />
                </span>
                <span class="w-7 shrink-0 text-right font-mono text-xs text-muted">{{ move.power }}</span>
                <span :class="['shrink-0 rounded-full border px-1.5 py-0.5 text-[11px] font-bold', multiplierBadgeClass(move.multiplier)]">{{ formatMultiplier(move.multiplier) }}</span>
              </div>
            </div>
          </div>
        </div>
      </article>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, ref } from "vue";
import { RouterLink, useRoute, useRouter } from "vue-router";
import { useQuery } from "@tanstack/vue-query";
import type { Pokemon, PokemonListItem, PokemonMove, MoveLearnMethod } from "@/types";
import { fetchPokemon, fetchPokemonList, fetchPokemonMoves } from "@/api/client";
import { t, labelType, labelStatShort, labelMoveCategory, labelLearnMethod, useLocale } from "@/i18n";
import { getTypeChipStyle } from "@/constants/pokemonTypes";
import { getAttackMultiplierForTypes } from "@/constants/typeEffectiveness";
import { useDebouncedValue } from "@/composables/useDebouncedValue";
import { formatLearnMethodLabels } from "@/utils/moveLearnMethods";

const route = useRoute();
const router = useRouter();
const { locale } = useLocale();

const STAT_ORDER = ["hp", "attack", "defense", "special-attack", "special-defense", "speed"];
const MAX_STAT = 200;
const MOVE_CATEGORY_ICONS: Record<string, string> = {
  physical: "/move-category/physical.png",
  special: "/move-category/special.png",
};

// ── URL-driven IDs ──────────────────────────────────────────────────────────
const idA = computed(() => {
  const v = Number(route.query.a);
  return Number.isFinite(v) && v > 0 ? v : null;
});
const idB = computed(() => {
  const v = Number(route.query.b);
  return Number.isFinite(v) && v > 0 ? v : null;
});

function setId(side: "a" | "b", id: number | null) {
  router.replace({ query: { ...route.query, [side]: id ?? undefined } });
}

function swapPokemon() {
  const tmpEdit = isEditingA.value;
  isEditingA.value = isEditingB.value;
  isEditingB.value = tmpEdit;
  router.replace({ query: { ...route.query, a: idB.value ?? undefined, b: idA.value ?? undefined } });
}

// ── Picker state ────────────────────────────────────────────────────────────
const searchA = ref("");
const searchB = ref("");
const debouncedA = useDebouncedValue(searchA, 250);
const debouncedB = useDebouncedValue(searchB, 250);
const showDropA = ref(false);
const showDropB = ref(false);
const isEditingA = ref(!route.query.a);
const isEditingB = ref(!route.query.b);
const inputRefA = ref<HTMLInputElement | null>(null);
const inputRefB = ref<HTMLInputElement | null>(null);

function selectA(p: PokemonListItem) {
  setId("a", p.id);
  searchA.value = "";
  showDropA.value = false;
  isEditingA.value = false;
}
function selectB(p: PokemonListItem) {
  setId("b", p.id);
  searchB.value = "";
  showDropB.value = false;
  isEditingB.value = false;
}
function startEditA() {
  isEditingA.value = true;
  nextTick(() => inputRefA.value?.focus());
}
function startEditB() {
  isEditingB.value = true;
  nextTick(() => inputRefB.value?.focus());
}
function onBlurA() {
  setTimeout(() => { showDropA.value = false; }, 150);
}
function onBlurB() {
  setTimeout(() => { showDropB.value = false; }, 150);
}

// ── Queries: search results ─────────────────────────────────────────────────
const searchQueryA = useQuery({
  queryKey: computed(() => ["pokemon-search", locale.value, debouncedA.value]),
  queryFn: () => fetchPokemonList({ q: debouncedA.value, limit: 8 }),
  enabled: computed(() => debouncedA.value.trim().length > 0),
});
const searchQueryB = useQuery({
  queryKey: computed(() => ["pokemon-search", locale.value, debouncedB.value]),
  queryFn: () => fetchPokemonList({ q: debouncedB.value, limit: 8 }),
  enabled: computed(() => debouncedB.value.trim().length > 0),
});

// ── Queries: selected Pokemon detail + moves ────────────────────────────────
const pokemonAQuery = useQuery({
  queryKey: computed(() => ["pokemon", locale.value, idA.value]),
  queryFn: () => fetchPokemon(idA.value!),
  enabled: computed(() => idA.value !== null),
});
const pokemonBQuery = useQuery({
  queryKey: computed(() => ["pokemon", locale.value, idB.value]),
  queryFn: () => fetchPokemon(idB.value!),
  enabled: computed(() => idB.value !== null),
});
const movesAQuery = useQuery({
  queryKey: computed(() => ["pokemon-moves", locale.value, idA.value]),
  queryFn: () => fetchPokemonMoves(idA.value!),
  enabled: computed(() => idA.value !== null),
});
const movesBQuery = useQuery({
  queryKey: computed(() => ["pokemon-moves", locale.value, idB.value]),
  queryFn: () => fetchPokemonMoves(idB.value!),
  enabled: computed(() => idB.value !== null),
});

// ── Extracted data ──────────────────────────────────────────────────────────
const pokemonA = computed(() => pokemonAQuery.data.value?.data ?? null);
const pokemonB = computed(() => pokemonBQuery.data.value?.data ?? null);
const movesA = computed(() => movesAQuery.data.value?.data ?? []);
const movesB = computed(() => movesBQuery.data.value?.data ?? []);
const searchResultsA = computed(() => searchQueryA.data.value?.data ?? []);
const searchResultsB = computed(() => searchQueryB.data.value?.data ?? []);
const spriteA = computed(
  () => pokemonA.value?.sprites?.official_artwork ?? pokemonA.value?.sprites?.front_default ?? null
);
const spriteB = computed(
  () => pokemonB.value?.sprites?.official_artwork ?? pokemonB.value?.sprites?.front_default ?? null
);

// ── Section 1: Statistics ───────────────────────────────────────────────────
function statVal(pokemon: Pokemon | null, stat: string): number {
  return pokemon?.stats?.[stat] ?? 0;
}

const statRows = computed(() => {
  if (!pokemonA.value || !pokemonB.value) return [];
  return STAT_ORDER.map((stat) => {
    const a = statVal(pokemonA.value, stat);
    const b = statVal(pokemonB.value, stat);
    return { stat, a, b, aWins: a > b, bWins: b > a };
  });
});

const physicalA = computed(() => {
  const atk = statVal(pokemonA.value, "attack");
  const def = statVal(pokemonB.value, "defense");
  return { atk, def, diff: atk - def };
});
const specialA = computed(() => {
  const spa = statVal(pokemonA.value, "special-attack");
  const spd = statVal(pokemonB.value, "special-defense");
  return { spa, spd, diff: spa - spd };
});
const physicalB = computed(() => {
  const atk = statVal(pokemonB.value, "attack");
  const def = statVal(pokemonA.value, "defense");
  return { atk, def, diff: atk - def };
});
const specialB = computed(() => {
  const spa = statVal(pokemonB.value, "special-attack");
  const spd = statVal(pokemonA.value, "special-defense");
  return { spa, spd, diff: spa - spd };
});

// ── Section 2: STAB matchup ─────────────────────────────────────────────────
const stabMatchupAvsB = computed(() => {
  if (!pokemonA.value || !pokemonB.value) return [];
  return pokemonA.value.types.map((type) => ({
    type,
    multiplier: getAttackMultiplierForTypes(type, pokemonB.value!.types),
  }));
});
const stabMatchupBvsA = computed(() => {
  if (!pokemonA.value || !pokemonB.value) return [];
  return pokemonB.value.types.map((type) => ({
    type,
    multiplier: getAttackMultiplierForTypes(type, pokemonA.value!.types),
  }));
});

// ── Section 3: Move effectiveness ──────────────────────────────────────────
type ScoredMove = PokemonMove & { multiplier: number };

const damageMovesAvsB = computed((): ScoredMove[] => {
  if (!pokemonB.value) return [];
  return movesA.value
    .filter((m) => m.power !== null && m.type !== null)
    .map((m) => ({ ...m, multiplier: getAttackMultiplierForTypes(m.type!, pokemonB.value!.types) }))
    .sort((a, b) => b.multiplier - a.multiplier || (b.power ?? 0) - (a.power ?? 0));
});
const damageMovesBvsA = computed((): ScoredMove[] => {
  if (!pokemonA.value) return [];
  return movesB.value
    .filter((m) => m.power !== null && m.type !== null)
    .map((m) => ({ ...m, multiplier: getAttackMultiplierForTypes(m.type!, pokemonA.value!.types) }))
    .sort((a, b) => b.multiplier - a.multiplier || (b.power ?? 0) - (a.power ?? 0));
});

// ── Helpers ─────────────────────────────────────────────────────────────────
function formatId(id: number): string {
  return String(id).padStart(3, "0");
}

function statBarPct(value: number): number {
  return Math.min(100, Math.round((value / MAX_STAT) * 100));
}

function formatMultiplier(mult: number): string {
  if (mult === 0) return "0×";
  if (Number.isInteger(mult)) return `${mult}×`;
  return `${mult.toFixed(2).replace(/0+$/, "").replace(/\.$/, "")}×`;
}

function formatSignedDiff(diff: number): string {
  if (diff > 0) return `+${diff}`;
  if (diff < 0) return String(diff);
  return "=";
}

function capitalize(s: string): string {
  return s ? s.charAt(0).toUpperCase() + s.slice(1) : s;
}

function multiplierBadgeClass(mult: number): string {
  if (mult === 0) return "border-gray-200 bg-gray-50 text-gray-400";
  if (mult >= 2) return "border-green-200 bg-green-50 text-green-700";
  if (mult <= 0.5) return "border-red-200 bg-red-50 text-red-500";
  return "border-black/10 bg-black/5 text-muted";
}

function getLearnMethodBadges(methods: MoveLearnMethod[]): string[] {
  return formatLearnMethodLabels(methods, labelLearnMethod, "Lv ");
}

function getMoveCategoryIcon(category: string | null): string | null {
  if (!category) return null;
  return MOVE_CATEGORY_ICONS[category.toLowerCase()] ?? null;
}

function diffBadgeClass(diff: number): string {
  if (diff > 0) return "border-green-200 bg-green-50 text-green-700";
  if (diff < 0) return "border-red-200 bg-red-50 text-red-600";
  return "border-black/10 bg-black/5 text-muted";
}
</script>
