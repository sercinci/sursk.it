<template>
  <RouterLink
    :to="`/pokemon/${pokemon.id}`"
    class="card-surface group flex items-center gap-3 rounded-2xl p-3 shadow-soft transition hover:-translate-y-0.5 focus-visible:ring-2 focus-visible:ring-accent/30 sm:gap-4 sm:p-4 lg:h-full lg:flex-col lg:items-center lg:gap-4 lg:p-5"
  >
    <div class="shrink-0 rounded-xl bg-white/80 p-1.5">
      <img
        v-if="pokemon.sprite"
        :src="pokemon.sprite"
        :alt="pokemon.name"
        class="h-12 w-12 object-contain transition group-hover:scale-105 sm:h-14 sm:w-14"
        loading="lazy"
      />
      <div v-else class="h-12 w-12 rounded-lg bg-black/5 sm:h-14 sm:w-14" />
    </div>

    <div class="min-w-0 flex-1 lg:w-full lg:text-center">
      <p class="font-mono text-xs text-muted">#{{ formatId(pokemon.id) }}</p>
      <h3 class="truncate font-display text-lg font-semibold capitalize text-text sm:text-xl lg:whitespace-normal">
        {{ pokemon.name }}
      </h3>
      <p v-if="evYieldText" class="mt-0.5 truncate text-[11px] font-semibold tracking-wide text-muted">
        {{ t("pokemon.ev_yield") }}: {{ evYieldText }}
      </p>
    </div>

    <div class="flex max-w-[45%] flex-wrap justify-end gap-1.5 lg:max-w-full lg:justify-center">
      <span
        v-for="type in pokemon.types"
        :key="type"
        class="rounded-full border px-2 py-0.5 text-xs font-semibold uppercase tracking-wide"
        :style="getTypeChipStyle(type)"
      >
        {{ labelType(type) }}
      </span>
    </div>
  </RouterLink>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { RouterLink } from "vue-router";

import { getTypeChipStyle } from "@/constants/pokemonTypes";
import { labelStatShort, labelType, t } from "@/i18n";
import type { PokemonListItem } from "@/types";

const props = defineProps<{
  pokemon: PokemonListItem;
}>();

const evYieldText = computed(() => {
  const entries = Object.entries(props.pokemon.ev_yield ?? {});
  if (!entries.length) {
    return "";
  }
  return entries
    .map(([name, value]) => `+${value} ${labelStatShort(name)}`)
    .join(", ");
});

function formatId(id: number) {
  return String(id).padStart(3, "0");
}
</script>
