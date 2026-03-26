<template>
  <section class="space-y-6">
    <div>
      <p class="font-mono text-xs uppercase tracking-[0.18em] text-accent">{{ t("locations.region") }}</p>
      <h1 class="font-display text-3xl font-bold">{{ t("locations.title") }}</h1>
    </div>

    <div class="space-y-2">
      <label for="location-search" class="text-xs font-semibold uppercase tracking-wide text-muted">{{ t("locations.search") }}</label>
      <input
        id="location-search"
        v-model.trim="locationSearch"
        type="search"
        :placeholder="t('locations.search_placeholder')"
        class="w-full rounded-xl border border-black/10 bg-white/90 px-3 py-2 text-sm text-text outline-none transition focus:border-black/30"
      />
    </div>

    <p class="font-mono text-xs text-muted">{{ t("locations.locations_count", { count: filteredHoennLocations.length }) }}</p>

    <div class="space-y-8">
      <section v-for="section in locationSections" :key="section.key" class="space-y-3">
        <div class="flex items-end justify-between gap-3">
          <h2 class="font-display text-2xl font-semibold">{{ section.title }}</h2>
          <p class="font-mono text-xs text-muted">{{ t("locations.locations_count", { count: section.locations.length }) }}</p>
        </div>
        <p class="text-sm text-muted">{{ section.description }}</p>

        <div v-if="section.locations.length" class="grid gap-3 md:grid-cols-2">
          <RouterLink
            v-for="location in section.locations"
            :key="location.name"
            :to="{ name: 'location-detail', params: { locationName: location.name } }"
            class="block"
          >
            <article class="card-surface rounded-2xl p-4 transition hover:-translate-y-0.5 hover:shadow-soft">
              <div class="flex items-start justify-between gap-3">
                <h3 class="font-display text-lg font-semibold">{{ location.display_name }}</h3>
                <p class="font-mono text-xs text-muted">{{ location.pokemon_ids.length }} Pokémon</p>
              </div>

              <div class="mt-3 flex flex-wrap gap-1.5">
                <img
                  v-for="pokemonId in location.pokemon_ids"
                  :key="`${location.name}-${pokemonId}`"
                  :src="getPokemonSpriteUrl(pokemonId)"
                  :alt="getPokemonDisplayName(pokemonId)"
                  :title="getPokemonDisplayName(pokemonId)"
                  width="40"
                  height="40"
                  loading="lazy"
                  class="h-10 w-10 rounded-md border border-black/10 bg-white/90 p-1 object-contain"
                  @error="(event) => handleSpriteError(event, pokemonId)"
                />
              </div>
            </article>
          </RouterLink>
        </div>
        <p v-else class="text-sm text-muted">
          {{ hasLocationSearch ? t("locations.no_match_section") : t("locations.no_section") }}
        </p>
      </section>
    </div>

    <p v-if="!hoennLocations.length && !errorMessage" class="text-sm text-muted">
      {{ t("locations.none") }}
    </p>

    <p v-if="errorMessage" class="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-600">
      {{ errorMessage }}
    </p>
  </section>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import { useQuery } from "@tanstack/vue-query";
import { RouterLink } from "vue-router";

import { fetchPokemmoHoennLocations, fetchPokemonList } from "@/api/client";
import { t, useLocale } from "@/i18n";
import type { Location } from "@/types";

const POKEMON_SPRITE_BASE = "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon";
const OFFICIAL_ARTWORK_BASE =
  "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork";
const NON_CAPTURABLE_POKEMON_IDS = new Set([252, 255, 258, 351, 385]);

interface HoennLocation {
  name: string;
  display_name: string;
  pokemon_ids: number[];
}

type LocationGroupKey = "settlements" | "routes" | "landmarks";
const { locale } = useLocale();

const locationsQuery = useQuery({
  queryKey: computed(() => ["locations", "pokemmo", "hoenn", locale.value]),
  queryFn: fetchPokemmoHoennLocations
});

const pokemonIndexQuery = useQuery({
  queryKey: computed(() => ["pokemon-index", locale.value]),
  queryFn: fetchAllPokemonIndex
});

const locations = computed(() => locationsQuery.data.value?.data ?? []);
const pokemonNameById = computed(() => {
  const nameMap = new Map<number, string>();
  for (const pokemon of pokemonIndexQuery.data.value ?? []) {
    nameMap.set(pokemon.id, pokemon.name);
  }
  return nameMap;
});

