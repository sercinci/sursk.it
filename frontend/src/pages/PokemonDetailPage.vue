<template>
  <section v-if="pokemon" class="space-y-6">
    <div class="card-surface relative rounded-3xl p-5 shadow-soft sm:p-8">
      <aside class="mx-auto mb-4 flex w-fit flex-col items-center sm:absolute sm:right-6 sm:top-6 sm:mb-0 sm:items-end">
        <div
          v-if="sprite"
          class="flex h-28 w-28 items-center justify-center rounded-xl border border-black/10 bg-white/85 p-1.5"
        >
          <img
            :src="sprite"
            :alt="pokemon.name"
            class="h-full w-full object-contain"
          />
        </div>

        <div class="mt-2 w-28 rounded-lg border border-black/10 bg-white/90 p-1.5">
          <p class="text-[10px] font-semibold uppercase tracking-wide text-muted">{{ t("pokemon.ev_yield") }}</p>
          <p v-if="!evYieldEntries.length" class="mt-1 text-[10px] text-muted">{{ t("pokemon.ev_none") }}</p>
          <ul v-else class="mt-1 flex gap-0.5">
            <li
              v-for="entry in evYieldEntries"
              :key="`ev-${entry.name}`"
              class="bg-white px-1.5 py-0.5 text-[10px] font-mono font-semibold leading-tight text-text"
            >
              +{{ entry.value }} {{ statShortLabel(entry.name) }}
            </li>
          </ul>
        </div>

        <div class="mt-2 w-28 sm:overflow-visible relative sm:min-h-9">
          <p v-if="evolutionLineLoading" class="text-center text-[10px] text-muted">{{ t("pokemon.evolution_loading") }}</p>
          <p
            v-else-if="!evolutionLine"
            class="text-center text-[10px] text-muted"
          >
            {{ t("pokemon.no_evolution_data") }}
          </p>
          <div
            v-else
            class="relative left-2/4 min-w-full w-max -translate-x-2/4 sm:absolute sm:left-auto sm:right-0 sm:translate-x-0"
          >
            <div
              class="flex items-center justify-center sm:justify-end"
              :class="hasMultipleEvolutionBranches ? 'flex-col gap-1 sm:flex-row sm:gap-3' : 'flex-row flex-nowrap gap-1'"
            >
              <div
                v-for="(branch, branchIndex) in evolutionDisplayBranches"
                :key="`evo-branch-${branchIndex}`"
                class="flex items-center gap-1"
              >
                <template
                  v-for="(entry, index) in evolutionLine.previous_chain"
                  :key="`evo-prev-${branchIndex}-${entry.pokemon.name}-${index}`"
                >
                  <RouterLink
                    v-if="entry.pokemon.id !== null"
                    :to="{ name: 'pokemon-detail', params: { id: entry.pokemon.id } }"
                    :title="formatLabel(entry.pokemon.name)"
                    class="inline-flex h-9 w-9 shrink-0 items-center justify-center rounded-md transition hover:bg-white/80"
                  >
                    <img
                      v-if="entry.pokemon.sprite"
                      :src="entry.pokemon.sprite"
                      :alt="entry.pokemon.name"
                      class="h-8 w-8 object-contain"
                    />
                    <div
                      v-else
                      class="flex h-8 w-8 items-center justify-center rounded bg-black/5 text-xs font-semibold text-muted"
                    >
                      ?
                    </div>
                  </RouterLink>
                  <div
                    v-else
                    :title="formatLabel(entry.pokemon.name)"
                    class="inline-flex h-9 w-9 shrink-0 items-center justify-center rounded-md"
                  >
                    <img
                      v-if="entry.pokemon.sprite"
                      :src="entry.pokemon.sprite"
                      :alt="entry.pokemon.name"
                      class="h-8 w-8 object-contain"
                    />
                    <div
                      v-else
                      class="flex h-8 w-8 items-center justify-center rounded bg-black/5 text-xs font-semibold text-muted"
                    >
                      ?
                    </div>
                  </div>

                  <div
                    class="inline-flex shrink-0 items-center gap-1 rounded-full border border-black/10 bg-amber-50 px-1.5 py-1 text-xs font-semibold text-amber-700"
                    :title="evolutionMethodTooltip(entry.method)"
                  >
                    <img
                      v-if="evolutionMethodIcon(entry.method)"
                      :src="evolutionMethodIcon(entry.method) ?? ''"
                      :alt="evolutionMethodLabel(entry.method)"
                      class="h-4 w-4 object-contain"
                    />
                    <span v-if="evolutionMethodBadgeLabel(entry.method)">
                      {{ evolutionMethodBadgeLabel(entry.method) }}
                    </span>
                  </div>
                </template>

                <RouterLink
                  v-if="evolutionLine.current.id !== null"
                  :to="{ name: 'pokemon-detail', params: { id: evolutionLine.current.id } }"
                  :title="formatLabel(evolutionLine.current.name)"
                  class="inline-flex h-9 w-9 shrink-0 items-center justify-center rounded-md transition hover:bg-white/80"
                >
                  <img
                    v-if="evolutionLine.current.sprite"
                    :src="evolutionLine.current.sprite"
                    :alt="evolutionLine.current.name"
                    class="h-8 w-8 object-contain"
                  />
                  <div
                    v-else
                    class="flex h-8 w-8 items-center justify-center rounded bg-black/5 text-xs font-semibold text-muted"
                  >
                    ?
                  </div>
                </RouterLink>
                <div
                  v-else
                  :title="formatLabel(evolutionLine.current.name)"
                  class="inline-flex h-9 w-9 shrink-0 items-center justify-center rounded-md"
                >
                  <img
                    v-if="evolutionLine.current.sprite"
                    :src="evolutionLine.current.sprite"
                    :alt="evolutionLine.current.name"
                    class="h-8 w-8 object-contain"
                  />
                  <div
                    v-else
                    class="flex h-8 w-8 items-center justify-center rounded bg-black/5 text-xs font-semibold text-muted"
                  >
                    ?
                  </div>
                </div>

                <template
                  v-for="(entry, index) in branch"
                  :key="`evo-next-${branchIndex}-${entry.pokemon.name}-${index}`"
                >
                  <div
                    class="inline-flex shrink-0 items-center gap-1 rounded-full border border-black/10 bg-amber-50 px-1.5 py-1 text-xs font-semibold text-amber-700"
                    :title="evolutionMethodTooltip(entry.method)"
                  >
                    <img
                      v-if="evolutionMethodIcon(entry.method)"
                      :src="evolutionMethodIcon(entry.method) ?? ''"
                      :alt="evolutionMethodLabel(entry.method)"
                      class="h-4 w-4 object-contain"
                    />
                    <span v-if="evolutionMethodBadgeLabel(entry.method)">
                      {{ evolutionMethodBadgeLabel(entry.method) }}
                    </span>
                  </div>

                  <RouterLink
                    v-if="entry.pokemon.id !== null"
                    :to="{ name: 'pokemon-detail', params: { id: entry.pokemon.id } }"
                    :title="formatLabel(entry.pokemon.name)"
                    class="inline-flex h-9 w-9 shrink-0 items-center justify-center rounded-md transition hover:bg-white/80"
                  >
                    <img
                      v-if="entry.pokemon.sprite"
                      :src="entry.pokemon.sprite"
                      :alt="entry.pokemon.name"
                      class="h-8 w-8 object-contain"
                    />
                    <div
                      v-else
                      class="flex h-8 w-8 items-center justify-center rounded bg-black/5 text-xs font-semibold text-muted"
                    >
                      ?
                    </div>
                  </RouterLink>
                  <div
                    v-else
                    :title="formatLabel(entry.pokemon.name)"
                    class="inline-flex h-9 w-9 shrink-0 items-center justify-center rounded-md"
                  >
                    <img
                      v-if="entry.pokemon.sprite"
                      :src="entry.pokemon.sprite"
                      :alt="entry.pokemon.name"
                      class="h-8 w-8 object-contain"
                    />
                    <div
                      v-else
                      class="flex h-8 w-8 items-center justify-center rounded bg-black/5 text-xs font-semibold text-muted"
                    >
                      ?
                    </div>
                  </div>
                </template>
              </div>
            </div>
          </div>
        </div>
      </aside>

      <div class="pr-0 sm:pr-36">
        <p class="font-mono text-xs uppercase tracking-[0.2em] text-muted">Pokémon #{{ pokemon.id }}</p>
        <h1 class="mt-1 font-display text-4xl font-bold capitalize">{{ pokemon.name }}</h1>

        <div class="mt-4 flex flex-wrap gap-2">
          <span
            v-for="type in pokemon.types"
            :key="type"
            class="rounded-full border px-3 py-1 text-xs font-semibold uppercase tracking-wide"
            :style="getTypeChipStyle(type)"
          >
            {{ labelType(type) }}
          </span>
        </div>

        <div class="mt-5">
          <h2 class="text-sm font-semibold uppercase tracking-wide text-muted">{{ t("pokemon.abilities") }}</h2>
          <p v-if="!pokemon.abilities.length" class="mt-2 text-sm text-muted">{{ t("pokemon.no_abilities") }}</p>
          <ul v-else class="mt-2 flex flex-wrap gap-2">
            <li
              v-for="ability in pokemon.abilities"
              :key="ability.name"
              class="relative"
            >
              <button
                type="button"
                class="rounded-lg border border-black/10 bg-white px-3 py-1 text-sm font-medium capitalize text-text"
                :title="ability.description"
                @mouseenter="setHoveredAbility(ability.name)"
                @mouseleave="setHoveredAbility(null)"
                @focus="setHoveredAbility(ability.name)"
                @blur="setHoveredAbility(null)"
                @click="toggleAbilityTooltip(ability.name)"
              >
                {{ ability.display_name ?? formatLabel(ability.name) }}
              </button>
              <div
                class="pointer-events-none absolute top-full z-20 mt-2 w-64 rounded-lg border border-black/10 bg-white px-3 py-2 text-xs font-medium normal-case leading-relaxed text-text shadow-soft transition-opacity"
                :class="isAbilityTooltipVisible(ability.name) ? 'opacity-100' : 'opacity-0'"
              >
                {{ ability.description }}
              </div>
            </li>
          </ul>
        </div>

      </div>

    </div>

    <article class="hidden card-surface rounded-2xl p-5 md:block">
      <h2 class="font-display text-xl font-semibold">{{ t("pokemon.statistics") }}</h2>
      <ul class="mt-4 grid grid-cols-2 gap-2 sm:grid-cols-3 md:grid-cols-6">
        <li
          v-for="entry in stats"
          :key="`fullwidth-stat-${entry.name}`"
          class="rounded-lg bg-white/80 px-2.5 py-2"
        >
          <p class="text-xs font-semibold tracking-wide text-muted">{{ statShortLabel(entry.name) }}</p>
          <p class="mt-0.5 font-mono text-base font-semibold leading-none">{{ entry.value }}</p>
        </li>
      </ul>
    </article>

    <section class="space-y-3 md:hidden">
      <article class="card-surface overflow-hidden rounded-2xl">
        <button
          type="button"
          class="flex w-full items-center justify-between px-4 py-3 text-left"
          @click="toggleMobileSection('statistics')"
        >
          <h2 class="font-display text-lg font-semibold">{{ t("pokemon.statistics") }}</h2>
          <span class="font-mono text-sm text-muted">{{ isMobileSectionOpen('statistics') ? "−" : "+" }}</span>
        </button>
        <div v-show="isMobileSectionOpen('statistics')" class="border-t border-black/10 px-4 py-4">
          <ul class="grid grid-cols-2 gap-2">
            <li
              v-for="entry in stats"
              :key="`mobile-stat-${entry.name}`"
              class="rounded-lg bg-white/80 px-2.5 py-2"
            >
              <p class="text-xs font-semibold tracking-wide text-muted">{{ statShortLabel(entry.name) }}</p>
              <p class="mt-0.5 font-mono text-base font-semibold leading-none">{{ entry.value }}</p>
            </li>
          </ul>
        </div>
      </article>

      <article class="card-surface overflow-hidden rounded-2xl">
        <button
          type="button"
          class="flex w-full items-center justify-between px-4 py-3 text-left"
          @click="toggleMobileSection('damage-dealt')"
        >
          <h2 class="font-display text-lg font-semibold">{{ t("pokemon.damage_dealt") }}</h2>
          <span class="font-mono text-sm text-muted">{{ isMobileSectionOpen('damage-dealt') ? "−" : "+" }}</span>
        </button>
        <div v-show="isMobileSectionOpen('damage-dealt')" class="border-t border-black/10 px-4 py-4">
          <div class="space-y-5">
            <section v-for="group in offensiveDamageGroups" :key="`multiplier-${group.multiplier}`">
              <h3 class="font-display text-lg font-semibold">
                {{ t("pokemon.stab_damage_to", { multiplier: formatMultiplier(group.multiplier) }) }}
              </h3>
              <ul class="mt-2 grid grid-cols-2 gap-2 sm:grid-cols-3 lg:grid-cols-4 2xl:grid-cols-5">
                <li
                  v-for="entry in group.entries"
                  :key="entry.type"
                  class="rounded-md border px-2.5 py-1 text-sm font-semibold capitalize leading-tight sm:text-base"
                  :style="getTypeChipStyle(entry.type)"
                >
                  {{ labelType(entry.type) }}
                </li>
              </ul>
            </section>
          </div>
        </div>
      </article>

      <article class="card-surface overflow-hidden rounded-2xl">
        <button
          type="button"
          class="flex w-full items-center justify-between px-4 py-3 text-left"
          @click="toggleMobileSection('damage-taken')"
        >
          <h2 class="font-display text-lg font-semibold">{{ t("pokemon.damage_taken") }}</h2>
          <span class="font-mono text-sm text-muted">{{ isMobileSectionOpen('damage-taken') ? "−" : "+" }}</span>
        </button>
        <div v-show="isMobileSectionOpen('damage-taken')" class="border-t border-black/10 px-4 py-4">
          <div class="space-y-5">
            <section v-for="group in defensiveDamageGroups" :key="`def-multiplier-${group.multiplier}`">
              <h3 class="font-display text-lg font-semibold">
                {{ t("pokemon.takes_from", { multiplier: formatMultiplier(group.multiplier) }) }}
              </h3>
              <ul class="mt-2 grid grid-cols-2 gap-2 sm:grid-cols-3 lg:grid-cols-4 2xl:grid-cols-5">
                <li
                  v-for="entry in group.entries"
                  :key="`def-${entry.type}`"
                  class="rounded-md border px-2.5 py-1 text-sm font-semibold capitalize leading-tight sm:text-base"
                  :style="getTypeChipStyle(entry.type)"
                >
                  {{ labelType(entry.type) }}
                </li>
              </ul>
            </section>
          </div>
        </div>
      </article>

      <article class="card-surface overflow-hidden rounded-2xl">
        <button
          type="button"
          class="flex w-full items-center justify-between px-4 py-3 text-left"
          @click="toggleMobileSection('moves')"
        >
          <h2 class="font-display text-lg font-semibold">{{ t("pokemon.moves_list") }}</h2>
          <span class="font-mono text-sm text-muted">{{ isMobileSectionOpen('moves') ? "−" : "+" }}</span>
        </button>
        <div v-show="isMobileSectionOpen('moves')" class="border-t border-black/10 px-4 py-4">
          <p v-if="pokemonMovesLoading" class="text-sm text-muted">{{ t("pokemon.loading_moves") }}</p>
          <p v-else-if="pokemonMovesErrorMessage" class="text-sm text-red-600">{{ pokemonMovesErrorMessage }}</p>
          <div v-else class="space-y-3">
            <div class="space-y-2 rounded-lg border border-black/10 bg-white/70 p-3">
              <div class="flex items-center justify-between">
                <p class="text-xs font-semibold uppercase tracking-wide text-muted">{{ t("pokemon.filters") }}</p>
                <button
                  v-if="hasActiveMoveFilters"
                  type="button"
                  class="text-xs font-semibold text-muted underline-offset-2 hover:text-text hover:underline"
                  @click="resetMoveFilters"
                >
                  {{ t("pokemon.clear") }}
                </button>
              </div>

              <div class="space-y-1">
                <p class="text-[11px] font-semibold uppercase tracking-wide text-muted">{{ t("pokemon.filter.type") }}</p>
                <div class="flex flex-wrap gap-2">
                  <label
                    v-for="typeOption in moveTypeOptions"
                    :key="`mobile-filter-type-${typeOption}`"
                    class="inline-flex items-center gap-1.5 rounded-md border border-black/10 bg-white px-2 py-1 text-xs"
                  >
                    <input v-model="selectedTypeFilters" type="checkbox" :value="typeOption" />
                    <span class="capitalize">{{ labelType(typeOption) }}</span>
                  </label>
                </div>
              </div>

              <div class="space-y-1">
                <p class="text-[11px] font-semibold uppercase tracking-wide text-muted">{{ t("pokemon.filter.category") }}</p>
                <div class="flex flex-wrap gap-2">
                  <label
                    v-for="categoryOption in moveCategoryOptions"
                    :key="`mobile-filter-category-${categoryOption}`"
                    class="inline-flex items-center gap-1.5 rounded-md border border-black/10 bg-white px-2 py-1 text-xs"
                  >
                    <input v-model="selectedCategoryFilters" type="checkbox" :value="categoryOption" />
                    <span class="capitalize">{{ labelMoveCategory(categoryOption) }}</span>
                  </label>
                </div>
              </div>

              <div class="space-y-1">
                <p class="text-[11px] font-semibold uppercase tracking-wide text-muted">{{ t("pokemon.filter.learn") }}</p>
                <div class="flex flex-wrap gap-2">
                  <label
                    v-for="learnOption in moveLearnOptions"
                    :key="`mobile-filter-learn-${learnOption}`"
                    class="inline-flex items-center gap-1.5 rounded-md border border-black/10 bg-white px-2 py-1 text-xs"
                  >
                    <input v-model="selectedLearnFilters" type="checkbox" :value="learnOption" />
                    <span>{{ formatLearnMethodName(learnOption) }}</span>
                  </label>
                </div>
              </div>
            </div>

            <div class="overflow-x-auto">
            <table class="min-w-[700px] w-full text-left text-sm">
              <thead class="bg-black/5 text-xs uppercase tracking-wide text-muted">
                <tr>
                  <th class="px-3 py-2">
                    <button type="button" class="inline-flex items-center gap-1 hover:text-text" @click="toggleMoveSort('name')">
                      {{ t("moves.column.move") }} <span class="font-mono">{{ moveSortIndicator('name') }}</span>
                    </button>
                  </th>
                  <th class="px-3 py-2">
                    <button type="button" class="inline-flex items-center gap-1 hover:text-text" @click="toggleMoveSort('type')">
                      {{ t("moves.column.type") }} <span class="font-mono">{{ moveSortIndicator('type') }}</span>
                    </button>
                  </th>
                  <th class="px-3 py-2">
                    <button type="button" class="inline-flex items-center gap-1 hover:text-text" @click="toggleMoveSort('category')">
                      {{ t("moves.column.category") }} <span class="font-mono">{{ moveSortIndicator('category') }}</span>
                    </button>
                  </th>
                  <th class="px-3 py-2">
                    <button type="button" class="inline-flex items-center gap-1 hover:text-text" @click="toggleMoveSort('power')">
                      {{ t("moves.column.power") }} <span class="font-mono">{{ moveSortIndicator('power') }}</span>
                    </button>
                  </th>
                  <th class="px-3 py-2">
                    <button type="button" class="inline-flex items-center gap-1 hover:text-text" @click="toggleMoveSort('pp')">
                      {{ t("moves.column.pp") }} <span class="font-mono">{{ moveSortIndicator('pp') }}</span>
                    </button>
                  </th>
                  <th class="px-3 py-2">
                    <button type="button" class="inline-flex items-center gap-1 hover:text-text" @click="toggleMoveSort('accuracy')">
                      {{ t("moves.column.accuracy") }} <span class="font-mono">{{ moveSortIndicator('accuracy') }}</span>
                    </button>
                  </th>
                  <th class="px-3 py-2">
                    <button type="button" class="inline-flex items-center gap-1 hover:text-text" @click="toggleMoveSort('learn')">
                      {{ t("pokemon.filter.learn") }} <span class="font-mono">{{ moveSortIndicator('learn') }}</span>
                    </button>
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="move in filteredAndSortedPokemonMoves"
                  :key="`mobile-move-table-${move.name}`"
                  class="border-t border-black/5"
                >
                  <td class="px-3 py-2 align-top">
                    <div class="relative inline-block w-full">
                      <button
                        type="button"
                        class="text-left font-medium capitalize text-text underline decoration-dotted underline-offset-2"
                        @mouseenter="setHoveredMove(move.name)"
                        @mouseleave="setHoveredMove(null)"
                        @focus="setHoveredMove(move.name)"
                        @blur="setHoveredMove(null)"
                        @click="toggleMoveTooltip(move.name)"
                      >
                        {{ move.display_name ?? formatLabel(move.name) }}
                      </button>
                      <p
                        v-if="isMoveTooltipVisible(move.name)"
                        class="pointer-events-none absolute left-0 top-full z-20 mt-1 w-72 max-w-[calc(100vw-4rem)] rounded-md border border-black/10 bg-white px-2 py-1 text-xs normal-case leading-relaxed text-muted shadow-soft"
                      >
                        {{ move.description ?? t("moves.no_description") }}
                      </p>
                    </div>
                  </td>
                  <td class="px-3 py-2">
                    <span
                      v-if="move.type"
                      class="inline-flex rounded-full border px-2 py-0.5 text-xs font-semibold uppercase tracking-wide"
                      :style="getTypeChipStyle(move.type)"
                    >
                      {{ labelType(move.type) }}
                    </span>
                    <span v-else class="text-muted">-</span>
                  </td>
                  <td class="px-3 py-2 capitalize text-muted">{{ move.category ? labelMoveCategory(move.category) : "-" }}</td>
                  <td class="px-3 py-2">
                    <strong v-if="move.power !== null && isStabMove(move)">{{ move.power }}</strong>
                    <span v-else>{{ move.power ?? "-" }}</span>
                  </td>
                  <td class="px-3 py-2">{{ move.pp ?? "-" }}</td>
                  <td class="px-3 py-2">{{ move.accuracy ?? "-" }}</td>
                  <td class="px-3 py-2 text-muted">{{ formatLearnMethods(move.methods) }}</td>
                </tr>
              </tbody>
            </table>
            </div>
          </div>
        </div>
      </article>

      <article class="card-surface overflow-hidden rounded-2xl">
        <button
          type="button"
          class="flex w-full items-center justify-between px-4 py-3 text-left"
          @click="toggleMobileSection('location')"
        >
          <h2 class="font-display text-lg font-semibold">{{ t("pokemon.location") }}</h2>
          <span class="font-mono text-sm text-muted">{{ isMobileSectionOpen('location') ? "−" : "+" }}</span>
        </button>
        <div v-show="isMobileSectionOpen('location')" class="border-t border-black/10 px-4 py-4">
          <p v-if="!hoennPokemonLocations.length" class="text-sm text-muted">{{ t("pokemon.no_hoenn_locations") }}</p>
          <ul v-else class="flex flex-wrap gap-2">
            <li
              v-for="location in hoennPokemonLocations"
              :key="`mobile-location-${location.name}`"
            >
              <RouterLink
                :to="{ name: 'location-detail', params: { locationName: location.name } }"
                class="inline-flex rounded-lg bg-amber-50 px-3 py-1 text-sm font-medium text-amber-700 underline-offset-2 transition hover:bg-amber-100 hover:underline"
              >
                {{ location.display_name }}
              </RouterLink>
            </li>
          </ul>
        </div>
      </article>
    </section>

    <section class="hidden gap-4 xl:grid-cols-2 md:grid">
      <article class="card-surface rounded-2xl p-4">
        <div class="space-y-5">
          <section v-for="group in offensiveDamageGroups" :key="`desktop-multiplier-${group.multiplier}`">
            <h3 class="font-display text-lg font-semibold">{{ t("pokemon.stab_damage_to", { multiplier: formatMultiplier(group.multiplier) }) }}</h3>
            <ul class="mt-2 grid grid-cols-2 gap-2 sm:grid-cols-3 lg:grid-cols-4 2xl:grid-cols-5">
              <li
                v-for="entry in group.entries"
                :key="`desktop-${entry.type}`"
                class="rounded-md border px-2.5 py-1 text-sm font-semibold capitalize leading-tight sm:text-base"
                :style="getTypeChipStyle(entry.type)"
              >
                {{ labelType(entry.type) }}
              </li>
            </ul>
          </section>
        </div>
      </article>

      <article class="card-surface rounded-2xl p-4">
        <div class="space-y-5">
          <section v-for="group in defensiveDamageGroups" :key="`desktop-def-multiplier-${group.multiplier}`">
            <h3 class="font-display text-lg font-semibold">{{ t("pokemon.takes_from", { multiplier: formatMultiplier(group.multiplier) }) }}</h3>
            <ul class="mt-2 grid grid-cols-2 gap-2 sm:grid-cols-3 lg:grid-cols-4 2xl:grid-cols-5">
              <li
                v-for="entry in group.entries"
                :key="`desktop-def-${entry.type}`"
                class="rounded-md border px-2.5 py-1 text-sm font-semibold capitalize leading-tight sm:text-base"
                :style="getTypeChipStyle(entry.type)"
              >
                {{ labelType(entry.type) }}
              </li>
            </ul>
          </section>
        </div>
      </article>
    </section>

    <article class="hidden card-surface rounded-2xl p-5 md:block">
        <h2 class="font-display text-xl font-semibold">{{ t("pokemon.moves_list") }}</h2>
        <p v-if="pokemonMovesLoading" class="mt-3 text-sm text-muted">{{ t("pokemon.loading_moves") }}</p>
        <p v-else-if="pokemonMovesErrorMessage" class="mt-3 text-sm text-red-600">{{ pokemonMovesErrorMessage }}</p>
        <div v-else class="mt-3 space-y-3">
          <div class="space-y-2 rounded-lg border border-black/10 bg-white/70 p-3">
            <div class="flex items-center justify-between">
              <p class="text-xs font-semibold uppercase tracking-wide text-muted">{{ t("pokemon.filters") }}</p>
              <button
                v-if="hasActiveMoveFilters"
                type="button"
                class="text-xs font-semibold text-muted underline-offset-2 hover:text-text hover:underline"
                @click="resetMoveFilters"
              >
                {{ t("pokemon.clear") }}
              </button>
            </div>

            <div class="space-y-1">
              <p class="text-[11px] font-semibold uppercase tracking-wide text-muted">{{ t("pokemon.filter.type") }}</p>
              <div class="flex flex-wrap gap-2">
                <label
                  v-for="typeOption in moveTypeOptions"
                  :key="`desktop-filter-type-${typeOption}`"
                  class="inline-flex items-center gap-1.5 rounded-md border border-black/10 bg-white px-2 py-1 text-xs"
                >
                  <input v-model="selectedTypeFilters" type="checkbox" :value="typeOption" />
                  <span class="capitalize">{{ labelType(typeOption) }}</span>
                </label>
              </div>
            </div>

            <div class="space-y-1">
              <p class="text-[11px] font-semibold uppercase tracking-wide text-muted">{{ t("pokemon.filter.category") }}</p>
              <div class="flex flex-wrap gap-2">
                <label
                  v-for="categoryOption in moveCategoryOptions"
                  :key="`desktop-filter-category-${categoryOption}`"
                  class="inline-flex items-center gap-1.5 rounded-md border border-black/10 bg-white px-2 py-1 text-xs"
                >
                  <input v-model="selectedCategoryFilters" type="checkbox" :value="categoryOption" />
                  <span class="capitalize">{{ labelMoveCategory(categoryOption) }}</span>
                </label>
              </div>
            </div>

            <div class="space-y-1">
              <p class="text-[11px] font-semibold uppercase tracking-wide text-muted">{{ t("pokemon.filter.learn") }}</p>
              <div class="flex flex-wrap gap-2">
                <label
                  v-for="learnOption in moveLearnOptions"
                  :key="`desktop-filter-learn-${learnOption}`"
                  class="inline-flex items-center gap-1.5 rounded-md border border-black/10 bg-white px-2 py-1 text-xs"
                >
                  <input v-model="selectedLearnFilters" type="checkbox" :value="learnOption" />
                  <span>{{ formatLearnMethodName(learnOption) }}</span>
                </label>
              </div>
            </div>
          </div>

          <div class="overflow-x-auto">
            <table class="min-w-[700px] w-full text-left text-sm">
            <thead class="bg-black/5 text-xs uppercase tracking-wide text-muted">
              <tr>
                <th class="px-3 py-2">
                  <button type="button" class="inline-flex items-center gap-1 hover:text-text" @click="toggleMoveSort('name')">
                    {{ t("moves.column.move") }} <span class="font-mono">{{ moveSortIndicator('name') }}</span>
                  </button>
                </th>
                <th class="px-3 py-2">
                  <button type="button" class="inline-flex items-center gap-1 hover:text-text" @click="toggleMoveSort('type')">
                    {{ t("moves.column.type") }} <span class="font-mono">{{ moveSortIndicator('type') }}</span>
                  </button>
                </th>
                <th class="px-3 py-2">
                  <button type="button" class="inline-flex items-center gap-1 hover:text-text" @click="toggleMoveSort('category')">
                    {{ t("moves.column.category") }} <span class="font-mono">{{ moveSortIndicator('category') }}</span>
                  </button>
                </th>
                <th class="px-3 py-2">
                  <button type="button" class="inline-flex items-center gap-1 hover:text-text" @click="toggleMoveSort('power')">
                    {{ t("moves.column.power") }} <span class="font-mono">{{ moveSortIndicator('power') }}</span>
                  </button>
                </th>
                <th class="px-3 py-2">
                  <button type="button" class="inline-flex items-center gap-1 hover:text-text" @click="toggleMoveSort('pp')">
                    {{ t("moves.column.pp") }} <span class="font-mono">{{ moveSortIndicator('pp') }}</span>
                  </button>
                </th>
                <th class="px-3 py-2">
                  <button type="button" class="inline-flex items-center gap-1 hover:text-text" @click="toggleMoveSort('accuracy')">
                    {{ t("moves.column.accuracy") }} <span class="font-mono">{{ moveSortIndicator('accuracy') }}</span>
                  </button>
                </th>
                <th class="px-3 py-2">
                  <button type="button" class="inline-flex items-center gap-1 hover:text-text" @click="toggleMoveSort('learn')">
                    {{ t("pokemon.filter.learn") }} <span class="font-mono">{{ moveSortIndicator('learn') }}</span>
                  </button>
                </th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="move in filteredAndSortedPokemonMoves"
                :key="`desktop-move-table-${move.name}`"
                class="border-t border-black/5"
              >
                <td class="px-3 py-2 align-top">
                  <div class="relative inline-block w-full">
                    <button
                      :ref="(el) => { if (el) moveButtonRefs[move.name] = el as HTMLElement }"
                      type="button"
                      class="text-left font-medium capitalize text-text underline decoration-dotted underline-offset-2"
                      @mouseenter="setHoveredMove(move.name)"
                      @mouseleave="setHoveredMove(null)"
                      @focus="setHoveredMove(move.name)"
                      @blur="setHoveredMove(null)"
                      @click="toggleMoveTooltip(move.name)"
                    >
                      {{ move.display_name ?? formatLabel(move.name) }}
                    </button>
                    <Teleport v-if="isMoveTooltipVisible(move.name)" to="body">
                      <p
                        class="pointer-events-none fixed z-50 rounded-md border border-black/10 bg-white px-2 py-1 text-xs normal-case leading-relaxed text-muted shadow-soft"
                        style="max-width: calc(100vw - 2rem); width: 18rem;"
                        :style="getMoveTooltipStyle(move.name)"
                      >
                        {{ move.description ?? t("moves.no_description") }}
                      </p>
                    </Teleport>
                  </div>
                </td>
                <td class="px-3 py-2">
                  <span
                    v-if="move.type"
                    class="inline-flex rounded-full border px-2 py-0.5 text-xs font-semibold uppercase tracking-wide"
                    :style="getTypeChipStyle(move.type)"
                  >
                    {{ labelType(move.type) }}
                  </span>
                  <span v-else class="text-muted">-</span>
                </td>
                <td class="px-3 py-2 capitalize text-muted">{{ move.category ? labelMoveCategory(move.category) : "-" }}</td>
                <td class="px-3 py-2">
                  <strong v-if="move.power !== null && isStabMove(move)">{{ move.power }}</strong>
                  <span v-else>{{ move.power ?? "-" }}</span>
                </td>
                <td class="px-3 py-2">{{ move.pp ?? "-" }}</td>
                <td class="px-3 py-2">{{ move.accuracy ?? "-" }}</td>
                <td class="px-3 py-2 text-muted">{{ formatLearnMethods(move.methods) }}</td>
              </tr>
            </tbody>
            </table>
          </div>
        </div>
    </article>

    <article class="hidden card-surface rounded-2xl p-5 md:block">
      <h2 class="font-display text-xl font-semibold">{{ t("pokemon.location") }}</h2>
      <p v-if="!hoennPokemonLocations.length" class="mt-2 text-sm text-muted">{{ t("pokemon.no_hoenn_locations") }}</p>
      <ul v-else class="mt-3 flex flex-wrap gap-2">
        <li
          v-for="location in hoennPokemonLocations"
          :key="`desktop-location-${location.name}`"
        >
          <RouterLink
            :to="{ name: 'location-detail', params: { locationName: location.name } }"
            class="inline-flex rounded-lg bg-amber-50 px-3 py-1 text-sm font-medium text-amber-700 underline-offset-2 transition hover:bg-amber-100 hover:underline"
          >
            {{ location.display_name }}
          </RouterLink>
        </li>
      </ul>
    </article>
  </section>

  <p v-else-if="isLoading" class="text-sm text-muted">{{ t("pokemon.loading") }}</p>

  <p v-else class="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-600">
    {{ errorMessage || t("pokemon.not_found") }}
  </p>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import { useQuery } from "@tanstack/vue-query";
