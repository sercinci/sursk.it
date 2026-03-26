<template>
  <section class="space-y-5">
    <div>
      <h1 class="font-display text-3xl font-bold">{{ t("pokedex.title") }}</h1>
    </div>

    <PokemonFilters
      :q="store.q"
      :type-filters="store.typeFilters"
      :ev-yield="store.ev_yield"
      :hoenn-only="store.hoenn_only"
      @update:q="onSearch"
      @update:type-filters="onTypeFilters"
      @update:ev-yield="onEvYieldFilter"
      @update:hoenn-only="onHoennOnlyFilter"
      @clear="onClear"
    />

    <div class="flex items-center justify-between">
      <p class="font-mono text-xs uppercase tracking-wider text-muted">
        {{ t("pokedex.showing", { count: list.length, total }) }}
      </p>
      <div class="flex items-center gap-2">
        <button
          type="button"
          class="rounded-lg border border-black/10 px-3 py-1.5 text-sm disabled:opacity-40"
          :disabled="!canPrev"
          @click="store.setOffset(store.offset - store.limit)"
        >
          {{ t("pokedex.prev") }}
        </button>
        <span class="font-mono text-xs text-muted">{{ t("pokedex.page", { page }) }}</span>
        <button
          type="button"
          class="rounded-lg border border-black/10 px-3 py-1.5 text-sm disabled:opacity-40"
          :disabled="!canNext"
          @click="store.setOffset(store.offset + store.limit)"
        >
          {{ t("pokedex.next") }}
        </button>
      </div>
    </div>

    <SkeletonList v-if="isLoading" />

    <div v-else-if="list.length" class="grid gap-3 lg:grid-cols-2 xl:grid-cols-3">
      <PokemonCard v-for="pokemon in list" :key="pokemon.id" :pokemon="pokemon" />
    </div>

    <p v-else class="card-surface rounded-2xl p-6 text-center text-sm text-muted">{{ t("pokedex.empty") }}</p>

    <p v-if="errorMessage" class="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-600">
      {{ errorMessage }}
    </p>
  </section>
</template>

<script setup lang="ts">
import { computed, watch } from "vue";
import { useQuery } from "@tanstack/vue-query";
import { useRoute, useRouter } from "vue-router";

import { fetchPokemonList } from "@/api/client";
import PokemonCard from "@/components/PokemonCard.vue";
import PokemonFilters from "@/components/PokemonFilters.vue";
import SkeletonList from "@/components/SkeletonList.vue";
import { usePokedexFiltersStore } from "@/stores/pokedexFilters";
import { t, useLocale } from "@/i18n";

const route = useRoute();
const router = useRouter();
const store = usePokedexFiltersStore();
const { locale } = useLocale();

watch(
  () => route.query,
  (query) => {
    store.setFromRoute(query);
  },
  { immediate: true }
);

watch(
  () => [store.q, store.typeFilters, store.ev_yield, store.hoenn_only, store.offset],
  () => {
    const next = store.toRouteQuery();
    const current = JSON.stringify(route.query);
    const candidate = JSON.stringify(next);
    if (current !== candidate) {
      router.replace({ query: next });
    }
  }
);

const params = computed(() => ({
  q: store.q || undefined,
  type: store.typeFilters.length ? store.typeFilters.join(",") : undefined,
  ev_yield: store.ev_yield || undefined,
  hoenn_only: store.hoenn_only || undefined,
  limit: store.limit,
  offset: store.offset
}));

const pokemonQuery = useQuery({
  queryKey: computed(() => ["pokemon", locale.value, params.value]),
  queryFn: () => fetchPokemonList(params.value)
});

const list = computed(() => pokemonQuery.data.value?.data ?? []);
const total = computed(() => Number(pokemonQuery.data.value?.meta.total ?? 0));
const page = computed(() => Math.floor(store.offset / store.limit) + 1);
const canPrev = computed(() => store.offset > 0);
const canNext = computed(() => store.offset + store.limit < total.value);
const isLoading = computed(() => pokemonQuery.isPending.value);
const errorMessage = computed(() =>
  pokemonQuery.error.value instanceof Error ? pokemonQuery.error.value.message : ""
);

function onSearch(value: string) {
  store.setQ(value);
  store.setOffset(0);
}

function onTypeFilters(value: string[]) {
  store.setTypeFilters(value);
  store.setOffset(0);
}

function onEvYieldFilter(value: string) {
  store.setEvYield(value);
  store.setOffset(0);
}

function onHoennOnlyFilter(value: boolean) {
  store.setHoennOnly(value);
  store.setOffset(0);
}

function onClear() {
  store.clearFilters();
}
</script>
