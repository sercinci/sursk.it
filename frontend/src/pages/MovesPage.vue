<template>
  <section class="space-y-5">
    <div>
      <h1 class="font-display text-3xl font-bold">{{ t("moves.title") }}</h1>
    </div>

    <div class="space-y-2">
      <div class="flex flex-wrap items-center gap-2">
      <input
        v-model="query"
        type="search"
        :placeholder="t('moves.filter_placeholder')"
        class="w-full min-w-[220px] flex-1 rounded-xl border border-black/10 bg-white px-3 py-2 text-sm outline-none ring-accent/30 focus:ring"
      />

      <select
        v-model="selectedCategoryFilter"
        class="cursor-pointer rounded-xl border border-black/10 bg-white px-3 py-2 text-sm outline-none ring-accent/30 focus:ring"
      >
        <option value="">{{ t("moves.filter.all_categories") }}</option>
        <option
          v-for="categoryOption in moveCategoryOptions"
          :key="`moves-filter-category-${categoryOption}`"
          :value="categoryOption"
        >
          {{ labelMoveCategory(categoryOption) }}
        </option>
      </select>
      <button
        type="button"
        :title="t('filters.clear')"
        :aria-label="t('filters.clear')"
        class="inline-flex h-9 w-9 items-center justify-center rounded-full border border-black/10 bg-white text-lg font-semibold leading-none text-muted transition hover:border-black/20 hover:text-text disabled:cursor-not-allowed disabled:border-black/5 disabled:bg-black/5 disabled:text-slate-400 disabled:hover:border-black/5 disabled:hover:text-slate-400"
        :disabled="!hasActiveFilters"
        @click="resetFilters"
      >
        ×
      </button>
      </div>

      <div class="flex flex-wrap gap-1.5 rounded-xl border border-black/10 bg-white p-2">
        <button
          v-for="typeOption in moveTypeOptions"
          :key="`moves-chip-type-${typeOption}`"
          type="button"
          class="cursor-pointer rounded-full border px-2 py-0.5 text-xs font-semibold uppercase tracking-wide transition"
          :class="selectedTypeFilter === typeOption ? 'opacity-100 ring-1 ring-black/20' : 'opacity-35 hover:opacity-60'"
          :style="getTypeChipStyle(typeOption)"
          @click="toggleTypeFilter(typeOption)"
        >
          {{ labelType(typeOption) }}
        </button>
      </div>
    </div>

    <div class="card-surface overflow-hidden rounded-2xl">
      <div class="overflow-x-auto">
        <table class="min-w-[720px] w-full text-left text-sm">
          <thead class="bg-black/5 text-xs uppercase tracking-wide text-muted">
            <tr>
              <th class="px-4 py-3">{{ t("moves.column.move") }}</th>
              <th class="px-4 py-3">{{ t("moves.column.type") }}</th>
              <th class="px-4 py-3">{{ t("moves.column.category") }}</th>
              <th class="px-4 py-3">{{ t("moves.column.power") }}</th>
              <th class="px-4 py-3">{{ t("moves.column.pp") }}</th>
              <th class="px-4 py-3">{{ t("moves.column.accuracy") }}</th>
            </tr>
          </thead>
          <tbody>
            <template v-for="move in filtered" :key="move.name">
              <tr
                class="cursor-pointer border-t border-black/5 transition-colors hover:bg-black/[0.03]"
                @click="toggleExpanded(move.name)"
              >
                <td class="px-4 py-3 font-medium text-text">
                  <div class="flex items-center gap-2">
                    <span>{{ move.display_name ?? formatLabel(move.name) }}</span>
                    <span class="font-mono text-xs text-muted">{{ expandedMove === move.name ? "−" : "+" }}</span>
                  </div>
                </td>
                <td class="px-4 py-3">
                  <span
                    v-if="move.type"
                    class="inline-flex rounded-full border px-2 py-0.5 text-xs font-semibold uppercase tracking-wide"
                    :style="getTypeChipStyle(move.type)"
                  >
                    {{ labelType(move.type) }}
                  </span>
                  <span v-else class="text-muted">-</span>
                </td>
                <td class="px-4 py-3 text-muted">{{ labelMoveCategory(move.category) }}</td>
                <td class="px-4 py-3">{{ move.power ?? "-" }}</td>
                <td class="px-4 py-3">{{ move.pp ?? "-" }}</td>
                <td class="px-4 py-3">{{ move.accuracy ?? "-" }}</td>
              </tr>
              <tr v-if="expandedMove === move.name" class="border-t border-black/5 bg-black/[0.02]">
                <td colspan="6" class="px-4 py-4">
                  <p class="text-xs font-semibold uppercase tracking-wide text-muted">{{ t("moves.description") }}</p>
                  <p v-if="isMoveDetailLoading" class="mt-1 text-sm text-muted">{{ t("moves.loading_detail") }}</p>
                  <p v-else class="mt-1 text-sm leading-relaxed text-text">
                    {{ currentMoveDetail?.description ?? t("moves.no_description") }}
                  </p>

                  <div
                    v-if="currentMoveDetail?.tm_purchase"
                    class="mt-3 rounded-lg border border-black/10 bg-white px-3 py-2 text-sm"
                  >
                    <p class="text-xs font-semibold uppercase tracking-wide text-muted">{{ t("moves.tm_purchase") }}</p>
                    <p class="mt-1 text-text">
                      {{ formatTmPurchaseLocation(currentMoveDetail.tm_purchase) }}
                    </p>
                    <p
                      v-if="currentMoveDetail.tm_purchase.price_text || currentMoveDetail.tm_purchase.price_pokeyen !== null"
                      class="text-muted"
                    >
                      {{ t("moves.price") }}:
                      {{
                        currentMoveDetail.tm_purchase.price_text ??
                        formatPokeyen(currentMoveDetail.tm_purchase.price_pokeyen)
                      }}
                    </p>
                  </div>

                  <div v-if="isDamagingMove(move.category)" class="mt-3 text-sm">
                    <p class="text-xs font-semibold uppercase tracking-wide text-muted">{{ t("moves.effectiveness") }}</p>
                    <p v-if="!move.type" class="mt-1 text-sm text-muted">{{ t("moves.no_matchups") }}</p>
                    <p
                      v-else-if="!getMoveEffectivenessGroups(move.type).length"
                      class="mt-1 text-sm text-muted"
                    >
                      {{ t("moves.no_matchups") }}
                    </p>
                    <div v-else class="mt-2 flex flex-wrap gap-1.5">
                      <div
                        v-for="group in getMoveEffectivenessGroups(move.type)"
                        :key="`move-effectiveness-${move.name}-${group.multiplier}`"
                        class="inline-flex items-center gap-1.5 rounded-md border border-black/10 bg-white px-2 py-1"
                      >
                        <span class="font-mono text-[11px] font-semibold text-muted">
                          {{ formatDamageMultiplier(group.multiplier) }}
                        </span>
                        <div class="flex flex-wrap items-center gap-1">
                          <span
                            v-for="defendingType in group.types"
                            :key="`${move.name}-${group.multiplier}-${defendingType}`"
                            class="inline-flex rounded-full border px-1.5 py-0.5 text-[10px] font-semibold uppercase tracking-wide"
                            :style="getTypeChipStyle(defendingType)"
                          >
                            {{ labelType(defendingType) }}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div class="mt-4">
                    <p class="text-xs font-semibold uppercase tracking-wide text-muted">{{ t("moves.learners") }}</p>
                    <p v-if="isMoveDetailLoading" class="mt-1 text-sm text-muted">{{ t("moves.loading_learners") }}</p>
                    <p v-else-if="moveDetailErrorMessage" class="mt-1 text-sm text-red-600">{{ moveDetailErrorMessage }}</p>
                    <p v-else-if="!currentMoveDetail?.learners.length" class="mt-1 text-sm text-muted">
                      {{ t("moves.no_learners") }}
                    </p>
                    <ul
                      v-else
                      class="mt-2 grid max-h-96 grid-cols-1 gap-2 overflow-auto pr-1 md:grid-cols-2 xl:grid-cols-3"
                    >
                      <li
                        v-for="learner in currentMoveDetail.learners"
                        :key="learner.pokemon_id"
                        class="rounded-lg border border-black/10 bg-white"
                      >
                        <RouterLink
                          :to="`/pokemon/${learner.pokemon_id}`"
                          class="flex items-start gap-2 rounded-lg px-2.5 py-2 transition-colors hover:bg-black/[0.03]"
                        >
                          <img
                            :src="getLearnerSpriteUrl(learner)"
                            :alt="learner.pokemon_name"
                            class="h-9 w-9 shrink-0 rounded-md border border-black/10 bg-white object-contain"
                            loading="lazy"
                            @error="handleLearnerSpriteError($event, learner)"
                          />

                          <div class="min-w-0">
                            <p class="truncate text-sm font-semibold text-text">{{ formatLabel(learner.pokemon_name) }}</p>
                            <div class="mt-1 flex flex-wrap gap-1">
                              <span
                                v-for="method in learner.methods"
                                :key="`${learner.pokemon_id}-${method.method}-${method.level ?? 'na'}`"
                                class="rounded-md border border-black/10 bg-black/[0.03] px-2 py-0.5 text-xs font-semibold text-muted"
                              >
                                {{ formatLearnMethod(method) }}
                              </span>
                            </div>
                          </div>
                        </RouterLink>
                      </li>
                    </ul>
                  </div>
                </td>
              </tr>
            </template>
          </tbody>
        </table>
      </div>
    </div>

    <p v-if="errorMessage" class="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-600">
      {{ errorMessage }}
    </p>
  </section>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import { useQuery } from "@tanstack/vue-query";