import { RouterLink, useRoute } from "vue-router";

import {
  fetchPokemmoHoennLocations,
  fetchPokemon,
  fetchPokemonEvolutionLine,
  fetchPokemonMoves
} from "@/api/client";
import {
  labelLearnMethod,
  labelMoveCategory,
  labelStatShort,
  labelType,
  t,
  useLocale
} from "@/i18n";
import {
  getDefensiveDamageGroups,
  getOffensiveDamageGroups
} from "@/constants/typeEffectiveness";
import { getTypeChipStyle } from "@/constants/pokemonTypes";
import type { Location, MoveLearnMethod, PokemonEvolutionMethod, PokemonMove } from "@/types";

type MobileSection =
  | "damage-dealt"
  | "damage-taken"
  | "statistics"
  | "moves"
  | "location";
type MoveSortColumn = "name" | "type" | "category" | "power" | "pp" | "accuracy" | "learn";
const LEARN_METHOD_SORT_ORDER: Record<string, number> = {
  "level-up": 0,
  tm: 1,
  tutor: 2,
  egg: 3
};

const STAT_ORDER = ["hp", "attack", "defense", "special-attack", "special-defense", "speed"];
const EVOLUTION_METHOD_ICONS = {
  friendship: "/evolution/friendship.svg",
  trade: "/evolution/trade.svg",
  beauty: "/evolution/beauty.svg",
  time: "/evolution/time.svg",
  special: "/evolution/special.svg"
} as const;

