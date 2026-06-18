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
                <TypeEffectivenessBadge
                  v-for="type in pokemonA.types"
                  :key="type"
                  :type="type"
                  mode="pokemon"
                  badge-class="px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide"
                  :focusable="false"
                />
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
                  <TypeEffectivenessBadge
                    v-for="type in p.types"
                    :key="type"
                    :type="type"
                    mode="pokemon"
                    badge-class="px-1.5 py-0.5 text-[10px] font-semibold uppercase"
                    :focusable="false"
                  />
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
                <TypeEffectivenessBadge
                  v-for="type in pokemonB.types"
                  :key="type"
                  :type="type"
                  mode="pokemon"
                  badge-class="px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide"
                  :focusable="false"
                />
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
                  <TypeEffectivenessBadge
                    v-for="type in p.types"
                    :key="type"
                    :type="type"
                    mode="pokemon"
                    badge-class="px-1.5 py-0.5 text-[10px] font-semibold uppercase"
                    :focusable="false"
                  />
                </div>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Stored build import -->
    <article v-if="storedBuildOptions.length > 0" class="card-surface overflow-visible rounded-2xl p-4">
      <div class="flex flex-col gap-3 sm:flex-row sm:items-end">
        <div class="min-w-0 flex-1">
          <h2 class="font-display text-sm font-semibold text-text">{{ t("compare.stored.title") }}</h2>
          <p class="mt-0.5 text-xs text-muted">{{ t("compare.stored.subtitle") }}</p>
          <p v-if="knownMoveNamesA.length || knownMoveNamesB.length" class="mt-1 font-mono text-[10px] font-semibold uppercase tracking-wide text-accent">
            {{ t("compare.stored.known_moves") }}
          </p>
        </div>
        <div class="grid grid-cols-1 gap-2 sm:w-[30rem] sm:grid-cols-2">
          <label>
            <span class="mb-1 block font-mono text-[10px] uppercase tracking-wide text-muted">{{ t("compare.stored.import_a") }}</span>
            <select
              :value="storedImportA"
              class="h-9 w-full rounded-xl border border-sky-200 bg-white/80 px-2 text-xs text-text outline-none focus:border-sky-400 focus:ring-1 focus:ring-sky-100"
              @change="onStoredImportChange('a', $event)"
            >
              <option value="">{{ t("compare.stored.none") }}</option>
              <option v-for="option in storedBuildOptions" :key="`a-${option.value}`" :value="option.value">
                {{ option.label }}
              </option>
            </select>
          </label>
          <label>
            <span class="mb-1 block font-mono text-[10px] uppercase tracking-wide text-muted">{{ t("compare.stored.import_b") }}</span>
            <select
              :value="storedImportB"
              class="h-9 w-full rounded-xl border border-amber-200 bg-white/80 px-2 text-xs text-text outline-none focus:border-amber-400 focus:ring-1 focus:ring-amber-100"
              @change="onStoredImportChange('b', $event)"
            >
              <option value="">{{ t("compare.stored.none") }}</option>
              <option v-for="option in storedBuildOptions" :key="`b-${option.value}`" :value="option.value">
                {{ option.label }}
              </option>
            </select>
          </label>
        </div>
      </div>
    </article>

    <!-- Placeholder -->
    <div v-if="!pokemonA || !pokemonB" class="card-surface rounded-2xl px-6 py-10 text-center text-sm text-muted">
      {{ t("compare.select_prompt") }}
    </div>

    <template v-else>
      <!-- ══ Section 1: STAB vs Type ══ -->
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

      <!-- ══ Section 2: Statistics ══ -->
      <article class="card-surface overflow-hidden rounded-2xl">
        <div class="space-y-3 border-b border-black/8 px-5 py-3.5">
          <h2 class="font-display font-semibold text-text">{{ t("compare.section.statistics") }}</h2>
          <div class="grid grid-cols-3 gap-2 sm:flex sm:flex-wrap">
            <label class="min-w-0">
              <span class="mb-1 block font-mono text-[10px] uppercase tracking-wide text-muted">{{ t("compare.level") }}</span>
              <input
                v-model.number="calculatorLevel"
                type="number"
                min="1"
                max="100"
                step="1"
                class="h-8 w-full rounded-lg border border-black/10 bg-white/80 px-2 font-mono text-xs text-text outline-none focus:border-accent/50 focus:ring-1 focus:ring-accent/20 sm:w-20"
              />
            </label>
            <label class="min-w-0">
              <span class="mb-1 block font-mono text-[10px] uppercase tracking-wide text-muted">{{ t("compare.weather") }}</span>
              <select
                v-model="selectedWeather"
                class="h-8 w-full rounded-lg border border-black/10 bg-white/80 px-2 font-mono text-xs text-text outline-none focus:border-accent/50 focus:ring-1 focus:ring-accent/20 sm:w-36"
              >
                <option v-for="weather in WEATHER_OPTIONS" :key="weather" :value="weather">
                  {{ labelWeather(weather) }}
                </option>
              </select>
            </label>
          </div>
        </div>
        <div class="p-5">
          <!-- Column headers -->
          <div class="mb-3 grid grid-cols-[1fr_48px_1fr] items-center gap-2">
            <div class="min-w-0 space-y-1">
              <p class="truncate text-right font-mono text-xs font-bold capitalize text-sky-600">{{ pokemonA.name }}</p>
              <div class="grid grid-cols-1 gap-1 sm:grid-cols-[minmax(0,1fr)_152px]">
                <div class="relative">
                  <input
                    v-model="natureSearchA"
                    type="text"
                    :placeholder="t('compare.nature_placeholder')"
                    class="h-8 w-full rounded-lg border border-black/10 bg-white/80 py-0 pl-2 pr-8 text-left text-xs text-text outline-none placeholder:text-muted/50 focus:border-accent/50 focus:ring-1 focus:ring-accent/20"
                    :aria-label="`${pokemonA.name} ${t('compare.nature')}`"
                    @focus="showNatureDropA = true"
                    @click="showNatureDropA = true"
                    @input="onNatureInput('a')"
                    @blur="onNatureBlur('a')"
                  />
                  <button
                    v-if="natureSearchA"
                    type="button"
                    class="absolute right-2 top-1/2 inline-flex h-5 w-5 -translate-y-1/2 cursor-pointer items-center justify-center font-mono text-[11px] font-bold text-muted transition hover:text-red-600"
                    :aria-label="`${t('compare.clear_nature')} ${pokemonA.name}`"
                    @mousedown.prevent.stop
                    @click.stop="clearNature('a')"
                  >x</button>
                  <div
                    v-if="showNatureDropA && natureResultsA.length > 0"
                    class="absolute left-0 right-0 top-full z-40 mt-1 max-h-56 overflow-y-auto rounded-xl border border-accent/15 bg-white text-left shadow-lg"
                  >
                    <button
                      v-for="nature in natureResultsA"
                      :key="`a-${nature.id}`"
                      type="button"
                      class="flex w-full items-center justify-between gap-2 px-3 py-2 text-left text-xs transition hover:bg-accent/10"
                      @mousedown.prevent="selectNature('a', nature)"
                    >
                      <span class="font-medium text-text">{{ getNatureName(nature) }}</span>
                      <span class="font-mono text-[10px] text-muted">({{ formatNatureModifier(nature) }})</span>
                    </button>
                  </div>
                </div>
                <label>
                  <span class="sr-only">{{ t("compare.status") }}</span>
                  <select
                    v-model="selectedStatusA"
                    class="h-8 w-full rounded-lg border border-black/10 bg-white/80 px-2 font-mono text-xs text-text outline-none focus:border-accent/50 focus:ring-1 focus:ring-accent/20"
                    :aria-label="`${pokemonA.name} ${t('compare.status')}`"
                  >
                    <option v-for="status in STATUS_OPTIONS" :key="`a-${status}`" :value="status">
                      {{ labelStatus(status) }}
                    </option>
                  </select>
                </label>
              </div>
              <label class="group relative !mt-1.5 block">
                <span class="sr-only">{{ t("compare.ability") }}</span>
                <select
                  v-model="selectedAbilityA"
                  class="h-8 w-full rounded-lg border border-black/10 bg-white/80 px-2 font-mono text-xs text-text outline-none focus:border-accent/50 focus:ring-1 focus:ring-accent/20"
                  :aria-label="`${pokemonA.name} ${t('compare.ability')}`"
                  :title="selectedAbilityDescriptionA"
                >
                  <option v-for="ability in pokemonA.abilities" :key="`a-${ability.name}`" :value="ability.name">
                    {{ formatAbilityOption(ability) }}
                  </option>
                </select>
                <span
                  v-if="selectedAbilityDescriptionA"
                  class="pointer-events-none absolute left-0 right-0 top-full z-50 mt-2 rounded-lg border border-black/10 bg-white px-3 py-2 text-left text-xs font-medium normal-case leading-relaxed text-text opacity-0 shadow-soft transition-opacity group-hover:opacity-100 group-focus-within:opacity-100"
                >
                  {{ selectedAbilityDescriptionA }}
                </span>
              </label>
              <div class="!mt-1.5 flex flex-wrap items-center gap-1">
                <div
                  class="flex h-8 w-full min-w-0 overflow-hidden rounded-lg border border-black/10 bg-white/80 sm:min-w-[154px] sm:flex-1"
                  role="group"
                  :aria-label="`${pokemonA.name} ${t('compare.spikes')}`"
                >
                  <span class="hidden items-center border-r border-black/10 px-2 font-mono text-[10px] font-bold uppercase text-muted sm:flex">{{ t("compare.spikes") }}</span>
                  <button
                    v-for="layers in HAZARD_LAYER_OPTIONS"
                    :key="`a-spikes-${layers}`"
                    type="button"
                    :aria-pressed="entryHazardsA.spikes === layers"
                    :aria-label="`${pokemonA.name} ${t('compare.spikes')} ${layers}`"
                    :class="[
                      'h-full min-w-0 flex-1 border-l border-black/10 font-mono text-[11px] font-bold transition first:border-l-0 focus:outline-none focus:ring-1 focus:ring-inset focus:ring-accent/30',
                      entryHazardsA.spikes === layers ? 'bg-accent text-white' : 'text-muted hover:bg-accent/10 hover:text-text'
                    ]"
                    @click="entryHazardsA.spikes = layers"
                  >{{ layers }}</button>
                </div>
                <label
                  :class="[
                    'flex h-8 w-full min-w-0 cursor-pointer items-center justify-center gap-1.5 rounded-lg border px-2 font-mono text-[10px] font-bold uppercase transition sm:min-w-[118px] sm:flex-1',
                    entryHazardsA.stealthRock ? 'border-accent/40 bg-accent/10 text-text' : 'border-black/10 bg-white/80 text-muted hover:border-accent/30 hover:text-text'
                  ]"
                  :title="t('compare.stealth_rock')"
                >
                  <input
                    v-model="entryHazardsA.stealthRock"
                    type="checkbox"
                    class="h-3.5 w-3.5 accent-accent"
                    :aria-label="`${pokemonA.name} ${t('compare.stealth_rock')}`"
                  />
                  {{ t("compare.stealth_rock") }}
                </label>
              </div>
            </div>
            <div />
            <div class="min-w-0 space-y-1">
              <p class="truncate font-mono text-xs font-bold capitalize text-amber-600">{{ pokemonB.name }}</p>
              <div class="grid grid-cols-1 gap-1 sm:grid-cols-[minmax(0,1fr)_152px]">
                <div class="relative">
                  <input
                    v-model="natureSearchB"
                    type="text"
                    :placeholder="t('compare.nature_placeholder')"
                    class="h-8 w-full rounded-lg border border-black/10 bg-white/80 py-0 pl-2 pr-8 text-left text-xs text-text outline-none placeholder:text-muted/50 focus:border-accent/50 focus:ring-1 focus:ring-accent/20"
                    :aria-label="`${pokemonB.name} ${t('compare.nature')}`"
                    @focus="showNatureDropB = true"
                    @click="showNatureDropB = true"
                    @input="onNatureInput('b')"
                    @blur="onNatureBlur('b')"
                  />
                  <button
                    v-if="natureSearchB"
                    type="button"
                    class="absolute right-2 top-1/2 inline-flex h-5 w-5 -translate-y-1/2 cursor-pointer items-center justify-center font-mono text-[11px] font-bold text-muted transition hover:text-red-600"
                    :aria-label="`${t('compare.clear_nature')} ${pokemonB.name}`"
                    @mousedown.prevent.stop
                    @click.stop="clearNature('b')"
                  >x</button>
                  <div
                    v-if="showNatureDropB && natureResultsB.length > 0"
                    class="absolute left-0 right-0 top-full z-40 mt-1 max-h-56 overflow-y-auto rounded-xl border border-accent/15 bg-white text-left shadow-lg"
                  >
                    <button
                      v-for="nature in natureResultsB"
                      :key="`b-${nature.id}`"
                      type="button"
                      class="flex w-full items-center justify-between gap-2 px-3 py-2 text-left text-xs transition hover:bg-accent/10"
                      @mousedown.prevent="selectNature('b', nature)"
                    >
                      <span class="font-medium text-text">{{ getNatureName(nature) }}</span>
                      <span class="font-mono text-[10px] text-muted">({{ formatNatureModifier(nature) }})</span>
                    </button>
                  </div>
                </div>
                <label>
                  <span class="sr-only">{{ t("compare.status") }}</span>
                  <select
                    v-model="selectedStatusB"
                    class="h-8 w-full rounded-lg border border-black/10 bg-white/80 px-2 font-mono text-xs text-text outline-none focus:border-accent/50 focus:ring-1 focus:ring-accent/20"
                    :aria-label="`${pokemonB.name} ${t('compare.status')}`"
                  >
                    <option v-for="status in STATUS_OPTIONS" :key="`b-${status}`" :value="status">
                      {{ labelStatus(status) }}
                    </option>
                  </select>
                </label>
              </div>
              <label class="group relative !mt-1.5 block">
                <span class="sr-only">{{ t("compare.ability") }}</span>
                <select
                  v-model="selectedAbilityB"
                  class="h-8 w-full rounded-lg border border-black/10 bg-white/80 px-2 font-mono text-xs text-text outline-none focus:border-accent/50 focus:ring-1 focus:ring-accent/20"
                  :aria-label="`${pokemonB.name} ${t('compare.ability')}`"
                  :title="selectedAbilityDescriptionB"
                >
                  <option v-for="ability in pokemonB.abilities" :key="`b-${ability.name}`" :value="ability.name">
                    {{ formatAbilityOption(ability) }}
                  </option>
                </select>
                <span
                  v-if="selectedAbilityDescriptionB"
                  class="pointer-events-none absolute left-0 right-0 top-full z-50 mt-2 rounded-lg border border-black/10 bg-white px-3 py-2 text-left text-xs font-medium normal-case leading-relaxed text-text opacity-0 shadow-soft transition-opacity group-hover:opacity-100 group-focus-within:opacity-100"
                >
                  {{ selectedAbilityDescriptionB }}
                </span>
              </label>
              <div class="!mt-1.5 flex flex-wrap items-center gap-1">
                <div
                  class="flex h-8 w-full min-w-0 overflow-hidden rounded-lg border border-black/10 bg-white/80 sm:min-w-[154px] sm:flex-1"
                  role="group"
                  :aria-label="`${pokemonB.name} ${t('compare.spikes')}`"
                >
                  <span class="hidden items-center border-r border-black/10 px-2 font-mono text-[10px] font-bold uppercase text-muted sm:flex">{{ t("compare.spikes") }}</span>
                  <button
                    v-for="layers in HAZARD_LAYER_OPTIONS"
                    :key="`b-spikes-${layers}`"
                    type="button"
                    :aria-pressed="entryHazardsB.spikes === layers"
                    :aria-label="`${pokemonB.name} ${t('compare.spikes')} ${layers}`"
                    :class="[
                      'h-full min-w-0 flex-1 border-l border-black/10 font-mono text-[11px] font-bold transition first:border-l-0 focus:outline-none focus:ring-1 focus:ring-inset focus:ring-accent/30',
                      entryHazardsB.spikes === layers ? 'bg-accent text-white' : 'text-muted hover:bg-accent/10 hover:text-text'
                    ]"
                    @click="entryHazardsB.spikes = layers"
                  >{{ layers }}</button>
                </div>
                <label
                  :class="[
                    'flex h-8 w-full min-w-0 cursor-pointer items-center justify-center gap-1.5 rounded-lg border px-2 font-mono text-[10px] font-bold uppercase transition sm:min-w-[118px] sm:flex-1',
                    entryHazardsB.stealthRock ? 'border-accent/40 bg-accent/10 text-text' : 'border-black/10 bg-white/80 text-muted hover:border-accent/30 hover:text-text'
                  ]"
                  :title="t('compare.stealth_rock')"
                >
                  <input
                    v-model="entryHazardsB.stealthRock"
                    type="checkbox"
                    class="h-3.5 w-3.5 accent-accent"
                    :aria-label="`${pokemonB.name} ${t('compare.stealth_rock')}`"
                  />
                  {{ t("compare.stealth_rock") }}
                </label>
              </div>
            </div>
          </div>

          <!-- Stat rows -->
          <div class="space-y-1.5">
            <div v-for="row in statRows" :key="row.stat" class="grid grid-cols-[1fr_48px_1fr] items-center gap-2">
              <!-- A: value + bar (right-to-left) -->
              <div class="space-y-1">
                <div class="flex items-start justify-end gap-2">
                  <div class="grid w-28 grid-cols-[56px_48px] items-start gap-1">
                    <span
                      v-if="getStatModifierLabel(pokemonA, natureA, row.stat, selectedStatusA, selectedAbilityA)"
                      :class="['inline-flex w-14 justify-center rounded border px-1 py-0.5 font-mono text-[9px] font-bold', statModifierBadgeClass(getStatModifierLabel(pokemonA, natureA, row.stat, selectedStatusA, selectedAbilityA))]"
                    >{{ getStatModifierLabel(pokemonA, natureA, row.stat, selectedStatusA, selectedAbilityA) }}</span>
                    <span v-else class="w-14" aria-hidden="true"></span>
                    <div class="relative flex w-12 flex-col items-end">
                      <span :class="['w-10 text-right font-mono text-sm font-bold', row.aWins ? 'text-sky-600' : 'text-slate-400']">{{ row.a }}</span>
                      <label
                        v-if="row.stat !== 'hp'"
                        class="absolute right-0 top-full mt-1 flex items-center gap-1 font-mono text-[9px] uppercase text-muted"
                      >
                        {{ t("compare.stage") }}
                        <input
                          v-model.number="statSettingsA[row.stat].stage"
                          type="number"
                          min="-6"
                          max="6"
                          step="1"
                          :aria-label="`${pokemonA.name} ${labelStatShort(row.stat)} ${t('compare.stage')}`"
                          class="h-5 w-[41px] rounded border border-black/10 bg-white/80 px-1 text-[11px] text-text outline-none focus:border-accent/50 focus:ring-1 focus:ring-accent/20"
                          @change="clampStageInput(statSettingsA, row.stat)"
                        />
                      </label>
                      <label
                        v-else
                        class="absolute right-0 top-full mt-1 flex items-center gap-1 font-mono text-[9px] uppercase text-muted"
                      >
                        {{ t("compare.current_hp_short") }}
                        <input
                          v-model.number="currentHpPercentA"
                          type="number"
                          min="1"
                          max="100"
                          step="1"
                          :aria-label="`${pokemonA.name} ${t('compare.current_hp')}`"
                          class="h-5 w-[45px] rounded border border-black/10 bg-white/80 px-1 text-[11px] text-text outline-none focus:border-accent/50 focus:ring-1 focus:ring-accent/20"
                          @change="clampCurrentHpPercent('a')"
                        />
                      </label>
                    </div>
                  </div>
                  <div class="mt-[7px] h-2 flex-1 overflow-hidden rounded-full bg-black/8">
                    <div
                      class="ml-auto h-full rounded-full bg-sky-500 transition-all duration-300"
                      :style="{ width: statBarPct(row.a, row.max) + '%' }"
                    />
                  </div>
                </div>
                <div class="flex justify-end gap-1">
                  <label class="flex items-center gap-1 font-mono text-[9px] uppercase text-muted">
                    {{ t("compare.iv") }}
                    <input
                      v-model.number="statSettingsA[row.stat].iv"
                      type="number"
                      min="0"
                      max="31"
                      step="1"
                      :aria-label="`${pokemonA.name} ${labelStatShort(row.stat)} ${t('compare.iv')}`"
                      class="h-6 w-11 rounded border border-black/10 bg-white/80 px-1 text-[11px] text-text outline-none focus:border-accent/50 focus:ring-1 focus:ring-accent/20"
                      @input="onComparisonIvInput(statSettingsA, row.stat, $event)"
                    />
                  </label>
                  <label class="flex items-center gap-1 font-mono text-[9px] uppercase text-muted">
                    {{ t("compare.ev") }}
                    <input
                      v-model.number="statSettingsA[row.stat].ev"
                      type="number"
                      min="0"
                      max="252"
                      step="1"
                      :aria-label="`${pokemonA.name} ${labelStatShort(row.stat)} ${t('compare.ev')}`"
                      class="h-6 w-12 rounded border border-black/10 bg-white/80 px-1 text-[11px] text-text outline-none focus:border-accent/50 focus:ring-1 focus:ring-accent/20"
                      @input="onComparisonEvInput(statSettingsA, row.stat, $event)"
                    />
                  </label>
                </div>
              </div>
              <!-- Stat label -->
              <div class="text-center">
                <span class="font-mono text-[11px] font-bold uppercase text-muted">{{ labelStatShort(row.stat) }}</span>
              </div>
              <!-- B: bar + value (left-to-right) -->
              <div class="space-y-1">
                <div class="flex items-start gap-2">
                  <div class="mt-[7px] h-2 flex-1 overflow-hidden rounded-full bg-black/8">
                    <div
                      class="h-full rounded-full bg-amber-400 transition-all duration-300"
                      :style="{ width: statBarPct(row.b, row.max) + '%' }"
                    />
                  </div>
                  <div class="grid w-28 grid-cols-[48px_56px] items-start gap-1">
                    <div class="relative flex w-12 flex-col items-start">
                      <span :class="['w-10 font-mono text-sm font-bold', row.bWins ? 'text-amber-600' : 'text-slate-400']">{{ row.b }}</span>
                      <label
                        v-if="row.stat !== 'hp'"
                        class="absolute left-0 top-full mt-1 flex items-center gap-1 font-mono text-[9px] uppercase text-muted"
                      >
                        {{ t("compare.stage") }}
                        <input
                          v-model.number="statSettingsB[row.stat].stage"
                          type="number"
                          min="-6"
                          max="6"
                          step="1"
                          :aria-label="`${pokemonB.name} ${labelStatShort(row.stat)} ${t('compare.stage')}`"
                          class="h-5 w-[41px] rounded border border-black/10 bg-white/80 px-1 text-[11px] text-text outline-none focus:border-accent/50 focus:ring-1 focus:ring-accent/20"
                          @change="clampStageInput(statSettingsB, row.stat)"
                        />
                      </label>
                      <label
                        v-else
                        class="absolute left-0 top-full mt-1 flex items-center gap-1 font-mono text-[9px] uppercase text-muted"
                      >
                        {{ t("compare.current_hp_short") }}
                        <input
                          v-model.number="currentHpPercentB"
                          type="number"
                          min="1"
                          max="100"
                          step="1"
                          :aria-label="`${pokemonB.name} ${t('compare.current_hp')}`"
                          class="h-5 w-[45px] rounded border border-black/10 bg-white/80 px-1 text-[11px] text-text outline-none focus:border-accent/50 focus:ring-1 focus:ring-accent/20"
                          @change="clampCurrentHpPercent('b')"
                        />
                      </label>
                    </div>
                    <span
                      v-if="getStatModifierLabel(pokemonB, natureB, row.stat, selectedStatusB, selectedAbilityB)"
                      :class="['inline-flex w-14 justify-center rounded border px-1 py-0.5 font-mono text-[9px] font-bold', statModifierBadgeClass(getStatModifierLabel(pokemonB, natureB, row.stat, selectedStatusB, selectedAbilityB))]"
                    >{{ getStatModifierLabel(pokemonB, natureB, row.stat, selectedStatusB, selectedAbilityB) }}</span>
                    <span v-else class="w-14" aria-hidden="true"></span>
                  </div>
                </div>
                <div class="flex justify-start gap-1">
                  <label class="flex items-center gap-1 font-mono text-[9px] uppercase text-muted">
                    {{ t("compare.iv") }}
                    <input
                      v-model.number="statSettingsB[row.stat].iv"
                      type="number"
                      min="0"
                      max="31"
                      step="1"
                      :aria-label="`${pokemonB.name} ${labelStatShort(row.stat)} ${t('compare.iv')}`"
                      class="h-6 w-11 rounded border border-black/10 bg-white/80 px-1 text-[11px] text-text outline-none focus:border-accent/50 focus:ring-1 focus:ring-accent/20"
                      @input="onComparisonIvInput(statSettingsB, row.stat, $event)"
                    />
                  </label>
                  <label class="flex items-center gap-1 font-mono text-[9px] uppercase text-muted">
                    {{ t("compare.ev") }}
                    <input
                      v-model.number="statSettingsB[row.stat].ev"
                      type="number"
                      min="0"
                      max="252"
                      step="1"
                      :aria-label="`${pokemonB.name} ${labelStatShort(row.stat)} ${t('compare.ev')}`"
                      class="h-6 w-12 rounded border border-black/10 bg-white/80 px-1 text-[11px] text-text outline-none focus:border-accent/50 focus:ring-1 focus:ring-accent/20"
                      @input="onComparisonEvInput(statSettingsB, row.stat, $event)"
                    />
                  </label>
                </div>
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

      <!-- ══ Section 3: Move Effectiveness ══ -->
      <article class="card-surface overflow-hidden rounded-2xl">
        <div class="border-b border-black/8 px-5 py-3.5">
          <h2 class="font-display font-semibold text-text">{{ t("compare.section.moves") }}</h2>
          <p class="mt-1 text-[11px] text-muted">
            {{ t("compare.damage_note", { level: calculatorLevelValue }) }}
          </p>
        </div>
        <div class="grid grid-cols-1 divide-y divide-black/8 md:grid-cols-2 md:divide-x md:divide-y-0">
          <!-- A moves vs B -->
          <div class="flex flex-col p-5">
            <p class="mb-3 text-[11px] font-semibold uppercase tracking-widest text-muted">
              {{ t("compare.moves_vs", { name: capitalize(pokemonB.name) }) }}
            </p>
            <div
              v-if="selectedDamageAvsB"
              class="mb-3 rounded-lg border border-accent/15 bg-white/80 px-3 py-2"
            >
              <div class="mb-2 flex flex-wrap items-start justify-between gap-2">
                <div>
                  <p class="text-sm font-semibold capitalize text-text">{{ selectedDamageAvsB.move.display_name ?? selectedDamageAvsB.move.name }}</p>
                  <label class="mt-1 inline-flex cursor-pointer items-center gap-1.5 font-mono text-[10px] font-bold uppercase tracking-wide text-muted transition hover:text-text">
                    <input
                      v-model="criticalAvsB"
                      type="checkbox"
                      class="h-3.5 w-3.5 accent-accent"
                      :aria-label="`${selectedDamageAvsB.move.display_name ?? selectedDamageAvsB.move.name} ${t('compare.critical')}`"
                    />
                    {{ t("compare.critical") }}
                  </label>
                </div>
                <div class="flex shrink-0 flex-wrap items-center justify-end gap-1">
                  <span
                    v-if="formatCriticalModifier(selectedDamageAvsB.calculation)"
                    class="rounded-full border border-rose-200 bg-rose-50 px-1.5 py-0.5 font-mono text-[10px] font-bold text-rose-700"
                  >{{ formatCriticalModifier(selectedDamageAvsB.calculation) }}</span>
                  <span
                    v-if="formatWeatherDamageModifier(selectedDamageAvsB.calculation)"
                    class="rounded-full border border-amber-200 bg-amber-50 px-1.5 py-0.5 font-mono text-[10px] font-bold text-amber-700"
                  >{{ formatWeatherDamageModifier(selectedDamageAvsB.calculation) }}</span>
                  <span
                    v-if="formatStatusDamageModifier(selectedDamageAvsB.calculation)"
                    class="rounded-full border border-red-200 bg-red-50 px-1.5 py-0.5 font-mono text-[10px] font-bold text-red-600"
                  >{{ formatStatusDamageModifier(selectedDamageAvsB.calculation) }}</span>
                  <span
                    v-if="formatStatusResidualModifier(selectedDamageAvsB.calculation)"
                    class="rounded-full border border-violet-200 bg-violet-50 px-1.5 py-0.5 font-mono text-[10px] font-bold text-violet-700"
                  >{{ formatStatusResidualModifier(selectedDamageAvsB.calculation) }}</span>
                  <span
                    v-for="hazardLabel in formatEntryHazardModifiers(selectedDamageAvsB.calculation)"
                    :key="`a-entry-hazard-${hazardLabel}`"
                    class="rounded-full border border-stone-200 bg-stone-50 px-1.5 py-0.5 font-mono text-[10px] font-bold text-stone-700"
                  >{{ hazardLabel }}</span>
                  <span
                    v-for="weatherLabel in formatWeatherResidualModifiers(selectedDamageAvsB.calculation)"
                    :key="`a-weather-residual-${weatherLabel}`"
                    class="rounded-full border border-amber-200 bg-amber-50 px-1.5 py-0.5 font-mono text-[10px] font-bold text-amber-700"
                  >{{ weatherLabel }}</span>
                  <span
                    v-for="abilityLabel in formatAbilityDamageModifiers(selectedDamageAvsB.calculation)"
                    :key="`a-ability-${abilityLabel}`"
                    class="rounded-full border border-indigo-200 bg-indigo-50 px-1.5 py-0.5 font-mono text-[10px] font-bold text-indigo-700"
                  >{{ abilityLabel }}</span>
                  <span :class="['rounded-full border px-1.5 py-0.5 text-[11px] font-bold', multiplierBadgeClass(selectedDamageAvsB.move.multiplier)]">{{ formatMultiplier(selectedDamageAvsB.move.multiplier) }}</span>
                </div>
              </div>
              <div>
                <p class="font-mono text-[10px] uppercase tracking-wide text-muted">{{ t("compare.damage_range") }}</p>
                <p class="font-mono font-bold text-text">{{ formatDamageRange(selectedDamageAvsB.calculation) }} HP</p>
                <p class="font-mono text-[11px] text-muted">
                  {{ formatDamagePercentRange(selectedDamageAvsB.calculation) }} {{ formatKoSummary(selectedDamageAvsB.calculation) }}
                </p>
              </div>
            </div>
            <p v-if="movesAQuery.isPending.value" class="text-xs text-muted">{{ t("compare.loading_moves") }}</p>
            <p v-else-if="!damageMovesAvsB.length" class="text-xs text-muted">{{ t("compare.no_damage_moves") }}</p>
            <div v-else class="max-h-64 space-y-0.5 overflow-y-auto pr-1 md:max-h-96">
              <div
                v-for="move in damageMovesAvsB"
                :key="move.name"
                class="rounded-lg"
              >
                <button
                  type="button"
                  class="flex w-full flex-wrap items-center gap-1.5 rounded-lg border px-2 py-1.5 text-left transition"
                  :class="moveRowClass(move, selectedMoveAvsB, knownMoveNamesA)"
                  @click="selectedMoveAvsB = move.name"
                >
                  <TypeEffectivenessBadge
                    v-if="move.effectiveType"
                    :type="move.effectiveType"
                    mode="move"
                    badge-class="shrink-0 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide"
                  />
                  <span class="min-w-28 flex-1 truncate text-xs capitalize text-text">{{ move.display_name ?? move.name }}</span>
                  <span
                    v-if="knownMoveNamesA.includes(move.name)"
                    class="shrink-0 rounded border border-accent/20 bg-accent/10 px-1.5 py-0.5 font-mono text-[9px] font-semibold uppercase tracking-wide text-accent"
                  >
                    {{ t("compare.stored.known_move") }}
                  </span>
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
                  <span class="w-7 shrink-0 text-right font-mono text-xs text-muted">{{ move.effectivePower }}</span>
                  <span :class="['shrink-0 rounded-full border px-1.5 py-0.5 text-[11px] font-bold', multiplierBadgeClass(move.multiplier)]">{{ formatMultiplier(move.multiplier) }}</span>
                </button>
              </div>
            </div>
          </div>
          <!-- B moves vs A -->
          <div class="flex flex-col p-5">
            <p class="mb-3 text-[11px] font-semibold uppercase tracking-widest text-muted">
              {{ t("compare.moves_vs", { name: capitalize(pokemonA.name) }) }}
            </p>
            <div
              v-if="selectedDamageBvsA"
              class="mb-3 rounded-lg border border-accent/15 bg-white/80 px-3 py-2"
            >
              <div class="mb-2 flex flex-wrap items-start justify-between gap-2">
                <div>
                  <p class="text-sm font-semibold capitalize text-text">{{ selectedDamageBvsA.move.display_name ?? selectedDamageBvsA.move.name }}</p>
                  <label class="mt-1 inline-flex cursor-pointer items-center gap-1.5 font-mono text-[10px] font-bold uppercase tracking-wide text-muted transition hover:text-text">
                    <input
                      v-model="criticalBvsA"
                      type="checkbox"
                      class="h-3.5 w-3.5 accent-accent"
                      :aria-label="`${selectedDamageBvsA.move.display_name ?? selectedDamageBvsA.move.name} ${t('compare.critical')}`"
                    />
                    {{ t("compare.critical") }}
                  </label>
                </div>
                <div class="flex shrink-0 flex-wrap items-center justify-end gap-1">
                  <span
                    v-if="formatCriticalModifier(selectedDamageBvsA.calculation)"
                    class="rounded-full border border-rose-200 bg-rose-50 px-1.5 py-0.5 font-mono text-[10px] font-bold text-rose-700"
                  >{{ formatCriticalModifier(selectedDamageBvsA.calculation) }}</span>
                  <span
                    v-if="formatWeatherDamageModifier(selectedDamageBvsA.calculation)"
                    class="rounded-full border border-amber-200 bg-amber-50 px-1.5 py-0.5 font-mono text-[10px] font-bold text-amber-700"
                  >{{ formatWeatherDamageModifier(selectedDamageBvsA.calculation) }}</span>
                  <span
                    v-if="formatStatusDamageModifier(selectedDamageBvsA.calculation)"
                    class="rounded-full border border-red-200 bg-red-50 px-1.5 py-0.5 font-mono text-[10px] font-bold text-red-600"
                  >{{ formatStatusDamageModifier(selectedDamageBvsA.calculation) }}</span>
                  <span
                    v-if="formatStatusResidualModifier(selectedDamageBvsA.calculation)"
                    class="rounded-full border border-violet-200 bg-violet-50 px-1.5 py-0.5 font-mono text-[10px] font-bold text-violet-700"
                  >{{ formatStatusResidualModifier(selectedDamageBvsA.calculation) }}</span>
                  <span
                    v-for="hazardLabel in formatEntryHazardModifiers(selectedDamageBvsA.calculation)"
                    :key="`b-entry-hazard-${hazardLabel}`"
                    class="rounded-full border border-stone-200 bg-stone-50 px-1.5 py-0.5 font-mono text-[10px] font-bold text-stone-700"
                  >{{ hazardLabel }}</span>
                  <span
                    v-for="weatherLabel in formatWeatherResidualModifiers(selectedDamageBvsA.calculation)"
                    :key="`b-weather-residual-${weatherLabel}`"
                    class="rounded-full border border-amber-200 bg-amber-50 px-1.5 py-0.5 font-mono text-[10px] font-bold text-amber-700"
                  >{{ weatherLabel }}</span>
                  <span
                    v-for="abilityLabel in formatAbilityDamageModifiers(selectedDamageBvsA.calculation)"
                    :key="`b-ability-${abilityLabel}`"
                    class="rounded-full border border-indigo-200 bg-indigo-50 px-1.5 py-0.5 font-mono text-[10px] font-bold text-indigo-700"
                  >{{ abilityLabel }}</span>
                  <span :class="['rounded-full border px-1.5 py-0.5 text-[11px] font-bold', multiplierBadgeClass(selectedDamageBvsA.move.multiplier)]">{{ formatMultiplier(selectedDamageBvsA.move.multiplier) }}</span>
                </div>
              </div>
              <div>
                <p class="font-mono text-[10px] uppercase tracking-wide text-muted">{{ t("compare.damage_range") }}</p>
                <p class="font-mono font-bold text-text">{{ formatDamageRange(selectedDamageBvsA.calculation) }} HP</p>
                <p class="font-mono text-[11px] text-muted">
                  {{ formatDamagePercentRange(selectedDamageBvsA.calculation) }} {{ formatKoSummary(selectedDamageBvsA.calculation) }}
                </p>
              </div>
            </div>
            <p v-if="movesBQuery.isPending.value" class="text-xs text-muted">{{ t("compare.loading_moves") }}</p>
            <p v-else-if="!damageMovesBvsA.length" class="text-xs text-muted">{{ t("compare.no_damage_moves") }}</p>
            <div v-else class="max-h-64 space-y-0.5 overflow-y-auto pr-1 md:max-h-96">
              <div
                v-for="move in damageMovesBvsA"
                :key="move.name"
                class="rounded-lg"
              >
                <button
                  type="button"
                  class="flex w-full flex-wrap items-center gap-1.5 rounded-lg border px-2 py-1.5 text-left transition"
                  :class="moveRowClass(move, selectedMoveBvsA, knownMoveNamesB)"
                  @click="selectedMoveBvsA = move.name"
                >
                  <TypeEffectivenessBadge
                    v-if="move.effectiveType"
                    :type="move.effectiveType"
                    mode="move"
                    badge-class="shrink-0 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide"
                  />
                  <span class="min-w-28 flex-1 truncate text-xs capitalize text-text">{{ move.display_name ?? move.name }}</span>
                  <span
                    v-if="knownMoveNamesB.includes(move.name)"
                    class="shrink-0 rounded border border-accent/20 bg-accent/10 px-1.5 py-0.5 font-mono text-[9px] font-semibold uppercase tracking-wide text-accent"
                  >
                    {{ t("compare.stored.known_move") }}
                  </span>
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
                  <span class="w-7 shrink-0 text-right font-mono text-xs text-muted">{{ move.effectivePower }}</span>
                  <span :class="['shrink-0 rounded-full border px-1.5 py-0.5 text-[11px] font-bold', multiplierBadgeClass(move.multiplier)]">{{ formatMultiplier(move.multiplier) }}</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </article>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, ref, watch } from "vue";