import { fetchMoveDetail, fetchMoves } from "@/api/client";
import { getTypeChipStyle } from "@/constants/pokemonTypes";
import { getOffensiveDamageGroups } from "@/constants/typeEffectiveness";
import { labelLearnMethod, labelMoveCategory, labelType, t, useLocale } from "@/i18n";
import type { MoveTmPurchase } from "@/types";
import type { MoveLearnMethod, MoveLearner } from "@/types";

type DamageMultiplier = 2 | 0.5 | 0;

interface MoveEffectivenessGroup {
  multiplier: DamageMultiplier;
  types: string[];
}

const query = ref("");
const expandedMove = ref<string | null>(null);
const selectedTypeFilter = ref("");
const selectedCategoryFilter = ref("");
const { locale } = useLocale();
const DAMAGE_MULTIPLIERS: DamageMultiplier[] = [2, 0.5, 0];

const movesQuery = useQuery({
  queryKey: computed(() => ["moves", locale.value]),
  queryFn: fetchMoves
});

const moveDetailQuery = useQuery({
  queryKey: computed(() => ["move-detail", locale.value, expandedMove.value]),
  queryFn: () => fetchMoveDetail(expandedMove.value as string),
  enabled: computed(() => Boolean(expandedMove.value))
});

const filtered = computed(() => {
  const list = movesQuery.data.value?.data ?? [];
  const needle = normalizeQuery(query.value);

  return list.filter((move) => {
    if (selectedTypeFilter.value && move.type !== selectedTypeFilter.value) {
      return false;
    }
    if (selectedCategoryFilter.value && move.category !== selectedCategoryFilter.value) {
      return false;
    }
    if (!needle) {
      return true;
    }
    const display = normalizeQuery(move.display_name ?? move.name);
    const slug = normalizeQuery(move.name);
    return display.includes(needle) || slug.includes(needle);
  });
});

