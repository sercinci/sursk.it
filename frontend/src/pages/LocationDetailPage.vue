<template>
  <section class="space-y-6">
    <RouterLink
      to="/locations"
      class="inline-flex items-center gap-2 text-sm font-semibold text-muted transition hover:text-text"
    >
      <span aria-hidden="true">←</span>
      <span>{{ t("location_detail.back") }}</span>
    </RouterLink>

    <p v-if="isLoading" class="text-sm text-muted">{{ t("location_detail.loading") }}</p>

    <p
      v-else-if="errorMessage"
      class="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-600"
    >
      {{ errorMessage }}
    </p>

    <template v-else-if="locationDetail">
      <div>
        <p class="font-mono text-xs uppercase tracking-[0.18em] text-accent">{{ t("location_detail.region") }}</p>
        <h1 class="mt-1 font-display text-3xl font-bold">{{ locationDetail.display_name }}</h1>
        <p class="mt-1 text-sm text-muted">
          {{ t("location_detail.encounter_entries", { count: locationDetail.encounters.length }) }}
        </p>
      </div>

      <div class="grid gap-4 lg:grid-cols-2">
        <article class="card-surface overflow-hidden rounded-2xl">
          <div class="border-b border-black/10 px-4 py-3">
            <h2 class="font-display text-lg font-semibold">{{ t("location_detail.birdview") }}</h2>
          </div>
          <div
            class="space-y-4 p-4"
            :class="isBirdviewScrollable ? 'max-h-[70vh] overflow-y-auto pr-2' : ''"
          >
            <template v-if="birdviewImages.length">
              <article
                v-for="(image, index) in birdviewImages"
                :key="`${image.image_url}-${index}`"
                class="rounded-xl border border-black/10 bg-white/70 p-3"
              >
                <p v-if="image.label" class="mb-2 text-xs font-semibold text-muted">{{ image.label }}</p>
                <div class="relative min-h-[220px]">
                  <div
                    v-if="!isMediaLoaded(image.image_url)"
                    class="absolute inset-0 flex items-center justify-center rounded-lg border border-black/10 bg-black/5"
                  >
                    <div class="h-6 w-6 animate-spin rounded-full border-2 border-black/20 border-t-black/60" />
                  </div>
                  <img
                    :src="image.image_url"
                    :alt="image.label
                      ? t('location_detail.alt_birdview_labeled', { name: locationDetail.display_name, label: image.label })
                      : t('location_detail.alt_birdview', { name: locationDetail.display_name })"
                    class="max-h-[420px] w-full rounded-lg border border-black/10 bg-white object-contain transition-opacity duration-300"
                    :class="isMediaLoaded(image.image_url) ? 'opacity-100' : 'opacity-0'"
                    loading="lazy"
                    @load="markMediaLoaded(image.image_url)"
                    @error="markMediaLoaded(image.image_url)"
                  />
                </div>
                <a
                  v-if="image.source_url"
                  :href="image.source_url"
                  target="_blank"
                  rel="noreferrer"
                  class="mt-2 inline-block text-xs font-semibold text-muted underline-offset-2 hover:text-text hover:underline"
                >
                  {{ t("location_detail.birdview_source") }}
                </a>
              </article>
            </template>
            <p v-else class="text-sm text-muted">{{ t("location_detail.birdview_none") }}</p>
          </div>
        </article>

        <article class="card-surface overflow-hidden rounded-2xl">
          <div class="border-b border-black/10 px-4 py-3">
            <h2 class="font-display text-lg font-semibold">{{ t("location_detail.map") }}</h2>
          </div>
          <div class="p-4">
            <div v-if="locationDetail.map_image_url" class="relative min-h-[260px]">
              <div
                v-if="!isMediaLoaded(locationDetail.map_image_url)"
                class="absolute inset-0 flex items-center justify-center rounded-xl border border-black/10 bg-black/5"
              >
                <div class="h-7 w-7 animate-spin rounded-full border-2 border-black/20 border-t-black/60" />
              </div>
              <img
                :src="locationDetail.map_image_url"
                :alt="t('location_detail.alt_map', { name: locationDetail.display_name })"
                class="max-h-[460px] w-full rounded-xl border border-black/10 bg-white object-contain transition-opacity duration-300"
                :class="isMediaLoaded(locationDetail.map_image_url) ? 'opacity-100' : 'opacity-0'"
                loading="lazy"
                @load="markMediaLoaded(locationDetail.map_image_url)"
                @error="markMediaLoaded(locationDetail.map_image_url)"
              />
            </div>
            <p v-else class="text-sm text-muted">{{ t("location_detail.map_none") }}</p>
            <a
              v-if="locationDetail.map_source_url"
              :href="locationDetail.map_source_url"
              target="_blank"
              rel="noreferrer"
              class="mt-3 inline-block text-xs font-semibold text-muted underline-offset-2 hover:text-text hover:underline"
            >
              {{ t("location_detail.map_source") }}
            </a>
          </div>
        </article>
      </div>

      <a
        v-if="locationDetail.source_url"
        :href="locationDetail.source_url"
        target="_blank"
        rel="noreferrer"
        class="inline-block text-xs font-semibold text-muted underline-offset-2 hover:text-text hover:underline"
      >
        {{ t("location_detail.page") }}
      </a>

      <article class="card-surface overflow-hidden rounded-2xl">
        <div class="border-b border-black/10 px-4 py-3">
          <h2 class="font-display text-lg font-semibold">{{ t("location_detail.encounters") }}</h2>
        </div>
        <div class="overflow-x-auto">
          <table class="min-w-full text-sm">
            <thead class="bg-black/5 text-left font-semibold text-muted">
              <tr>
                <th class="px-4 py-2">
                  <button type="button" class="inline-flex items-center gap-1" @click="setSort('pokemon_name')">
                    {{ t("location_detail.column.pokemon") }}
                    <span class="font-mono text-xs">{{ sortIndicator('pokemon_name') }}</span>
                  </button>
                </th>
                <th class="px-4 py-2">
                  <button type="button" class="inline-flex items-center gap-1" @click="setSort('sub_location')">
                    {{ t("location_detail.column.sub_area") }}
                    <span class="font-mono text-xs">{{ sortIndicator('sub_location') }}</span>
                  </button>
                </th>
                <th class="px-4 py-2">
                  <button type="button" class="inline-flex items-center gap-1" @click="setSort('level_range')">
                    {{ t("location_detail.column.levels") }}
                    <span class="font-mono text-xs">{{ sortIndicator('level_range') }}</span>
                  </button>
                </th>
                <th class="px-4 py-2">
                  <button type="button" class="inline-flex items-center gap-1" @click="setSort('method')">
                    {{ t("location_detail.column.method") }}
                    <span class="font-mono text-xs">{{ sortIndicator('method') }}</span>
                  </button>
                </th>
                <th class="px-4 py-2">
                  <button type="button" class="inline-flex items-center gap-1" @click="setSort('rate')">
                    {{ t("location_detail.column.rate") }}
                    <span class="font-mono text-xs">{{ sortIndicator('rate') }}</span>
                  </button>
                </th>
                <th class="px-4 py-2">
                  <button type="button" class="inline-flex items-center gap-1" @click="setSort('period')">
                    {{ t("location_detail.column.time") }}
                    <span class="font-mono text-xs">{{ sortIndicator('period') }}</span>
                  </button>
                </th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="encounter in sortedEncounters"
                :key="`${encounter.pokemon_name}-${encounter.sub_location ?? ''}-${encounter.method}-${encounter.level_range}-${encounter.rate}`"
                class="border-t border-black/10"
              >
                <td class="px-4 py-2">
                  <div class="flex items-center gap-2">
                    <RouterLink
                      v-if="encounter.pokemon_id !== null"
                      :to="{ name: 'pokemon-detail', params: { id: encounter.pokemon_id } }"
                      class="inline-flex items-center gap-2 rounded-md px-1 py-0.5 transition hover:bg-black/5"
                    >
                      <img
                        :src="getPokemonSpriteUrl(encounter.pokemon_id)"
                        :alt="encounter.pokemon_name"
                        class="h-8 w-8 rounded border border-black/10 bg-white p-0.5 object-contain"
                        loading="lazy"
                        @error="(event) => handleSpriteError(event, encounter.pokemon_id!)"
                      />
                      <span class="font-semibold hover:underline">{{ encounter.pokemon_name }}</span>
                    </RouterLink>
                    <span v-else class="font-semibold">{{ encounter.pokemon_name }}</span>
                  </div>
                </td>
                <td class="px-4 py-2">{{ encounter.sub_location ?? "—" }}</td>
                <td class="px-4 py-2 font-mono">{{ encounter.level_range }}</td>
                <td class="px-4 py-2">{{ encounter.method }}</td>
                <td class="px-4 py-2">{{ encounter.rate }}</td>
                <td class="px-4 py-2">{{ encounter.period }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </article>
    </template>
  </section>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import { useQuery } from "@tanstack/vue-query";
import { RouterLink, useRoute } from "vue-router";

import { fetchPokemmoHoennLocation } from "@/api/client";
import { t, useLocale } from "@/i18n";
import type { LocationEncounter } from "@/types";

const POKEMON_SPRITE_BASE = "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon";
const OFFICIAL_ARTWORK_BASE =
  "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork";

const route = useRoute();
const locationName = computed(() => String(route.params.locationName ?? "").trim());
const { locale } = useLocale();

const locationQuery = useQuery({
  queryKey: computed(() => ["location-detail", "pokemmo", "hoenn", locale.value, locationName.value]),
  queryFn: () => fetchPokemmoHoennLocation(locationName.value),
  enabled: computed(() => locationName.value.length > 0)
});

const locationDetail = computed(() => locationQuery.data.value?.data ?? null);
const isLoading = computed(() => locationQuery.isLoading.value || locationQuery.isFetching.value);
const errorMessage = computed(() =>
  locationQuery.error.value instanceof Error ? locationQuery.error.value.message : ""
);
const birdviewImages = computed(() => {
  if (!locationDetail.value) {
    return [];
  }
  if (locationDetail.value.birdview_images?.length) {
    return locationDetail.value.birdview_images;
  }
  if (locationDetail.value.birdview_image_url) {
    return [
      {
        label: locationDetail.value.display_name,
        image_url: locationDetail.value.birdview_image_url,
        source_url: locationDetail.value.birdview_source_url
      }
    ];
  }
  return [];
});
const isBirdviewScrollable = computed(() => birdviewImages.value.length > 1);
const loadedMediaByUrl = ref<Record<string, boolean>>({});

function isMediaLoaded(url: string | null | undefined): boolean {
  if (!url) {
    return true;
  }
  return loadedMediaByUrl.value[url] === true;
}

function markMediaLoaded(url: string | null | undefined): void {
  if (!url) {
    return;
  }
  loadedMediaByUrl.value = {
    ...loadedMediaByUrl.value,
    [url]: true
  };
}

type EncounterRow = LocationEncounter & { period: string };
type SortColumn = "pokemon_name" | "sub_location" | "level_range" | "method" | "rate" | "period";
type SortDirection = "asc" | "desc";

const sortColumn = ref<SortColumn>("pokemon_name");
const sortDirection = ref<SortDirection>("asc");

const mergedEncounters = computed<EncounterRow[]>(() => {
  if (!locationDetail.value) {
    return [];
  }
  const grouped = new Map<
    string,
    {
      pokemon_name: string;
      pokemon_id: number | null;
      sub_location: string | null;
      level_range: string;
      method: string;
      rate: string;
      category: string;
      periods: Set<string>;
    }
  >();

  for (const encounter of locationDetail.value.encounters) {
    const key = [
      encounter.pokemon_name,
      encounter.pokemon_id ?? "",
      encounter.sub_location ?? "",
      encounter.level_range,
      encounter.method,
      encounter.rate,
      encounter.category
    ].join("||");

    const existing = grouped.get(key);
    if (existing) {
      existing.periods.add(encounter.period ?? "Any");
      continue;
    }

    grouped.set(key, {
      pokemon_name: encounter.pokemon_name,
      pokemon_id: encounter.pokemon_id,
      sub_location: encounter.sub_location ?? null,
      level_range: encounter.level_range,
      method: encounter.method,
      rate: encounter.rate,
      category: encounter.category,
      periods: new Set([encounter.period ?? t("location_detail.any_period")])
    });
  }

  return [...grouped.values()]
    .map((encounter) => {
      const periods = [...encounter.periods];
      const hasAny = periods.some((period) => isAnyPeriod(period));
      const normalizedPeriod = hasAny
        ? t("location_detail.any_period")
        : periods
            .sort(
              (a, b) =>
                periodTokenSortOrder(a) - periodTokenSortOrder(b)
            )
            .join(" | ");
      return {
        ...encounter,
        period: normalizedPeriod
      };
    });
});

const sortedEncounters = computed(() => {
  return [...mergedEncounters.value].sort((a, b) => {
    const direction = sortDirection.value === "asc" ? 1 : -1;
    const bySelected = compareByColumn(a, b, sortColumn.value);
    if (bySelected !== 0) {
      return bySelected * direction;
    }
    return a.pokemon_name.localeCompare(b.pokemon_name, undefined, { sensitivity: "base" });
  });
});

function getPokemonSpriteUrl(pokemonId: number) {
  return `${OFFICIAL_ARTWORK_BASE}/${pokemonId}.png`;
}

function handleSpriteError(event: Event, pokemonId: number) {
  const img = event.target as HTMLImageElement | null;
  if (!img) {
    return;
  }
  const fallback = `${POKEMON_SPRITE_BASE}/${pokemonId}.png`;
  if (img.src !== fallback) {
    img.src = fallback;
  }
}

function setSort(column: SortColumn) {
  if (sortColumn.value === column) {
    sortDirection.value = sortDirection.value === "asc" ? "desc" : "asc";
    return;
  }
  sortColumn.value = column;
  sortDirection.value = "asc";
}

function sortIndicator(column: SortColumn) {
  if (sortColumn.value !== column) {
    return "↕";
  }
  return sortDirection.value === "asc" ? "↑" : "↓";
}

function compareByColumn(a: EncounterRow, b: EncounterRow, column: SortColumn) {
  if (column === "level_range") {
    return parseLevelFloor(a.level_range) - parseLevelFloor(b.level_range);
  }
  if (column === "rate") {
    const rankDiff = rateRank(a.rate) - rateRank(b.rate);
    if (rankDiff !== 0) {
      return rankDiff;
    }
    return a.rate.localeCompare(b.rate, undefined, { sensitivity: "base" });
  }
  if (column === "period") {
    return periodRank(a.period) - periodRank(b.period);
  }

  const left = String(a[column] ?? "");
  const right = String(b[column] ?? "");
  return left.localeCompare(right, undefined, { sensitivity: "base", numeric: true });
}

function parseLevelFloor(levelRange: string) {
  const match = String(levelRange).match(/\d+/);
  if (!match) {
    return Number.MAX_SAFE_INTEGER;
  }
  return Number(match[0]);
}

function rateRank(rate: string) {
  const value = rate.toLowerCase();
  if (value.startsWith("very common") || value.startsWith("molto comune")) return 0;
  if (value.startsWith("common") || value.startsWith("comune")) return 1;
  if (value.startsWith("uncommon") || value.startsWith("non comune")) return 2;
  if (value.startsWith("rare") || value.startsWith("raro")) return 3;
  if (value.startsWith("very rare") || value.startsWith("molto raro")) return 4;
  if (value.includes("horde") || value.includes("orda")) return 5;
  if (value.includes("lure") || value.includes("aroma")) return 6;
  return 7;
}

function periodRank(period: string) {
  if (isAnyPeriod(period)) return 7;

  const bitmask = period
    .split("|")
    .map((token) => token.trim())
    .filter(Boolean)
    .reduce((result, token) => result | periodTokenBit(token), 0);

  if (bitmask === 1) return 0;
  if (bitmask === 2) return 1;
  if (bitmask === 4) return 2;
  if (bitmask === 3) return 3;
  if (bitmask === 6) return 4;
  if (bitmask === 5) return 5;
  if (bitmask === 7) return 6;
  return 8;
}

function isAnyPeriod(period: string) {
  const value = period.trim().toLowerCase();
  const localizedAny = t("location_detail.any_period").toLowerCase();
  return value === "any" || value === "qualsiasi" || value === localizedAny;
}

function periodTokenBit(token: string) {
  const value = token.trim().toLowerCase();
  if (value === "morning" || value === "mattina") return 1;
  if (value === "day" || value === "giorno") return 2;
  if (value === "night" || value === "notte") return 4;
  return 0;
}

function periodTokenSortOrder(token: string) {
  const bit = periodTokenBit(token);
  if (bit === 1) return 0;
  if (bit === 2) return 1;
  if (bit === 4) return 2;
  return Number.MAX_SAFE_INTEGER;
}
</script>