const route = useRoute();
const pokemonId = computed(() => Number(route.params.id));
const { locale, isItalian } = useLocale();

const pokemonQuery = useQuery({
  queryKey: computed(() => ["pokemon", locale.value, pokemonId.value]),
  queryFn: () => fetchPokemon(pokemonId.value),
  enabled: computed(() => Number.isFinite(pokemonId.value))
});

const pokemonMovesQuery = useQuery({
  queryKey: computed(() => ["pokemon-moves", locale.value, pokemonId.value]),
  queryFn: () => fetchPokemonMoves(pokemonId.value),
  enabled: computed(() => Number.isFinite(pokemonId.value))
});
const evolutionLineQuery = useQuery({
  queryKey: computed(() => ["pokemon-evolution-line", locale.value, pokemonId.value]),
  queryFn: () => fetchPokemonEvolutionLine(pokemonId.value),
  enabled: computed(() => Number.isFinite(pokemonId.value)),
  staleTime: 1000 * 60 * 60
});
const hoennLocationsQuery = useQuery({
  queryKey: computed(() => ["locations", "pokemmo", "hoenn", locale.value]),
  queryFn: fetchPokemmoHoennLocations
});

const pokemon = computed(() => pokemonQuery.data.value?.data ?? null);
const pokemonMoves = computed(() => pokemonMovesQuery.data.value?.data ?? []);
const evolutionLine = computed(() => evolutionLineQuery.data.value ?? null);
const evolutionDisplayBranches = computed(() => {
  if (!evolutionLine.value) {
    return [];
  }
  return evolutionLine.value.next_branches.length ? evolutionLine.value.next_branches : [[]];
});
const hasMultipleEvolutionBranches = computed(() => evolutionDisplayBranches.value.length > 1);
const hoennLocations = computed(() => hoennLocationsQuery.data.value?.data ?? []);
const hoennPokemonLocations = computed(() => {
  if (!pokemon.value) {
    return [] as Array<{ name: string; display_name: string }>;
  }

  const pokemonLocationRows = hoennLocations.value
    .filter((location) => location.pokemon_ids.includes(pokemon.value!.id))
    .map((location) => ({
      name: location.name,
      display_name: location.display_name ?? formatLocationName(location.name)
    }));

  return pokemonLocationRows.sort((a, b) =>
    a.display_name.localeCompare(b.display_name, undefined, {
      numeric: true,
      sensitivity: "base"
    })
  );
});
const sprite = computed(
  () =>
    pokemon.value?.sprites?.official_artwork ?? pokemon.value?.sprites?.front_default ?? null
);
const stats = computed(() => {
  const entries = Object.entries(pokemon.value?.stats ?? {}).map(([name, value]) => ({ name, value }));
  return entries.sort((a, b) => STAT_ORDER.indexOf(a.name) - STAT_ORDER.indexOf(b.name));
});
const evYieldEntries = computed(() => {
  const entries = Object.entries(pokemon.value?.ev_yield ?? {}).map(([name, value]) => ({
    name,
    value
  }));
  return entries.sort((a, b) => STAT_ORDER.indexOf(a.name) - STAT_ORDER.indexOf(b.name));
});
const offensiveDamageGroups = computed(() => getOffensiveDamageGroups(pokemon.value?.types ?? []));
const defensiveDamageGroups = computed(() => getDefensiveDamageGroups(pokemon.value?.types ?? []));
const isLoading = computed(() => pokemonQuery.isPending.value);
const errorMessage = computed(() =>
  pokemonQuery.error.value instanceof Error ? pokemonQuery.error.value.message : ""
);
const pokemonMovesLoading = computed(() => pokemonMovesQuery.isPending.value);
const pokemonMovesErrorMessage = computed(() =>
  pokemonMovesQuery.error.value instanceof Error ? pokemonMovesQuery.error.value.message : ""
);
const evolutionLineLoading = computed(() => evolutionLineQuery.isPending.value);
const selectedTypeFilters = ref<string[]>([]);
const selectedCategoryFilters = ref<string[]>([]);
const selectedLearnFilters = ref<string[]>([]);
const moveTypeOptions = computed(() => {
  const values = new Set(
    pokemonMoves.value
      .map((move) => move.type)
      .filter((value): value is string => Boolean(value))
  );
  return [...values].sort();
});
const moveCategoryOptions = computed(() => {
  const values = new Set(
    pokemonMoves.value
      .map((move) => move.category)
      .filter((value): value is string => Boolean(value))
  );
  return [...values].sort();
});
const moveLearnOptions = computed(() => {
  const values = new Set(pokemonMoves.value.flatMap((move) => move.methods.map((method) => method.method)));
  return [...values].sort((a, b) => compareSortValues(LEARN_METHOD_SORT_ORDER[a] ?? 99, LEARN_METHOD_SORT_ORDER[b] ?? 99));
});
const hasActiveMoveFilters = computed(
  () =>
    selectedTypeFilters.value.length > 0 ||
    selectedCategoryFilters.value.length > 0 ||
    selectedLearnFilters.value.length > 0
);
const filteredPokemonMoves = computed(() => {
  return pokemonMoves.value.filter((move) => {
    if (selectedTypeFilters.value.length && (!move.type || !selectedTypeFilters.value.includes(move.type))) {
      return false;
    }
    if (
      selectedCategoryFilters.value.length &&
      (!move.category || !selectedCategoryFilters.value.includes(move.category))
    ) {
      return false;
    }
    if (selectedLearnFilters.value.length) {
      const methods = move.methods.map((entry) => entry.method);
      if (!methods.some((method) => selectedLearnFilters.value.includes(method))) {
        return false;
      }
    }
    return true;
  });
});
const moveSortColumn = ref<MoveSortColumn>("name");
const moveSortDirection = ref<"asc" | "desc">("asc");
const filteredAndSortedPokemonMoves = computed(() => {
  const rows = [...filteredPokemonMoves.value];
  const direction = moveSortDirection.value === "asc" ? 1 : -1;

  rows.sort((a, b) => {
    const aValue = getMoveSortValue(a, moveSortColumn.value);
    const bValue = getMoveSortValue(b, moveSortColumn.value);
    return compareSortValues(aValue, bValue) * direction;
  });

  return rows;
});
const hoveredAbility = ref<string | null>(null);
const activeAbility = ref<string | null>(null);
const hoveredMove = ref<string | null>(null);
const activeMove = ref<string | null>(null);
const moveButtonRefs = ref<Record<string, HTMLElement>>({});
const mobileOpenSection = ref<MobileSection | null>("damage-dealt");