import { RouterLink, useRoute, useRouter } from "vue-router";
import { useQueries, useQuery } from "@tanstack/vue-query";
import type { Pokemon, PokemonAbility, PokemonListItem, PokemonMove, MoveLearnMethod } from "@/types";
import { fetchPokemon, fetchPokemonList, fetchPokemonMoves } from "@/api/client";
import TypeEffectivenessBadge from "@/components/TypeEffectivenessBadge.vue";
import { t, labelType, labelStatShort, labelMoveCategory, labelLearnMethod, useLocale } from "@/i18n";
import { getTypeChipStyle } from "@/constants/pokemonTypes";
import { getAttackMultiplierForTypes } from "@/constants/typeEffectiveness";
import { POKEMON_NATURES, getNatureById, type PokemonNature } from "@/constants/natures";
import { useDebouncedValue } from "@/composables/useDebouncedValue";
import { formatLearnMethodLabels } from "@/utils/moveLearnMethods";
import {
  DAMAGE_EV,
  DAMAGE_IV,
  DAMAGE_LEVEL,
  DAMAGE_STAGE,
  calculatePokemonStat,
  calculateMoveDamage,
  getAbilityAdjustedTypeEffectiveness,
  getAbilityWeather,
  getEffectivePokemonStatus,
  getMoveDamageProfile,
  isWeatherSuppressedByAbility,
  type BattleAbility,
  type BattleWeather,
  type PokemonStatus,
  type DamageSideSettings,
  type DamageCalculation,
  type EntryHazards,
} from "@/utils/pokemmoDamage";
import {
  decodeStoredMemberRef,
  encodeStoredMemberRef,
  findStoredMember,
  loadStoredTeams,
  type StoredPokemonBuild,
} from "@/utils/localTeams";