const hasActiveFilters = computed(
  () => Boolean(query.value.trim() || selectedTypeFilter.value || selectedCategoryFilter.value)
);

const moveTypeOptions = computed(() => {
  const values = new Set(
    (movesQuery.data.value?.data ?? [])
      .map((move) => move.type)
      .filter((value): value is string => Boolean(value))
  );
  return [...values].sort();
});

const moveCategoryOptions = computed(() => {
  const values = new Set(
    (movesQuery.data.value?.data ?? [])
      .map((move) => move.category)
      .filter((value): value is string => Boolean(value))
  );
  return [...values].sort();
});

const errorMessage = computed(() =>
  movesQuery.error.value instanceof Error ? movesQuery.error.value.message : ""
);

const currentMoveDetail = computed(() => moveDetailQuery.data.value?.data ?? null);

const moveDetailErrorMessage = computed(() =>
  moveDetailQuery.error.value instanceof Error ? moveDetailQuery.error.value.message : ""
);

const isMoveDetailLoading = computed(
  () => moveDetailQuery.isLoading.value || moveDetailQuery.isFetching.value
);

function toggleExpanded(moveName: string) {
  expandedMove.value = expandedMove.value === moveName ? null : moveName;
}

function toggleTypeFilter(type: string) {
  selectedTypeFilter.value = selectedTypeFilter.value === type ? "" : type;
}