function formatLabel(value: string) {
  return value.replace(/-/g, " ");
}

function formatLearnMethods(methods: MoveLearnMethod[]) {
  if (!methods.length) {
    return "-";
  }
  return methods
    .map((method) => {
      if (method.method === "level-up") {
        return method.level !== null ? `Lv ${method.level}` : labelLearnMethod(method.method);
      }
      return labelLearnMethod(method.method);
    })
    .join(", ");
}

function formatLearnMethodName(method: string) {
  return labelLearnMethod(method);
}

function formatEvolutionTrigger(trigger: string | null) {
  if (!trigger) {
    return isItalian.value ? "Speciale" : "Special";
  }
  if (trigger === "level-up") {
    return isItalian.value ? "Livello" : "Level";
  }
  if (trigger === "use-item") {
    return isItalian.value ? "Usa strumento" : "Use item";
  }
  if (trigger === "trade") {
    return isItalian.value ? "Scambio" : "Trade";
  }
  return formatLabel(trigger);
}

function evolutionMethodDisplay(method: PokemonEvolutionMethod | null) {
  if (!method) {
    return { label: isItalian.value ? "Speciale" : "Special", icon: EVOLUTION_METHOD_ICONS.special };
  }

  if (method.min_level !== null) {
    return { label: `Lv ${method.min_level}`, icon: null as string | null };
  }

  if (method.item_sprite) {
    return {
      label: formatLabel(method.item_name ?? "stone"),
      icon: method.item_sprite
    };
  }

  if (method.held_item_sprite) {
    return {
      label: isItalian.value
        ? `Tieni ${formatLabel(method.held_item_name ?? "strumento")}`
        : `Hold ${formatLabel(method.held_item_name ?? "item")}`,
      icon: method.held_item_sprite
    };
  }

  if (method.min_happiness !== null || method.min_affection !== null) {
    return {
      label: isItalian.value ? "Amicizia" : "Friendship",
      icon: EVOLUTION_METHOD_ICONS.friendship
    };
  }

  if (method.min_beauty !== null) {
    return {
      label: isItalian.value ? "Bellezza" : "Beauty",
      icon: EVOLUTION_METHOD_ICONS.beauty
    };
  }

  if (method.time_of_day) {
    return {
      label: method.time_of_day === "day"
        ? (isItalian.value ? "Giorno" : "Day")
        : (isItalian.value ? "Notte" : "Night"),
      icon: EVOLUTION_METHOD_ICONS.time
    };
  }

  if (method.trigger === "trade") {
    return {
      label: isItalian.value ? "Scambio" : "Trade",
      icon: EVOLUTION_METHOD_ICONS.trade
    };
  }

  return {
    label: formatEvolutionTrigger(method.trigger).replace(/^./, (character) => character.toUpperCase()),
    icon: EVOLUTION_METHOD_ICONS.special
  };
}