const hoennLocations = computed<HoennLocation[]>(() =>
  locations.value
    .map((location) => ({
      name: location.name,
      display_name: location.display_name ?? formatLocationName(location.name),
      pokemon_ids: uniquePokemonIds(location).filter((pokemonId) => !NON_CAPTURABLE_POKEMON_IDS.has(pokemonId))
    }))
    .filter((location) => location.pokemon_ids.length > 0)
    .sort((a, b) =>
      a.display_name.localeCompare(b.display_name, undefined, {
        numeric: true,
        sensitivity: "base"
      })
    )
);
const locationSearch = ref("");
const normalizedLocationSearch = computed(() => locationSearch.value.trim().toLowerCase());
const hasLocationSearch = computed(() => normalizedLocationSearch.value.length > 0);
const filteredHoennLocations = computed<HoennLocation[]>(() => {
  const query = normalizedLocationSearch.value;
  if (!query) {
    return hoennLocations.value;
  }
  return hoennLocations.value.filter((location) => {
    const haystack = `${location.display_name} ${location.name}`.toLowerCase();
    return haystack.includes(query);
  });
});
const locationSections = computed(() => {
  const grouped: Record<LocationGroupKey, HoennLocation[]> = {
    settlements: [],
    routes: [],
    landmarks: []
  };

  for (const location of filteredHoennLocations.value) {
    grouped[classifyLocationGroup(location)].push(location);
  }

  return [
    {
      key: "settlements",
      title: t("locations.section.settlements"),
      description: t("locations.section.settlements_desc"),
      locations: grouped.settlements
    },
    {
      key: "routes",
      title: t("locations.section.routes"),
      description: t("locations.section.routes_desc"),
      locations: grouped.routes
    },
    {
      key: "landmarks",
      title: t("locations.section.landmarks"),
      description: t("locations.section.landmarks_desc"),
      locations: grouped.landmarks
    }
  ] as const;
});

const errorMessage = computed(() =>
  locationsQuery.error.value instanceof Error ? locationsQuery.error.value.message : ""
);

function uniquePokemonIds(location: Location) {
  return [...new Set(location.pokemon_ids)].sort((a, b) => a - b);
}

function formatLocationName(locationName: string) {
  const segments = locationName
    .replace(/^hoenn-/, "")
    .split("-")
    .filter(Boolean);
  const filteredSegments = segments.at(-1) === "area" ? segments.slice(0, -1) : segments;

  return filteredSegments
    .map((segment) => {
      if (segment === "oras") {
        return "ORAS";
      }
      if (/^b?\d+f$/i.test(segment)) {
        return segment.toUpperCase();
      }
      const mergedFloorMatch = segment.match(/^(\d+f)([a-z].*)$/i);
      if (mergedFloorMatch) {
        return `${mergedFloorMatch[1].toUpperCase()} ${mergedFloorMatch[2].charAt(0).toUpperCase()}${mergedFloorMatch[2].slice(1)}`;
      }
      if (/^\d+$/.test(segment)) {
        return segment;
      }
      return segment.charAt(0).toUpperCase() + segment.slice(1);
    })
    .join(" ");
}

function getPokemonSpriteUrl(pokemonId: number) {
  return `${OFFICIAL_ARTWORK_BASE}/${pokemonId}.png`;
}

function getPokemonDisplayName(pokemonId: number) {
  const name = pokemonNameById.value.get(pokemonId);
  if (!name) {
    return `Pokemon #${pokemonId}`;
  }
  return name
    .split("-")
    .filter(Boolean)
    .map((segment) => segment.charAt(0).toUpperCase() + segment.slice(1))
    .join(" ");
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

function classifyLocationGroup(location: HoennLocation): LocationGroupKey {
  if (/^hoenn-route-\d+-area$/i.test(location.name)) {
    return "routes";
  }
  if (/(city|town)-area$/i.test(location.name)) {
    return "settlements";
  }
  return "landmarks";
}

async function fetchAllPokemonIndex() {
  const pageSize = 100;
  let offset = 0;
  let total = 0;
  const rows: Array<{ id: number; name: string }> = [];

  do {
    const response = await fetchPokemonList({ limit: pageSize, offset });
    rows.push(...response.data.map((pokemon) => ({ id: pokemon.id, name: pokemon.name })));
    total = Number(response.meta.total ?? rows.length);
    offset += pageSize;
  } while (offset < total);

  return rows;
}
</script>
