<template>
  <section class="card-surface rounded-2xl p-4 sm:p-5">
    <div class="grid gap-3 md:grid-cols-3">
      <div class="flex flex-col gap-2">
        <label class="text-xs font-semibold uppercase tracking-wide text-muted" for="pokemon-search">
          {{ t("filters.search") }}
        </label>
        <input
          id="pokemon-search"
          v-model="searchDraft"
          type="search"
          :placeholder="t('filters.search_placeholder')"
          class="rounded-xl border border-black/10 bg-white px-3 py-2.5 text-sm outline-none ring-accent/30 focus:ring"
        />
        <label
          for="pokemon-hoenn-only"
          class="mt-1 inline-flex cursor-pointer items-center gap-2 text-xs font-semibold uppercase tracking-wide text-muted"
        >
          <input
            id="pokemon-hoenn-only"
            v-model="hoennOnlyDraft"
            type="checkbox"
            class="h-4 w-4 cursor-pointer rounded border-black/20 text-accent focus:ring-accent/30"
          />
          {{ t("filters.hoenn_only") }}
        </label>
      </div>

      <div class="flex flex-col gap-2">
        <label class="text-xs font-semibold uppercase tracking-wide text-muted" for="pokemon-type-filter">
          {{ t("filters.type") }}
        </label>
        <div id="pokemon-type-filter" class="flex flex-wrap gap-1.5 rounded-xl border border-black/10 bg-white p-2">
          <button
            v-for="option in typeOptions"
            :key="option"
            type="button"
            class="rounded-full border px-2 py-0.5 text-xs font-semibold uppercase tracking-wide transition"
            :class="isTypeSelected(option) ? 'opacity-100 ring-1 ring-black/20' : 'opacity-35 hover:opacity-60'"
            :style="getTypeChipStyle(option)"
            @click="toggleType(option)"
          >
            {{ labelType(option) }}
          </button>
        </div>
      </div>

      <div class="flex flex-col gap-2">
        <label class="text-xs font-semibold uppercase tracking-wide text-muted" for="pokemon-ev-yield-filter">
          {{ t("filters.ev_yield") }}
        </label>
        <select
          id="pokemon-ev-yield-filter"
          v-model="evYieldDraft"
          class="cursor-pointer rounded-xl border border-black/10 bg-white px-3 py-2.5 text-sm outline-none ring-accent/30 focus:ring"
        >
          <option value="">{{ t("filters.ev_all") }}</option>
          <option v-for="option in evYieldOptions" :key="option.value" :value="option.value">
            {{ option.label }}
          </option>
        </select>
      </div>
    </div>

    <div class="mt-3 flex justify-end">
      <button
        type="button"
        class="cursor-pointer rounded-xl border border-black/10 bg-white px-3 py-1.5 text-sm font-medium text-muted transition hover:border-black/20 hover:text-text disabled:cursor-not-allowed disabled:border-black/5 disabled:bg-black/5 disabled:text-slate-400 disabled:hover:border-black/5 disabled:hover:text-slate-400"
        :disabled="!hasActiveFilters"
        @click="emit('clear')"
      >
        {{ t("filters.clear") }}
      </button>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, ref, watch } from "vue";

import { TYPE_STYLES, getTypeChipStyle } from "@/constants/pokemonTypes";
import { labelType, t, useLocale } from "@/i18n";

const props = defineProps<{
  q: string;
  typeFilters: string[];
  evYield: string;
  hoennOnly: boolean;
}>();

const emit = defineEmits<{
  (event: "update:q", value: string): void;
  (event: "update:typeFilters", value: string[]): void;
  (event: "update:evYield", value: string): void;
  (event: "update:hoennOnly", value: boolean): void;
  (event: "clear"): void;
}>();

const searchDraft = ref(props.q);
const typeFiltersDraft = ref<string[]>([...props.typeFilters]);
const evYieldDraft = ref(props.evYield);
const hoennOnlyDraft = ref(props.hoennOnly);
let timer: ReturnType<typeof setTimeout> | null = null;

watch(
  () => props.q,
  (value) => {
    if (value !== searchDraft.value) {
      searchDraft.value = value;
    }
  }
);

watch(
  () => props.typeFilters,
  (value) => {
    if (JSON.stringify(value) !== JSON.stringify(typeFiltersDraft.value)) {
      typeFiltersDraft.value = [...value];
    }
  },
  { deep: true }
);

watch(
  () => props.evYield,
  (value) => {
    if (value !== evYieldDraft.value) {
      evYieldDraft.value = value;
    }
  }
);

watch(
  () => props.hoennOnly,
  (value) => {
    if (value !== hoennOnlyDraft.value) {
      hoennOnlyDraft.value = value;
    }
  }
);

watch(searchDraft, (value) => {
  if (timer) {
    clearTimeout(timer);
  }
  timer = setTimeout(() => {
    emit("update:q", value);
  }, 350);
});

watch(typeFiltersDraft, (value) => {
  emit("update:typeFilters", [...value]);
});

watch(evYieldDraft, (value) => {
  emit("update:evYield", value);
});

watch(hoennOnlyDraft, (value) => {
  emit("update:hoennOnly", value);
});

const typeOptions = Object.keys(TYPE_STYLES)
  .filter((type) => type !== "fairy")
  .sort((a, b) => a.localeCompare(b));

const { isItalian } = useLocale();
const evYieldOptions = computed(() => [
  { value: "hp", label: "HP" },
  { value: "attack", label: isItalian.value ? "Attacco" : "Attack" },
  { value: "defense", label: isItalian.value ? "Difesa" : "Defense" },
  { value: "special-attack", label: isItalian.value ? "Attacco Speciale" : "Special Attack" },
  { value: "special-defense", label: isItalian.value ? "Difesa Speciale" : "Special Defense" },
  { value: "speed", label: isItalian.value ? "Velocità" : "Speed" }
]);

const hasActiveFilters = computed(() =>
  Boolean(props.q || props.typeFilters.length || props.evYield || props.hoennOnly)
);

function isTypeSelected(type: string) {
  return typeFiltersDraft.value.includes(type);
}

function toggleType(type: string) {
  if (isTypeSelected(type)) {
    typeFiltersDraft.value = typeFiltersDraft.value.filter((value) => value !== type);
    return;
  }
  typeFiltersDraft.value = [...typeFiltersDraft.value, type];
}
</script>