function evolutionMethodLabel(method: PokemonEvolutionMethod | null) {
  return evolutionMethodDisplay(method).label;
}

function evolutionMethodIcon(method: PokemonEvolutionMethod | null) {
  return evolutionMethodDisplay(method).icon;
}

function evolutionMethodBadgeLabel(method: PokemonEvolutionMethod | null) {
  if (!method) {
    return "";
  }
  if (method.min_level !== null) {
    return `Lv${method.min_level}`;
  }
  return "";
}

function evolutionMethodTooltip(method: PokemonEvolutionMethod | null) {
  if (!method) {
    return isItalian.value ? "Condizione evolutiva speciale" : "Special evolution condition";
  }
  const methodLabel = evolutionMethodDisplay(method).label.replace(/^./, (character) => character.toUpperCase());
  if (method.trade_species_name) {
    return isItalian.value
      ? `${methodLabel} con ${formatLabel(method.trade_species_name)}`
      : `${methodLabel} with ${formatLabel(method.trade_species_name)}`;
  }
  return methodLabel;
}

function resetMoveFilters() {
  selectedTypeFilters.value = [];
  selectedCategoryFilters.value = [];
  selectedLearnFilters.value = [];
}

function toggleMoveSort(column: MoveSortColumn) {
  if (moveSortColumn.value === column) {
    moveSortDirection.value = moveSortDirection.value === "asc" ? "desc" : "asc";
    return;
  }
  moveSortColumn.value = column;
  moveSortDirection.value = "asc";
}