function resetFilters() {
  query.value = "";
  selectedTypeFilter.value = "";
  selectedCategoryFilter.value = "";
}

function normalizeQuery(value: string) {
  return value.trim().toLowerCase().replaceAll("-", " ").replace(/\s+/g, " ");
}

function getMoveEffectivenessGroups(moveType: string): MoveEffectivenessGroup[] {
  const grouped = getOffensiveDamageGroups([moveType.toLowerCase()]);

  return DAMAGE_MULTIPLIERS.map((multiplier) => {
    const row = grouped.find((group) => group.multiplier === multiplier);
    return {
      multiplier,
      types: row ? row.entries.map((entry) => entry.type) : []
    };
  }).filter((group) => group.types.length > 0);
}

function formatDamageMultiplier(multiplier: DamageMultiplier) {
  return `${multiplier}x`;
}

function isDamagingMove(category: string | null) {
  return category === "physical" || category === "special";
}

function formatLabel(value: string | null) {
  if (!value) {
    return "-";
  }
  return value
    .split("-")
    .filter(Boolean)
    .map((segment) => segment.charAt(0).toUpperCase() + segment.slice(1))
    .join(" ");
}

function formatLearnMethod(method: MoveLearnMethod) {
  if (method.method === "level-up") {
    return method.level !== null ? `Lv ${method.level}` : labelLearnMethod(method.method);
  }
  return labelLearnMethod(method.method);
}

function getLearnerSpriteUrl(learner: MoveLearner) {
  return (
    learner.pokemon_sprite ??
    `https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/${learner.pokemon_id}.png`
  );
}

function handleLearnerSpriteError(event: Event, learner: MoveLearner) {
  const img = event.target as HTMLImageElement | null;
  if (!img) {
    return;
  }
  const fallback = `https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/${learner.pokemon_id}.png`;
  if (img.src !== fallback) {
    img.src = fallback;
  }
}

function formatPokeyen(value: number | null) {
  if (value === null) {
    return "-";
  }
  return `$${value.toLocaleString()}`;
}

function formatTmPurchaseLocation(tmPurchase: MoveTmPurchase) {
  const parts = [tmPurchase.location];
  const secondary = tmPurchase.secondary?.location;
  if (secondary) {
    parts.push(stripPriceSuffix(secondary));
  }
  return parts.join(", ");
}

function stripPriceSuffix(location: string) {
  return location
    .replace(/,?\s*(for|per)\s+\$[\d,]+$/i, "")
    .replace(/,?\s*(for|per)\s+[\d,]+\s+(coins|gettoni)$/i, "")
    .trim();
}
</script>