const route = useRoute();
const router = useRouter();
const { locale } = useLocale();

const STAT_ORDER = ["hp", "attack", "defense", "special-attack", "special-defense", "speed"] as const;
type StatName = (typeof STAT_ORDER)[number];
type StatIvEvSettings = Record<StatName, { iv: number; ev: number; stage: number }>;
const WEATHER_OPTIONS: BattleWeather[] = ["clear", "sun", "rain", "sandstorm", "hail"];
const STATUS_OPTIONS: PokemonStatus[] = ["none", "burn", "paralysis", "poison", "toxic", "sleep", "freeze"];
const HAZARD_LAYER_OPTIONS = [0, 1, 2, 3] as const;
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
  const storedKey = side === "a" ? "teamA" : "teamB";
  router.replace({ query: { ...route.query, [side]: id ?? undefined, [storedKey]: undefined } });
}

function swapPokemon() {
  const tmpEdit = isEditingA.value;
  isEditingA.value = isEditingB.value;
  isEditingB.value = tmpEdit;
  const tmpSettings = statSettingsA.value;
  statSettingsA.value = statSettingsB.value;
  statSettingsB.value = tmpSettings;
  const tmpNature = selectedNatureA.value;
  selectedNatureA.value = selectedNatureB.value;
  selectedNatureB.value = tmpNature;
  const tmpStatus = selectedStatusA.value;
  selectedStatusA.value = selectedStatusB.value;
  selectedStatusB.value = tmpStatus;
  const tmpAbility = selectedAbilityA.value;
  selectedAbilityA.value = selectedAbilityB.value;
  selectedAbilityB.value = tmpAbility;
  const tmpHazards = entryHazardsA.value;
  entryHazardsA.value = entryHazardsB.value;
  entryHazardsB.value = tmpHazards;
  const tmpCurrentHpPercent = currentHpPercentA.value;
  currentHpPercentA.value = currentHpPercentB.value;
  currentHpPercentB.value = tmpCurrentHpPercent;
  const tmpKnownMoves = knownMoveNamesA.value;
  knownMoveNamesA.value = knownMoveNamesB.value;
  knownMoveNamesB.value = tmpKnownMoves;
  const tmpStoredRef = appliedStoredRefA.value;
  appliedStoredRefA.value = appliedStoredRefB.value;
  appliedStoredRefB.value = tmpStoredRef;
  selectedMoveAvsB.value = null;
  selectedMoveBvsA.value = null;
  criticalAvsB.value = false;
  criticalBvsA.value = false;
  router.replace({
    query: {
      ...route.query,
      a: idB.value ?? undefined,
      b: idA.value ?? undefined,
      teamA: route.query.teamB ?? undefined,
      teamB: route.query.teamA ?? undefined,
    }
  });
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
const selectedMoveAvsB = ref<string | null>(null);
const selectedMoveBvsA = ref<string | null>(null);
const knownMoveNamesA = ref<string[]>([]);
const knownMoveNamesB = ref<string[]>([]);
const appliedStoredRefA = ref("");
const appliedStoredRefB = ref("");
const criticalAvsB = ref(false);
const criticalBvsA = ref(false);
const calculatorLevel = ref(DAMAGE_LEVEL);
const selectedWeather = ref<BattleWeather>("clear");
const statSettingsA = ref(createDefaultStatSettings());
const statSettingsB = ref(createDefaultStatSettings());
const selectedNatureA = ref<string | null>(null);
const selectedNatureB = ref<string | null>(null);
const selectedStatusA = ref<PokemonStatus>("none");
const selectedStatusB = ref<PokemonStatus>("none");
const selectedAbilityA = ref<BattleAbility>(null);
const selectedAbilityB = ref<BattleAbility>(null);
const entryHazardsA = ref<EntryHazards>(createDefaultEntryHazards());
const entryHazardsB = ref<EntryHazards>(createDefaultEntryHazards());
const currentHpPercentA = ref(100);
const currentHpPercentB = ref(100);
const natureSearchA = ref("");
const natureSearchB = ref("");
const showNatureDropA = ref(false);
const showNatureDropB = ref(false);
const inputRefA = ref<HTMLInputElement | null>(null);
const inputRefB = ref<HTMLInputElement | null>(null);

const storedTeams = ref(loadStoredTeams());
const storedImportA = computed(() => typeof route.query.teamA === "string" ? route.query.teamA : "");
const storedImportB = computed(() => typeof route.query.teamB === "string" ? route.query.teamB : "");
const storedPokemonIds = computed(() => [
  ...new Set(storedTeams.value.flatMap(team => team.members.map(member => member.pokemonId)))
]);
const storedPokemonResults = useQueries({
  queries: computed(() => storedPokemonIds.value.map(id => ({
    queryKey: ["pokemon", locale.value, id] as const,
    queryFn: () => fetchPokemon(id),
  }))),
});
const storedPokemonById = computed(() => {
  const entries: [number, Pokemon][] = [];
  storedPokemonIds.value.forEach((id, index) => {
    const pokemon = storedPokemonResults.value[index]?.data?.data ?? null;
    if (pokemon) entries.push([id, pokemon]);
  });
  return new Map(entries);
});
const storedBuildOptions = computed(() =>
  storedTeams.value.flatMap(team =>
    team.members.map(member => {
      const pokemon = storedPokemonById.value.get(member.pokemonId);
      const pokemonLabel = pokemon?.name ?? `#${formatId(member.pokemonId)}`;
      return {
        value: encodeStoredMemberRef(team.id, member.id),
        label: `${team.name} - ${pokemonLabel}`,
        member,
      };
    })
  )
);

function createDefaultStatSettings(): StatIvEvSettings {
  return Object.fromEntries(
    STAT_ORDER.map((stat) => [stat, { iv: DAMAGE_IV, ev: DAMAGE_EV, stage: DAMAGE_STAGE }])
  ) as StatIvEvSettings;
}

function createDefaultEntryHazards(): EntryHazards {
  return { spikes: 0, stealthRock: false };
}

function clampWholeNumber(value: unknown, min: number, max: number, fallback: number): number {
  const numericValue = Number(value);
  if (!Number.isFinite(numericValue)) {
    return fallback;
  }
  return Math.min(max, Math.max(min, Math.trunc(numericValue)));
}

function clampBoundedStatInput(event: Event, max: number): number {
  const input = event.target as HTMLInputElement | null;
  const digits = (input?.value ?? "").replace(/\D/g, "").slice(0, String(max).length);
  const nextValue = digits ? clampWholeNumber(digits, 0, max, 0) : 0;
  if (input) {
    input.value = String(nextValue);
  }
  return nextValue;
}

function onComparisonIvInput(settings: StatIvEvSettings, stat: StatName, event: Event) {
  settings[stat].iv = clampBoundedStatInput(event, 31);
}

function onComparisonEvInput(settings: StatIvEvSettings, stat: StatName, event: Event) {
  settings[stat].ev = clampBoundedStatInput(event, 252);
}

const calculatorLevelValue = computed(() =>
  clampWholeNumber(calculatorLevel.value, 1, 100, DAMAGE_LEVEL)
);

const battleWeather = computed(() => selectedWeather.value);
const weatherSuppressedByAbility = computed(() =>
  isWeatherSuppressedByAbility(selectedAbilityA.value) || isWeatherSuppressedByAbility(selectedAbilityB.value)
);

function applyAbilityWeather(ability: BattleAbility) {
  const abilityWeather = getAbilityWeather(ability);
  if (abilityWeather) {
    selectedWeather.value = abilityWeather;
  }
}

function getEffectiveStage(settings: StatIvEvSettings, stat: StatName): number {
  if (stat === "hp") {
    return DAMAGE_STAGE;
  }
  const stage = clampWholeNumber(settings[stat]?.stage, -6, 6, DAMAGE_STAGE);
  return Math.min(6, Math.max(-6, stage));
}

function clampStageInput(settings: StatIvEvSettings, stat: StatName) {
  settings[stat].stage = stat === "hp"
    ? DAMAGE_STAGE
    : clampWholeNumber(settings[stat].stage, -6, 6, DAMAGE_STAGE);
}

function clampCurrentHpPercent(side: "a" | "b") {
  if (side === "a") {
    currentHpPercentA.value = clampWholeNumber(currentHpPercentA.value, 1, 100, 100);
    return;
  }
  currentHpPercentB.value = clampWholeNumber(currentHpPercentB.value, 1, 100, 100);
}

function getStatSettings(
  settings: StatIvEvSettings,
  stat: StatName,
  nature: PokemonNature | null = null,
  status: PokemonStatus = "none",
  ability: BattleAbility = null
) {
  return {
    level: calculatorLevelValue.value,
    iv: clampWholeNumber(settings[stat]?.iv, 0, 31, DAMAGE_IV),
    ev: clampWholeNumber(settings[stat]?.ev, 0, 252, DAMAGE_EV),
    stage: getEffectiveStage(settings, stat),
    nature: nature ? { increasedStat: nature.increasedStat, decreasedStat: nature.decreasedStat } : null,
    weather: battleWeather.value,
    status,
    ability,
    weatherSuppressed: weatherSuppressedByAbility.value,
  };
}

function getSideDamageSettings(
  settings: StatIvEvSettings,
  nature: PokemonNature | null,
  status: PokemonStatus,
  ability: BattleAbility,
  hazards: EntryHazards,
  currentHpPercent: number
): DamageSideSettings {
  const ivs: Record<string, number> = {};
  const evs: Record<string, number> = {};
  const stages: Record<string, number> = {};
  for (const stat of STAT_ORDER) {
    const statSettings = getStatSettings(settings, stat, nature, status, ability);
    ivs[stat] = statSettings.iv;
    evs[stat] = statSettings.ev;
    stages[stat] = statSettings.stage ?? DAMAGE_STAGE;
  }
  return {
    level: calculatorLevelValue.value,
    ivs,
    evs,
    stages,
    currentHpPercent: clampWholeNumber(currentHpPercent, 1, 100, 100),
    nature: nature ? { increasedStat: nature.increasedStat, decreasedStat: nature.decreasedStat } : null,
    weather: battleWeather.value,
    status,
    ability,
    hazards: {
      spikes: clampWholeNumber(hazards.spikes, 0, 3, 0),
      stealthRock: hazards.stealthRock,
    },
    weatherSuppressed: weatherSuppressedByAbility.value,
  };
}

const natureA = computed(() => getNatureById(selectedNatureA.value));
const natureB = computed(() => getNatureById(selectedNatureB.value));
const damageSettingsA = computed(() =>
  getSideDamageSettings(statSettingsA.value, natureA.value, selectedStatusA.value, selectedAbilityA.value, entryHazardsA.value, currentHpPercentA.value)
);
const damageSettingsB = computed(() =>
  getSideDamageSettings(statSettingsB.value, natureB.value, selectedStatusB.value, selectedAbilityB.value, entryHazardsB.value, currentHpPercentB.value)
);
const selectedAbilityDescriptionA = computed(() => getAbilityDescription(pokemonA.value, selectedAbilityA.value));
const selectedAbilityDescriptionB = computed(() => getAbilityDescription(pokemonB.value, selectedAbilityB.value));

watch([locale, selectedNatureA], () => {
  natureSearchA.value = natureA.value ? formatNatureOption(natureA.value) : "";
});
watch([locale, selectedNatureB], () => {
  natureSearchB.value = natureB.value ? formatNatureOption(natureB.value) : "";
});

function getNatureName(nature: PokemonNature): string {
  return nature.names[locale.value];
}

function labelWeather(weather: BattleWeather): string {
  return t(`compare.weather.${weather}`);
}

function labelStatus(status: PokemonStatus): string {
  return t(`compare.status.${status}`);
}

function formatAbilityName(abilityName: BattleAbility): string {
  if (!abilityName) {
    return "";
  }
  const ability = [...(pokemonA.value?.abilities ?? []), ...(pokemonB.value?.abilities ?? [])]
    .find((entry) => entry.name === abilityName);
  return ability?.display_name ?? abilityName.split("-").map(capitalize).join(" ");
}

function formatAbilityOption(ability: PokemonAbility): string {
  return ability.display_name ?? ability.name.split("-").map(capitalize).join(" ");
}

function getAbilityDescription(pokemon: Pokemon | null, abilityName: BattleAbility): string {
  if (!pokemon || !abilityName) {
    return "";
  }
  return pokemon.abilities.find((ability) => ability.name === abilityName)?.description.trim() ?? "";
}

function getValidSelectedAbility(pokemon: Pokemon | null, abilityName: BattleAbility): BattleAbility {
  if (!pokemon?.abilities.length) {
    return null;
  }
  if (abilityName && pokemon.abilities.some((ability) => ability.name === abilityName)) {
    return abilityName;
  }
  return pokemon.abilities[0].name;
}

function createStatSettingsFromStoredBuild(build: StoredPokemonBuild): StatIvEvSettings {
  return Object.fromEntries(
    STAT_ORDER.map((stat) => [
      stat,
      {
        iv: clampWholeNumber(build.ivs[stat], 0, 31, DAMAGE_IV),
        ev: clampWholeNumber(build.evs[stat], 0, 252, DAMAGE_EV),
        stage: DAMAGE_STAGE,
      }
    ])
  ) as StatIvEvSettings;
}

function getStoredBuildFromImport(raw: string): StoredPokemonBuild | null {
  const ref = decodeStoredMemberRef(raw);
  return ref ? findStoredMember(storedTeams.value, ref) : null;
}

function applyStoredBuild(side: "a" | "b", build: StoredPokemonBuild, pokemon: Pokemon) {
  const ability = getValidSelectedAbility(pokemon, build.ability);
  const knownMoves = build.moves.filter(Boolean);
  if (side === "a") {
    statSettingsA.value = createStatSettingsFromStoredBuild(build);
    selectedNatureA.value = build.nature;
    selectedAbilityA.value = ability;
    knownMoveNamesA.value = knownMoves;
    selectedMoveAvsB.value = null;
    isEditingA.value = false;
    return;
  }
  statSettingsB.value = createStatSettingsFromStoredBuild(build);
  selectedNatureB.value = build.nature;
  selectedAbilityB.value = ability;
  knownMoveNamesB.value = knownMoves;
  selectedMoveBvsA.value = null;
  isEditingB.value = false;
}

function maybeApplyStoredBuild(side: "a" | "b") {
  const raw = side === "a" ? storedImportA.value : storedImportB.value;
  const appliedRef = side === "a" ? appliedStoredRefA : appliedStoredRefB;
  if (!raw) {
    appliedRef.value = "";
    return;
  }
  if (appliedRef.value === raw) {
    return;
  }
  const build = getStoredBuildFromImport(raw);
  const pokemon = side === "a" ? pokemonA.value : pokemonB.value;
  if (!build || !pokemon || pokemon.id !== build.pokemonId) {
    return;
  }
  applyStoredBuild(side, build, pokemon);
  appliedRef.value = raw;
}

function onStoredImportChange(side: "a" | "b", event: Event) {
  const select = event.target as HTMLSelectElement | null;
  const raw = select?.value ?? "";
  const storedKey = side === "a" ? "teamA" : "teamB";
  const appliedRef = side === "a" ? appliedStoredRefA : appliedStoredRefB;
  appliedRef.value = "";
  if (!raw) {
    if (side === "a") {
      knownMoveNamesA.value = [];
    } else {
      knownMoveNamesB.value = [];
    }
    router.replace({ query: { ...route.query, [storedKey]: undefined } });
    return;
  }
  const build = getStoredBuildFromImport(raw);
  if (!build) {
    return;
  }
  router.replace({
    query: {
      ...route.query,
      [side]: build.pokemonId,
      [storedKey]: raw,
    }
  });
}

function formatNatureModifier(nature: PokemonNature): string {
  if (!nature.increasedStat || !nature.decreasedStat) {
    return t("compare.nature_neutral");
  }
  return `+${labelStatShort(nature.increasedStat)}, -${labelStatShort(nature.decreasedStat)}`;
}

function getNatureStatModifier(nature: PokemonNature | null, stat: StatName): 1 | -1 | 0 {
  if (!nature || stat === "hp") {
    return 0;
  }
  if (nature.increasedStat === stat) {
    return 1;
  }
  if (nature.decreasedStat === stat) {
    return -1;
  }
  return 0;
}

function formatNatureStatModifier(modifier: 1 | -1 | 0): string {
  if (modifier > 0) {
    return "+10%";
  }
  if (modifier < 0) {
    return "-10%";
  }
  return "";
}

function hasPokemonType(pokemon: Pokemon | null, typeName: string): boolean {
  return pokemon?.types.some((type) => type.toLowerCase() === typeName) ?? false;
}

function getStatModifierLabel(
  pokemon: Pokemon | null,
  nature: PokemonNature | null,
  stat: StatName,
  status: PokemonStatus,
  ability: BattleAbility
): string {
  const modifiers: string[] = [];
  const natureModifier = getNatureStatModifier(nature, stat);
  const effectiveStatus = getEffectivePokemonStatus(status, ability);
  if (natureModifier) {
    modifiers.push(formatNatureStatModifier(natureModifier));
  }
  if (stat === "special-defense" && battleWeather.value === "sandstorm" && !weatherSuppressedByAbility.value && hasPokemonType(pokemon, "rock")) {
    modifiers.push("+50%");
  }
  if ((ability === "huge-power" || ability === "pure-power") && stat === "attack") {
    modifiers.push("+100%");
  }
  if (ability === "guts" && stat === "attack" && effectiveStatus !== "none") {
    modifiers.push("+50%");
  }
  if (ability === "marvel-scale" && stat === "defense" && effectiveStatus !== "none") {
    modifiers.push("+50%");
  }
  if (ability === "solar-power" && stat === "special-attack" && battleWeather.value === "sun" && !weatherSuppressedByAbility.value) {
    modifiers.push("+50%");
  }
  if ((ability === "chlorophyll" && battleWeather.value === "sun" || ability === "swift-swim" && battleWeather.value === "rain") && stat === "speed" && !weatherSuppressedByAbility.value) {
    modifiers.push("+100%");
  }
  if (ability === "quick-feet" && stat === "speed" && effectiveStatus !== "none") {
    modifiers.push("+50%");
  }
  if (stat === "attack" && effectiveStatus === "burn" && ability !== "guts") {
    modifiers.push("-50%");
  }
  if (stat === "speed" && effectiveStatus === "paralysis") {
    modifiers.push("-50%");
  }
  return modifiers.join(" ");
}

function statModifierBadgeClass(label: string): string {
  const hasPositive = label.includes("+");
  const hasNegative = label.includes("-");
  if (hasPositive && hasNegative) {
    return "border-amber-200 bg-amber-50 text-amber-700";
  }
  if (hasPositive) {
    return "border-green-200 bg-green-50 text-green-700";
  }
  if (hasNegative) {
    return "border-red-200 bg-red-50 text-red-600";
  }
  return "border-black/10 bg-black/5 text-muted";
}

function formatNatureOption(nature: PokemonNature): string {
  return `${getNatureName(nature)} (${formatNatureModifier(nature)})`;
}

function filterNatureOptions(query: string): PokemonNature[] {
  const normalizedQuery = query.trim().toLowerCase();
  if (!normalizedQuery) {
    return POKEMON_NATURES;
  }
  return POKEMON_NATURES.filter((nature) => {
    const searchable = [
      nature.id,
      nature.names.en,
      nature.names.it,
      formatNatureModifier(nature),
    ].join(" ").toLowerCase();
    return searchable.includes(normalizedQuery);
  });
}

const natureResultsA = computed(() => filterNatureOptions(natureSearchA.value));
const natureResultsB = computed(() => filterNatureOptions(natureSearchB.value));

function selectNature(side: "a" | "b", nature: PokemonNature) {
  if (side === "a") {
    selectedNatureA.value = nature.id;
    natureSearchA.value = formatNatureOption(nature);
    showNatureDropA.value = false;
    return;
  }
  selectedNatureB.value = nature.id;
  natureSearchB.value = formatNatureOption(nature);
  showNatureDropB.value = false;
}

function clearNature(side: "a" | "b") {
  if (side === "a") {
    selectedNatureA.value = null;
    natureSearchA.value = "";
    showNatureDropA.value = false;
    return;
  }
  selectedNatureB.value = null;
  natureSearchB.value = "";
  showNatureDropB.value = false;
}

function onNatureInput(side: "a" | "b") {
  if (side === "a") {
    selectedNatureA.value = null;
    showNatureDropA.value = true;
    return;
  }
  selectedNatureB.value = null;
  showNatureDropB.value = true;
}

function onNatureBlur(side: "a" | "b") {
  setTimeout(() => {
    if (side === "a") {
      showNatureDropA.value = false;
      natureSearchA.value = natureA.value ? formatNatureOption(natureA.value) : "";
      return;
    }
    showNatureDropB.value = false;
    natureSearchB.value = natureB.value ? formatNatureOption(natureB.value) : "";
  }, 150);
}

function selectA(p: PokemonListItem) {
  knownMoveNamesA.value = [];
  appliedStoredRefA.value = "";
  setId("a", p.id);
  searchA.value = "";
  showDropA.value = false;
  isEditingA.value = false;
  selectedMoveAvsB.value = null;
  selectedMoveBvsA.value = null;
}
function selectB(p: PokemonListItem) {
  knownMoveNamesB.value = [];
  appliedStoredRefB.value = "";
  setId("b", p.id);
  searchB.value = "";
  showDropB.value = false;
  isEditingB.value = false;
  selectedMoveAvsB.value = null;
  selectedMoveBvsA.value = null;
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

watch(pokemonA, (pokemon) => {
  selectedAbilityA.value = getValidSelectedAbility(pokemon, selectedAbilityA.value);
}, { immediate: true });
watch(pokemonB, (pokemon) => {
  selectedAbilityB.value = getValidSelectedAbility(pokemon, selectedAbilityB.value);
}, { immediate: true });
watch(selectedAbilityA, (ability) => {
  applyAbilityWeather(ability);
}, { immediate: true });
watch(selectedAbilityB, (ability) => {
  applyAbilityWeather(ability);
}, { immediate: true });
watch([pokemonA, storedImportA], () => {
  maybeApplyStoredBuild("a");
}, { immediate: true });
watch([pokemonB, storedImportB], () => {
  maybeApplyStoredBuild("b");
}, { immediate: true });

// ── Section 1: Statistics ───────────────────────────────────────────────────
function statVal(
  pokemon: Pokemon | null,
  stat: StatName,
  settings: StatIvEvSettings,
  nature: PokemonNature | null,
  status: PokemonStatus,
  ability: BattleAbility
): number {
  return pokemon ? calculatePokemonStat(pokemon, stat, getStatSettings(settings, stat, nature, status, ability)) : 0;
}

const statRows = computed(() => {
  if (!pokemonA.value || !pokemonB.value) return [];
  return STAT_ORDER.map((stat) => {
    const a = statVal(pokemonA.value, stat, statSettingsA.value, natureA.value, selectedStatusA.value, selectedAbilityA.value);
    const b = statVal(pokemonB.value, stat, statSettingsB.value, natureB.value, selectedStatusB.value, selectedAbilityB.value);
    return { stat, a, b, max: Math.max(a, b, 1), aWins: a > b, bWins: b > a };
  });
});

const physicalA = computed(() => {
  const atk = statVal(pokemonA.value, "attack", statSettingsA.value, natureA.value, selectedStatusA.value, selectedAbilityA.value);
  const def = statVal(pokemonB.value, "defense", statSettingsB.value, natureB.value, selectedStatusB.value, selectedAbilityB.value);
  return { atk, def, diff: atk - def };
});
const specialA = computed(() => {
  const spa = statVal(pokemonA.value, "special-attack", statSettingsA.value, natureA.value, selectedStatusA.value, selectedAbilityA.value);
  const spd = statVal(pokemonB.value, "special-defense", statSettingsB.value, natureB.value, selectedStatusB.value, selectedAbilityB.value);
  return { spa, spd, diff: spa - spd };
});
const physicalB = computed(() => {
  const atk = statVal(pokemonB.value, "attack", statSettingsB.value, natureB.value, selectedStatusB.value, selectedAbilityB.value);
  const def = statVal(pokemonA.value, "defense", statSettingsA.value, natureA.value, selectedStatusA.value, selectedAbilityA.value);
  return { atk, def, diff: atk - def };
});
const specialB = computed(() => {
  const spa = statVal(pokemonB.value, "special-attack", statSettingsB.value, natureB.value, selectedStatusB.value, selectedAbilityB.value);
  const spd = statVal(pokemonA.value, "special-defense", statSettingsA.value, natureA.value, selectedStatusA.value, selectedAbilityA.value);
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
type ScoredMove = PokemonMove & {
  multiplier: number;
  effectiveType: string;
  effectivePower: number;
  weatherMultiplier: number;
};
type SelectedDamage = {
  move: ScoredMove;
  calculation: DamageCalculation;
};

function scoreDamageMove(
  move: PokemonMove,
  defender: Pokemon,
  attackerStatus: PokemonStatus,
  defenderStatus: PokemonStatus,
  attackerAbility: BattleAbility,
  defenderAbility: BattleAbility
): ScoredMove | null {
  if (move.power === null || move.type === null) return null;
  const profile = getMoveDamageProfile(
    move,
    battleWeather.value,
    attackerStatus,
    defenderStatus,
    attackerAbility,
    defenderAbility,
    weatherSuppressedByAbility.value
  );
  if (profile.type === null || profile.power === null) return null;
  const baseMultiplier = getAttackMultiplierForTypes(profile.type, defender.types);
  const multiplier = getAbilityAdjustedTypeEffectiveness(
    move,
    profile.type,
    baseMultiplier,
    attackerAbility,
    defenderAbility
  );
  return {
    ...move,
    effectiveType: profile.type,
    effectivePower: profile.power,
    weatherMultiplier: profile.weatherMultiplier,
    multiplier,
  };
}

function sortDamageMoves(a: ScoredMove, b: ScoredMove): number {
  return (
    b.multiplier - a.multiplier ||
    b.effectivePower * b.weatherMultiplier - a.effectivePower * a.weatherMultiplier ||
    (b.power ?? 0) - (a.power ?? 0)
  );
}

function sortDamageMovesWithKnownPriority(moves: ScoredMove[], knownNames: string[]): ScoredMove[] {
  const knownOrder = new Map(knownNames.map((name, index) => [name, index]));
  if (!knownOrder.size) {
    return [...moves].sort(sortDamageMoves);
  }
  return [...moves].sort((a, b) => {
    const knownA = knownOrder.get(a.name);
    const knownB = knownOrder.get(b.name);
    if (knownA !== undefined && knownB !== undefined) {
      return knownA - knownB;
    }
    if (knownA !== undefined) {
      return -1;
    }
    if (knownB !== undefined) {
      return 1;
    }
    return sortDamageMoves(a, b);
  });
}

const damageMovesAvsB = computed((): ScoredMove[] => {
  if (!pokemonB.value) return [];
  const knownMoves = knownMoveNamesA.value.filter(Boolean);
  const scoredMoves = movesA.value
    .map((move) => scoreDamageMove(move, pokemonB.value!, selectedStatusA.value, selectedStatusB.value, selectedAbilityA.value, selectedAbilityB.value))
    .filter((move): move is ScoredMove => move !== null);
  return sortDamageMovesWithKnownPriority(scoredMoves, knownMoves);
});
const damageMovesBvsA = computed((): ScoredMove[] => {
  if (!pokemonA.value) return [];
  const knownMoves = knownMoveNamesB.value.filter(Boolean);
  const scoredMoves = movesB.value
    .map((move) => scoreDamageMove(move, pokemonA.value!, selectedStatusB.value, selectedStatusA.value, selectedAbilityB.value, selectedAbilityA.value))
    .filter((move): move is ScoredMove => move !== null);
  return sortDamageMovesWithKnownPriority(scoredMoves, knownMoves);
});

watch(damageMovesAvsB, (moves) => {
  if (!knownMoveNamesA.value.length) return;
  if (!selectedMoveAvsB.value || !moves.some((move) => move.name === selectedMoveAvsB.value)) {
    selectedMoveAvsB.value = moves[0]?.name ?? null;
  }
});
watch(damageMovesBvsA, (moves) => {
  if (!knownMoveNamesB.value.length) return;
  if (!selectedMoveBvsA.value || !moves.some((move) => move.name === selectedMoveBvsA.value)) {
    selectedMoveBvsA.value = moves[0]?.name ?? null;
  }
});

const selectedDamageAvsB = computed((): SelectedDamage | null => {
  if (!pokemonA.value || !pokemonB.value || !selectedMoveAvsB.value) return null;
  const move = damageMovesAvsB.value.find((entry) => entry.name === selectedMoveAvsB.value);
  if (!move) return null;
  const calculation = calculateMoveDamage(
    pokemonA.value,
    pokemonB.value,
    move,
    move.multiplier,
    damageSettingsA.value,
    damageSettingsB.value,
    { critical: criticalAvsB.value }
  );
  return calculation ? { move, calculation } : null;
});
const selectedDamageBvsA = computed((): SelectedDamage | null => {
  if (!pokemonA.value || !pokemonB.value || !selectedMoveBvsA.value) return null;
  const move = damageMovesBvsA.value.find((entry) => entry.name === selectedMoveBvsA.value);
  if (!move) return null;
  const calculation = calculateMoveDamage(
    pokemonB.value,
    pokemonA.value,
    move,
    move.multiplier,
    damageSettingsB.value,
    damageSettingsA.value,
    { critical: criticalBvsA.value }
  );
  return calculation ? { move, calculation } : null;
});

// ── Helpers ─────────────────────────────────────────────────────────────────
function formatId(id: number): string {
  return String(id).padStart(3, "0");
}

function statBarPct(value: number, maxValue: number): number {
  return Math.min(100, Math.round((value / Math.max(maxValue, 1)) * 100));
}

function formatMultiplier(mult: number): string {
  if (mult === 0) return "0×";
  if (Number.isInteger(mult)) return `${mult}×`;
  return `${mult.toFixed(2).replace(/0+$/, "").replace(/\.$/, "")}×`;
}

function formatDamageRange(calculation: DamageCalculation): string {
  if (calculation.minDamage === calculation.maxDamage) {
    return String(calculation.minDamage);
  }
  return `${calculation.minDamage}-${calculation.maxDamage}`;
}

function formatDamagePercentRange(calculation: DamageCalculation): string {
  return `${formatPercent(calculation.minPercent)}-${formatPercent(calculation.maxPercent)}`;
}

function formatCriticalModifier(calculation: DamageCalculation): string {
  if (calculation.criticalBlockedBy) {
    return `${formatAbilityName(calculation.criticalBlockedBy)} ${t("compare.critical")} ${t("compare.immune")}`;
  }
  if (!calculation.critical) {
    return "";
  }
  return `${t("compare.critical")} +${formatPercent((calculation.criticalMultiplier - 1) * 100)}`;
}

function formatWeatherDamageModifier(calculation: DamageCalculation): string {
  if (calculation.weatherMultiplier === 1) {
    return "";
  }
  return `${labelWeather(calculation.weather)} ${calculation.weatherMultiplier > 1 ? "+50%" : "-50%"}`;
}

function formatStatusDamageModifier(calculation: DamageCalculation): string {
  if (calculation.statusDamageMultiplier === 1) {
    return "";
  }
  return `${labelStatus(calculation.attackerStatus)} -50%`;
}

function formatStatusResidualModifier(calculation: DamageCalculation): string {
  if (calculation.statusResidualDamage <= 0) {
    return "";
  }
  return `${labelStatus(calculation.defenderStatus)} +${formatPercent((calculation.statusResidualDamage / calculation.defenderHp) * 100)} ${t("compare.residual")}`;
}

function formatEntryHazardBlocker(blocker: string): string {
  if (blocker === "flying") {
    return capitalize(labelType("flying"));
  }
  return formatAbilityName(blocker);
}

function formatEntryHazardModifiers(calculation: DamageCalculation): string[] {
  const labels: string[] = [];
  if (calculation.stealthRockDamage > 0) {
    labels.push(`${t("compare.stealth_rock")} +${formatPercent((calculation.stealthRockDamage / calculation.defenderHp) * 100)} ${t("compare.residual")}`);
  }
  if (calculation.spikesDamage > 0) {
    labels.push(`${t("compare.spikes")} ${calculation.spikesLayers} +${formatPercent((calculation.spikesDamage / calculation.defenderHp) * 100)} ${t("compare.residual")}`);
  }

  if (calculation.spikesBlockedBy === "magic-guard" && calculation.stealthRockBlockedBy === "magic-guard") {
    labels.push(`${formatAbilityName("magic-guard")} ${t("compare.entry_hazards")} ${t("compare.immune")}`);
    return labels;
  }
  if (calculation.stealthRockBlockedBy) {
    labels.push(`${formatEntryHazardBlocker(calculation.stealthRockBlockedBy)} ${t("compare.stealth_rock")} ${t("compare.immune")}`);
  }
  if (calculation.spikesBlockedBy) {
    labels.push(`${formatEntryHazardBlocker(calculation.spikesBlockedBy)} ${t("compare.spikes")} ${t("compare.immune")}`);
  }
  return labels;
}

function formatWeatherResidualModifiers(calculation: DamageCalculation): string[] {
  const labels: string[] = [];
  if (calculation.weatherResidualDamage > 0) {
    labels.push(`${labelWeather(calculation.weather)} +${formatPercent((calculation.weatherResidualDamage / calculation.defenderHp) * 100)} ${t("compare.residual")}`);
  } else if (calculation.weatherResidualDamage < 0) {
    labels.push(`${labelWeather(calculation.weather)} -${formatPercent(Math.abs(calculation.weatherResidualDamage / calculation.defenderHp) * 100)} ${t("compare.heal")}`);
  }
  if (calculation.weatherResidualBlockedBy) {
    labels.push(`${formatAbilityName(calculation.weatherResidualBlockedBy)} ${labelWeather(calculation.weather)} ${t("compare.immune")}`);
  }
  return labels;
}

function formatAbilityDamageModifiers(calculation: DamageCalculation): string[] {
  const labels: string[] = [];
  if (calculation.abilityBlockedBy) {
    labels.push(`${formatAbilityName(calculation.abilityBlockedBy)} ${t("compare.immune")}`);
  }
  for (const modifier of calculation.abilityDamageModifiers) {
    const delta = modifier.multiplier > 1
      ? `+${formatPercent((modifier.multiplier - 1) * 100)}`
      : `-${formatPercent((1 - modifier.multiplier) * 100)}`;
    labels.push(`${formatAbilityName(modifier.ability)} ${delta}`);
  }
  if (calculation.sturdyBlockedOhko) {
    labels.push(`${formatAbilityName("sturdy")} ${t("compare.ohko_block")}`);
  }
  const abilityResidualDamage =
    calculation.abilityResidualDamage +
    (calculation.statusResidualDamage < 0 ? calculation.statusResidualDamage : 0);
  if (abilityResidualDamage !== 0) {
    const residualLabel = abilityResidualDamage > 0 ? t("compare.residual") : t("compare.heal");
    const sign = abilityResidualDamage > 0 ? "+" : "-";
    labels.push(`${formatAbilityName(calculation.defenderAbility)} ${sign}${formatPercent(Math.abs(abilityResidualDamage / calculation.defenderHp) * 100)} ${residualLabel}`);
  }
  return labels;
}

function formatKoSummary(calculation: DamageCalculation): string {
  const ohko = `${formatPercent(calculation.ohkoChance)} OHKO`;
  if (calculation.ohkoChance >= 100) {
    return `(${ohko})`;
  }
  return `(${ohko}, ${formatPercent(calculation.twoHkoChance)} 2HKO)`;
}

function formatPercent(value: number): string {
  if (value === 0) return "0%";
  if (value === 100) return "100%";
  if (value > 0 && value < 0.1) return "<0.1%";
  return `${value.toFixed(1).replace(/\.0$/, "")}%`;
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

function moveRowClass(move: ScoredMove, selectedMoveName: string | null, knownMoveNames: string[]): string {
  const isKnownMove = knownMoveNames.includes(move.name);
  if (move.name === selectedMoveName) {
    return isKnownMove
      ? "border-accent/40 bg-accent/15 shadow-soft"
      : "border-accent/25 bg-accent/10 shadow-soft";
  }
  if (isKnownMove) {
    return "border-accent/30 bg-accent/5 hover:bg-accent/10";
  }
  if (move.multiplier === 0) {
    return "border-transparent opacity-45";
  }
  return "border-transparent hover:bg-black/5";
}

function diffBadgeClass(diff: number): string {
  if (diff > 0) return "border-green-200 bg-green-50 text-green-700";
  if (diff < 0) return "border-red-200 bg-red-50 text-red-600";
  return "border-black/10 bg-black/5 text-muted";
}
</script>