function moveSortIndicator(column: MoveSortColumn) {
  if (moveSortColumn.value !== column) {
    return "";
  }
  return moveSortDirection.value === "asc" ? "↑" : "↓";
}

function getMoveSortValue(move: PokemonMove, column: MoveSortColumn) {
  if (column === "learn") {
    return getMoveLearnSortValue(move);
  }
  if (column === "power" || column === "pp" || column === "accuracy") {
    return move[column];
  }
  if (column === "name" || column === "type" || column === "category") {
    if (column === "name") {
      return (move.display_name ?? move.name ?? "").toLowerCase();
    }
    return (move[column] ?? "").toLowerCase();
  }
  return "";
}

function isStabMove(move: PokemonMove) {
  if (!move.type || !pokemon.value) {
    return false;
  }
  return pokemon.value.types.includes(move.type);
}

function getMoveLearnSortValue(move: PokemonMove) {
  const levelMethod = move.methods.find(
    (method) => method.method === "level-up" && method.level !== null
  );
  if (levelMethod && levelMethod.level !== null) {
    return levelMethod.level;
  }

  if (!move.methods.length) {
    return 2000;
  }

  const fallbackRank = Math.min(
    ...move.methods.map((method) => LEARN_METHOD_SORT_ORDER[method.method] ?? 99)
  );
  return 1000 + fallbackRank;
}

function compareSortValues(
  a: string | number | null | undefined,
  b: string | number | null | undefined
) {
  const aIsNull = a === null || a === undefined || a === "";
  const bIsNull = b === null || b === undefined || b === "";

  if (aIsNull && bIsNull) {
    return 0;
  }
  if (aIsNull) {
    return 1;
  }
  if (bIsNull) {
    return -1;
  }

  if (typeof a === "number" && typeof b === "number") {
    return a - b;
  }

  return String(a).localeCompare(String(b));
}

function statShortLabel(statName: string) {
  return labelStatShort(statName);
}

function formatMultiplier(multiplier: number) {
  if (multiplier === 0) {
    return "0x";
  }
  return Number.isInteger(multiplier)
    ? `${multiplier}x`
    : `${multiplier.toFixed(2).replace(/0+$/, "").replace(/\.$/, "")}x`;
}

function setHoveredAbility(abilityName: string | null) {
  hoveredAbility.value = abilityName;
}

function toggleAbilityTooltip(abilityName: string) {
  activeAbility.value = activeAbility.value === abilityName ? null : abilityName;
}

function isAbilityTooltipVisible(abilityName: string) {
  return hoveredAbility.value === abilityName || activeAbility.value === abilityName;
}

function setHoveredMove(moveName: string | null) {
  hoveredMove.value = moveName;
}

function toggleMoveTooltip(moveName: string) {
  activeMove.value = activeMove.value === moveName ? null : moveName;
}

function isMoveTooltipVisible(moveName: string) {
  return hoveredMove.value === moveName || activeMove.value === moveName;
}

function getMoveTooltipStyle(moveName: string) {
  const button = moveButtonRefs.value[moveName];
  if (!button) return {};
  const rect = button.getBoundingClientRect();
  return {
    left: `${rect.left}px`,
    top: `${rect.bottom + 4}px`
  };
}

function toggleMobileSection(section: MobileSection) {
  mobileOpenSection.value = mobileOpenSection.value === section ? null : section;
}

function isMobileSectionOpen(section: MobileSection) {
  return mobileOpenSection.value === section;
}

function formatLocationName(locationName: Location["name"]) {
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
</script>
