<template>
  <div class="mx-auto max-w-5xl space-y-5 px-4 py-6">

    <!-- Header -->
    <header class="space-y-1">
      <p class="font-mono text-xs uppercase tracking-widest text-accent">{{ t("team.eyebrow") }}</p>
      <h1 class="font-display text-3xl font-bold text-text">{{ t("team.title") }}</h1>
      <p class="text-sm text-muted">{{ t("team.subtitle") }}</p>
    </header>

    <!-- Team Builder -->
    <div class="relative z-10 grid grid-cols-1 gap-4 md:grid-cols-2">

      <!-- ── My Team ── -->
      <div class="card-surface rounded-2xl p-4 space-y-3">
        <div class="flex items-center gap-2">
          <span class="h-2 w-2 rounded-full bg-sky-500" />
          <h2 class="flex-1 font-display text-base font-semibold text-sky-700">{{ t("team.my_team") }}</h2>
          <span class="font-mono text-xs text-muted">{{ myTeamIds.length }} Pokémon</span>
          <button
            v-if="myTeamIds.length > 0"
            class="rounded-full px-2 py-0.5 text-xs text-muted transition hover:text-red-500"
            @click="clearMyTeam"
          >{{ t("team.clear") }}</button>
        </div>

        <div v-if="myTeamIds.length > 0" class="space-y-1.5">
          <div
            v-for="(_, i) in myTeamIds"
            :key="`my-${i}`"
            class="flex items-center gap-2.5 rounded-xl border border-black/8 bg-white/60 px-3 py-2"
          >
            <template v-if="mySlotData[i].isPending">
              <div class="h-9 w-9 shrink-0 animate-pulse rounded-lg bg-black/10" />
              <div class="flex-1 animate-pulse space-y-1.5">
                <div class="h-2.5 w-20 rounded bg-black/10" />
                <div class="h-2.5 w-14 rounded bg-black/10" />
              </div>
            </template>
            <template v-else-if="mySlotData[i]?.pokemon">
              <RouterLink
                :to="`/pokemon/${mySlotData[i].pokemon!.id}`"
                class="flex min-w-0 flex-1 items-center gap-2.5 transition hover:opacity-75"
              >
                <img
                  :src="mySlotData[i].pokemon!.sprites?.official_artwork ?? mySlotData[i].pokemon!.sprites?.front_default ?? ''"
                  :alt="mySlotData[i].pokemon!.name"
                  class="h-9 w-9 shrink-0 object-contain"
                />
                <div class="min-w-0 flex-1">
                  <p class="truncate text-sm font-medium capitalize text-text">{{ mySlotData[i].pokemon!.name }}</p>
                  <div class="mt-0.5 flex flex-wrap gap-1">
                    <span
                      v-for="type in mySlotData[i].pokemon!.types"
                      :key="type"
                      :style="getTypeChipStyle(type)"
                      class="rounded-full border px-1.5 py-0.5 text-[9px] font-semibold uppercase"
                    >{{ labelType(type) }}</span>
                  </div>
                  <div class="mt-0.5 flex flex-wrap gap-1">
                    <span
                      v-for="ability in mySlotData[i].pokemon!.abilities"
                      :key="ability.name"
                      :title="ability.description"
                      class="cursor-help rounded border border-violet-200 bg-violet-50 px-1.5 py-0.5 text-[9px] font-medium capitalize text-violet-700"
                    >{{ (ability.display_name ?? ability.name).replace(/-/g, ' ') }}</span>
                  </div>
                </div>
              </RouterLink>
            </template>
            <button
              class="ml-auto shrink-0 rounded-full p-1 text-muted transition hover:bg-red-50 hover:text-red-500"
              @click="removeFromMyTeam(i)"
            >
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" class="h-3.5 w-3.5" aria-hidden="true">
                <path d="M18 6L6 18M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        <div class="relative">
          <input
            v-model="searchMy"
            type="text"
            :placeholder="t('team.search_placeholder')"
            class="w-full rounded-xl border border-accent/20 bg-white/80 px-3 py-2 text-sm text-text outline-none placeholder:text-muted/50 focus:border-accent/50 focus:ring-1 focus:ring-accent/20"
            @focus="showDropMy = true"
            @input="showDropMy = true"
            @blur="onBlurMy"
          />
          <div
            v-if="showDropMy && searchResultsMy.length > 0"
            class="absolute left-0 right-0 top-full z-50 mt-1 max-h-52 overflow-y-auto rounded-xl border border-accent/15 bg-white shadow-lg"
          >
            <button
              v-for="p in searchResultsMy"
              :key="p.id"
              class="flex w-full items-center gap-2 px-3 py-2 text-left transition hover:bg-accent/10 disabled:!cursor-not-allowed disabled:opacity-40"
              :disabled="myTeamIds.includes(p.id)"
              @mousedown.prevent="selectMy(p)"
            >
              <img v-if="p.sprite" :src="p.sprite" :alt="p.name" class="h-7 w-7 shrink-0 object-contain" />
              <div v-else class="h-7 w-7 shrink-0 rounded bg-black/5" />
              <span class="shrink-0 font-mono text-xs text-muted">#{{ formatId(p.id) }}</span>
              <span class="min-w-0 truncate text-sm font-medium capitalize">{{ p.name }}</span>
              <div class="ml-auto flex shrink-0 gap-1">
                <span
                  v-for="type in p.types"
                  :key="type"
                  :style="getTypeChipStyle(type)"
                  class="rounded-full border px-1.5 py-0.5 text-[9px] font-semibold uppercase"
                >{{ labelType(type) }}</span>
              </div>
            </button>
          </div>
        </div>
      </div>

      <!-- ── Opponent Team ── -->
      <div class="card-surface rounded-2xl p-4 space-y-3">
        <div class="flex items-center gap-2">
          <span class="h-2 w-2 rounded-full bg-amber-500" />
          <h2 class="flex-1 font-display text-base font-semibold text-amber-700">{{ t("team.opp_team") }}</h2>
          <span class="font-mono text-xs text-muted">{{ oppTeamIds.length }} Pokémon</span>
          <button
            v-if="oppTeamIds.length > 0"
            class="rounded-full px-2 py-0.5 text-xs text-muted transition hover:text-red-500"
            @click="clearOppTeam"
          >{{ t("team.clear") }}</button>
        </div>

        <div v-if="oppTeamIds.length > 0" class="space-y-1.5">
          <div
            v-for="(_, i) in oppTeamIds"
            :key="`opp-${i}`"
            class="flex items-center gap-2.5 rounded-xl border border-black/8 bg-white/60 px-3 py-2"
          >
            <template v-if="oppSlotData[i].isPending">
              <div class="h-9 w-9 shrink-0 animate-pulse rounded-lg bg-black/10" />
              <div class="flex-1 animate-pulse space-y-1.5">
                <div class="h-2.5 w-20 rounded bg-black/10" />
                <div class="h-2.5 w-14 rounded bg-black/10" />
              </div>
            </template>
            <template v-else-if="oppSlotData[i]?.pokemon">
              <RouterLink
                :to="`/pokemon/${oppSlotData[i].pokemon!.id}`"
                class="flex min-w-0 flex-1 items-center gap-2.5 transition hover:opacity-75"
              >
                <img
                  :src="oppSlotData[i].pokemon!.sprites?.official_artwork ?? oppSlotData[i].pokemon!.sprites?.front_default ?? ''"
                  :alt="oppSlotData[i].pokemon!.name"
                  class="h-9 w-9 shrink-0 object-contain"
                />
                <div class="min-w-0 flex-1">
                  <p class="truncate text-sm font-medium capitalize text-text">{{ oppSlotData[i].pokemon!.name }}</p>
                  <div class="mt-0.5 flex flex-wrap gap-1">
                    <span
                      v-for="type in oppSlotData[i].pokemon!.types"
                      :key="type"
                      :style="getTypeChipStyle(type)"
                      class="rounded-full border px-1.5 py-0.5 text-[9px] font-semibold uppercase"
                    >{{ labelType(type) }}</span>
                  </div>
                  <div class="mt-0.5 flex flex-wrap gap-1">
                    <span
                      v-for="ability in oppSlotData[i].pokemon!.abilities"
                      :key="ability.name"
                      :title="ability.description"
                      class="cursor-help rounded border border-violet-200 bg-violet-50 px-1.5 py-0.5 text-[9px] font-medium capitalize text-violet-700"
                    >{{ (ability.display_name ?? ability.name).replace(/-/g, ' ') }}</span>
                  </div>
                </div>
              </RouterLink>
            </template>
            <button
              class="ml-auto shrink-0 rounded-full p-1 text-muted transition hover:bg-red-50 hover:text-red-500"
              @click="removeFromOppTeam(i)"
            >
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" class="h-3.5 w-3.5" aria-hidden="true">
                <path d="M18 6L6 18M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        <div class="relative">
          <input
            v-model="searchOpp"
            type="text"
            :placeholder="t('team.search_placeholder')"
            class="w-full rounded-xl border border-accent/20 bg-white/80 px-3 py-2 text-sm text-text outline-none placeholder:text-muted/50 focus:border-accent/50 focus:ring-1 focus:ring-accent/20"
            @focus="showDropOpp = true"
            @input="showDropOpp = true"
            @blur="onBlurOpp"
          />
          <div
            v-if="showDropOpp && searchResultsOpp.length > 0"
            class="absolute left-0 right-0 top-full z-50 mt-1 max-h-52 overflow-y-auto rounded-xl border border-accent/15 bg-white shadow-lg"
          >
            <button
              v-for="p in searchResultsOpp"
              :key="p.id"
              class="flex w-full items-center gap-2 px-3 py-2 text-left transition hover:bg-accent/10 disabled:!cursor-not-allowed disabled:opacity-40"
              :disabled="oppTeamIds.includes(p.id)"
              @mousedown.prevent="selectOpp(p)"
            >
              <img v-if="p.sprite" :src="p.sprite" :alt="p.name" class="h-7 w-7 shrink-0 object-contain" />
              <div v-else class="h-7 w-7 shrink-0 rounded bg-black/5" />
              <span class="shrink-0 font-mono text-xs text-muted">#{{ formatId(p.id) }}</span>
              <span class="min-w-0 truncate text-sm font-medium capitalize">{{ p.name }}</span>
              <div class="ml-auto flex shrink-0 gap-1">
                <span
                  v-for="type in p.types"
                  :key="type"
                  :style="getTypeChipStyle(type)"
                  class="rounded-full border px-1.5 py-0.5 text-[9px] font-semibold uppercase"
                >{{ labelType(type) }}</span>
              </div>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty state -->
    <div v-if="myTeam.length === 0" class="card-surface rounded-2xl px-6 py-10 text-center text-sm text-muted">
      {{ t("team.empty_prompt") }}
    </div>

    <template v-else>

      <!-- ══ No opponent yet: standalone weakness card ══ -->
      <template v-if="oppTeam.length === 0">
        <article class="card-surface overflow-hidden rounded-2xl">
          <div class="border-b border-black/8 px-5 py-3.5">
            <h2 class="font-display font-semibold text-text">{{ t("team.section.defensive") }}</h2>
            <p class="mt-0.5 text-xs text-muted">{{ t("team.section.defensive_desc") }}</p>
          </div>
          <div class="p-5 space-y-2">
            <p v-if="myDefenseExposure.length === 0" class="text-xs text-muted">{{ t("team.no_weaknesses") }}</p>
            <div v-for="entry in myDefenseExposure" :key="entry.type" class="flex items-center gap-2">
              <span :style="getTypeChipStyle(entry.type)" class="w-20 shrink-0 rounded-full border px-2 py-0.5 text-center text-[10px] font-semibold uppercase tracking-wide">{{ labelType(entry.type) }}</span>
              <div class="relative h-2 flex-1 overflow-hidden rounded-full bg-black/8">
                <div class="h-full rounded-full bg-red-400 transition-all duration-300" :style="{ width: weakPct(entry.weakCount, entry.total) + '%' }" />
              </div>
              <span class="w-9 shrink-0 text-right font-mono text-xs font-bold text-red-600">{{ entry.weakCount }}/{{ entry.total }}</span>
            </div>
          </div>
        </article>
        <div class="card-surface rounded-2xl px-6 py-8 text-center text-sm text-muted">
          {{ t("team.no_opp_prompt") }}
        </div>
      </template>

      <!-- ══ Both teams: full matchup + stats ══ -->
      <template v-else>

        <article class="card-surface overflow-hidden rounded-2xl">
          <div class="border-b border-black/8 px-5 py-3.5">
            <h2 class="font-display font-semibold text-text">{{ t("team.section.matchup") }}</h2>
          </div>

          <div class="divide-y divide-black/8">

            <!-- ── Matrix 1: My STAB → Their Team ── -->
            <div class="p-5">
              <div class="mb-3 flex items-center gap-2">
                <span class="h-2 w-2 rounded-full bg-sky-500" />
                <p class="font-display text-sm font-semibold text-sky-700">{{ t("team.my_team") }}</p>
                <span class="text-xs text-muted">{{ t("team.matrix.coverage_hint") }}</span>
              </div>
              <div class="overflow-x-auto">
                <!-- Column headers: their Pokémon -->
                <div class="grid items-end gap-x-1 pb-3" :style="myGridStyle">
                  <div />
                  <RouterLink v-for="pkmn in oppTeam" :key="pkmn.id" :to="`/pokemon/${pkmn.id}`" class="flex flex-col items-center gap-0.5 overflow-hidden transition hover:opacity-75">
                    <img :src="pokemonSprite(pkmn)" :alt="pkmn.name" class="h-7 w-7 object-contain" />
                    <span class="w-full truncate text-center font-mono text-[9px] capitalize leading-tight text-muted">{{ pkmn.name }}</span>
                  </RouterLink>
                  <div class="pb-1 text-center font-mono text-[9px] uppercase tracking-wide text-muted">SE</div>
                </div>
                <!-- Rows: my STAB types -->
                <p v-if="myOffenseMatrix.length === 0" class="text-xs text-muted">{{ t("team.no_types") }}</p>
                <div
                  v-for="row in myOffenseMatrix"
                  :key="row.attackType"
                  class="mb-1 grid items-center gap-x-1"
                  :style="myGridStyle"
                >
                  <div class="flex items-center gap-1">
                    <span :style="getTypeChipStyle(row.attackType)" class="min-w-0 flex-1 rounded-full border px-1.5 py-0.5 text-center text-[10px] font-semibold uppercase leading-tight">{{ labelType(row.attackType) }}</span>
                    <span :class="row.isStab ? 'bg-accent/15 text-accent' : 'opacity-0'" class="shrink-0 rounded px-1 py-0.5 font-mono text-[8px] font-bold">S</span>
                  </div>
                  <div v-for="cell in row.cells" :key="cell.pokemon.id" class="flex items-center justify-center py-0.5">
                    <span :class="['block w-full rounded border py-0.5 text-center font-mono text-[11px] font-bold leading-tight', cellClass(cell.multiplier)]">{{ formatMult(cell.multiplier) }}</span>
                  </div>
                  <div class="flex items-center gap-1 pl-2">
                    <div class="h-1.5 flex-1 overflow-hidden rounded-full bg-black/8">
                      <div class="h-full rounded-full bg-green-500 transition-all duration-300" :style="{ width: weakPct(row.hitCount, row.cells.length) + '%' }" />
                    </div>
                    <span class="w-4 shrink-0 text-right font-mono text-[10px] text-muted">{{ row.hitCount }}</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- ── Matrix 2: Their STAB → My Team ── -->
            <div class="p-5">
              <div class="mb-3 flex items-center gap-2">
                <span class="h-2 w-2 rounded-full bg-amber-500" />
                <p class="font-display text-sm font-semibold text-amber-700">{{ t("team.opp_team") }}</p>
                <span class="text-xs text-muted">{{ t("team.matrix.threats_hint") }}</span>
              </div>
              <div class="overflow-x-auto">
                <!-- Column headers: my Pokémon -->
                <div class="grid items-end gap-x-1 pb-3" :style="oppGridStyle">
                  <div />
                  <RouterLink v-for="pkmn in myTeam" :key="pkmn.id" :to="`/pokemon/${pkmn.id}`" class="flex flex-col items-center gap-0.5 overflow-hidden transition hover:opacity-75">
                    <img :src="pokemonSprite(pkmn)" :alt="pkmn.name" class="h-7 w-7 object-contain" />
                    <span class="w-full truncate text-center font-mono text-[9px] capitalize leading-tight text-muted">{{ pkmn.name }}</span>
                  </RouterLink>
                  <div class="pb-1 text-center font-mono text-[9px] uppercase tracking-wide text-muted">SE</div>
                </div>
                <!-- Rows: their STAB types -->
                <p v-if="oppOffenseMatrix.length === 0" class="text-xs text-muted">{{ t("team.no_types") }}</p>
                <div
                  v-for="row in oppOffenseMatrix"
                  :key="row.attackType"
                  class="mb-1 grid items-center gap-x-1"
                  :style="oppGridStyle"
                >
                  <div class="flex items-center gap-1">
                    <span :style="getTypeChipStyle(row.attackType)" class="min-w-0 flex-1 rounded-full border px-1.5 py-0.5 text-center text-[10px] font-semibold uppercase leading-tight">{{ labelType(row.attackType) }}</span>
                    <span :class="row.isStab ? 'bg-accent/15 text-accent' : 'opacity-0'" class="shrink-0 rounded px-1 py-0.5 font-mono text-[8px] font-bold">S</span>
                  </div>
                  <div v-for="cell in row.cells" :key="cell.pokemon.id" class="flex items-center justify-center py-0.5">
                    <span :class="['block w-full rounded border py-0.5 text-center font-mono text-[11px] font-bold leading-tight', cellClass(cell.multiplier)]">{{ formatMult(cell.multiplier) }}</span>
                  </div>
                  <div class="flex items-center gap-1 pl-2">
                    <div class="h-1.5 flex-1 overflow-hidden rounded-full bg-black/8">
                      <div class="h-full rounded-full bg-red-400 transition-all duration-300" :style="{ width: weakPct(row.hitCount, row.cells.length) + '%' }" />
                    </div>
                    <span class="w-4 shrink-0 text-right font-mono text-[10px] text-muted">{{ row.hitCount }}</span>
                  </div>
                </div>
              </div>
            </div>

          </div>
        </article>

        <!-- ══ Stat Comparison (collapsible) ══ -->
        <article class="card-surface overflow-hidden rounded-2xl">
          <button
            type="button"
            class="flex w-full items-center gap-3 px-5 py-3.5 text-left transition hover:bg-black/[0.02]"
            :class="statsOpen ? 'border-b border-black/8' : ''"
            @click="statsOpen = !statsOpen"
          >
            <h2 class="flex-1 font-display font-semibold text-text">{{ t("team.section.stats") }}</h2>
            <svg
              xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"
              stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"
              class="h-4 w-4 shrink-0 text-muted transition-transform duration-200"
              :class="statsOpen ? 'rotate-180' : ''"
              aria-hidden="true"
            ><path d="M6 9l6 6 6-6" /></svg>
          </button>
          <Transition
            enter-active-class="transition-all duration-200 ease-out overflow-hidden"
            leave-active-class="transition-all duration-150 ease-in overflow-hidden"
            enter-from-class="max-h-0 opacity-0"
            enter-to-class="max-h-[600px] opacity-100"
            leave-from-class="max-h-[600px] opacity-100"
            leave-to-class="max-h-0 opacity-0"
          >
            <div v-show="statsOpen" class="p-5">
              <div class="mb-3 grid grid-cols-[1fr_48px_1fr] items-center gap-2">
                <p class="truncate text-right font-mono text-xs font-bold text-sky-600">{{ t("team.my_team") }}</p>
                <div />
                <p class="truncate font-mono text-xs font-bold text-amber-600">{{ t("team.opp_team") }}</p>
              </div>
              <div class="space-y-1.5">
                <div
                  v-for="row in statRows"
                  :key="row.stat"
                  class="grid grid-cols-[1fr_48px_1fr] items-center gap-2"
                >
                  <div class="flex items-center justify-end gap-2">
                    <span :class="['w-8 text-right font-mono text-sm font-bold', row.aWins ? 'text-sky-600' : 'text-slate-300']">{{ row.a }}</span>
                    <div class="h-2 flex-1 overflow-hidden rounded-full bg-black/8">
                      <div class="ml-auto h-full rounded-full bg-sky-500 transition-all duration-300" :style="{ width: statBarPct(row.a) + '%' }" />
                    </div>
                  </div>
                  <div class="text-center">
                    <span class="font-mono text-[11px] font-bold uppercase text-muted">{{ labelStatShort(row.stat) }}</span>
                  </div>
                  <div class="flex items-center gap-2">
                    <div class="h-2 flex-1 overflow-hidden rounded-full bg-black/8">
                      <div class="h-full rounded-full bg-amber-400 transition-all duration-300" :style="{ width: statBarPct(row.b) + '%' }" />
                    </div>
                    <span :class="['w-8 font-mono text-sm font-bold', row.bWins ? 'text-amber-600' : 'text-slate-300']">{{ row.b }}</span>
                  </div>
                </div>
              </div>
              <p class="mt-3 text-center text-[10px] text-muted">{{ t("team.stats_avg_note") }}</p>
            </div>
          </Transition>
        </article>

      </template>

    </template>

    <!-- ══ AI Battle Analysis ══ -->
    <div class="card-surface overflow-hidden rounded-2xl">
      <div class="px-5 py-4 flex items-start gap-3">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" class="mt-0.5 h-4 w-4 shrink-0 text-accent" aria-hidden="true">
          <path d="M12 2a5 5 0 0 1 5 5v2H7V7a5 5 0 0 1 5-5z" /><rect x="3" y="9" width="18" height="13" rx="2" /><circle cx="12" cy="15.5" r="1.5" />
        </svg>
        <div>
          <p class="font-display text-sm font-semibold text-text">AI Battle Analysis</p>
          <p class="mt-0.5 text-xs text-muted">Get a full matchup breakdown — individual win/lose predictions, speed tiers, key threats, switch advice, and an overall team strategy — powered by <img src="/xcore_logo.png" alt="XCORE.GG" class="inline-block h-[1em] w-[1em] align-middle object-contain" /> XCORE.GG.</p>
        </div>
      </div>

      <!-- Unauthenticated CTA -->
      <template v-if="!authStore.isLoading && !authStore.isAuthenticated">
        <div class="border-t border-black/8 px-5 py-4 flex items-center justify-between gap-4">
          <p class="text-xs text-muted">Login with your <img src="/xcore_logo.png" alt="" class="inline-block h-[1em] w-[1em] align-middle object-contain" /> XCORE.GG account to run analyses and access your history across devices.</p>
          <button
            type="button"
            class="shrink-0 inline-flex items-center gap-2 rounded-xl bg-sun px-4 py-2 text-sm font-semibold text-text transition hover:bg-sun/90"
            @click="authStore.login()"
          ><img src="/xcore_logo.png" alt="" class="shrink-0 h-[1em] w-[1em] object-contain" /> Login with XCORE.GG</button>
        </div>
      </template>

      <!-- Authenticated: options + button -->
      <template v-if="authStore.isAuthenticated">

      <!-- Advanced options (always visible) -->
      <div class="border-t border-black/8 px-5 py-4 space-y-3">
        <p class="font-mono text-[10px] uppercase tracking-widest text-muted">Options</p>

        <!-- Level cap -->
        <div class="flex items-center gap-3">
          <input id="opt-level-cap" v-model="useLevelCap" type="checkbox" class="h-3.5 w-3.5 rounded accent-accent" />
          <label for="opt-level-cap" class="text-xs text-text">Level cap</label>
          <Transition enter-active-class="transition-opacity duration-150" leave-active-class="transition-opacity duration-100" enter-from-class="opacity-0" leave-to-class="opacity-0">
            <div v-if="useLevelCap" class="flex items-center gap-1.5">
              <input
                v-model.number="levelCapValue"
                type="number" min="1" max="100"
                class="w-16 rounded-lg border border-accent/20 bg-white px-2 py-1 text-center font-mono text-xs text-text outline-none focus:border-accent/50 focus:ring-1 focus:ring-accent/20"
              />
              <span class="font-mono text-[10px] text-muted">/ 100</span>
            </div>
          </Transition>
          <p class="text-[10px] text-muted">Only level-up moves at or below this level.</p>
        </div>

        <!-- Exclude tutor -->
        <div class="flex items-center gap-3">
          <input id="opt-excl-tutor" v-model="excludeTutor" type="checkbox" class="h-3.5 w-3.5 rounded accent-accent" />
          <label for="opt-excl-tutor" class="text-xs text-text">Exclude tutor moves</label>
        </div>

        <!-- Exclude egg -->
        <div class="flex items-center gap-3">
          <input id="opt-excl-egg" v-model="excludeEgg" type="checkbox" class="h-3.5 w-3.5 rounded accent-accent" />
          <label for="opt-excl-egg" class="text-xs text-text">Exclude egg moves</label>
        </div>
      </div>

      <!-- Analyse button -->
      <div class="border-t border-black/8 px-5 py-3.5">
        <div class="flex flex-wrap items-center gap-3">
          <button
            type="button"
            class="ml-auto relative z-10 flex !cursor-pointer items-center gap-2 rounded-xl bg-accent px-5 py-2.5 text-sm font-semibold text-white shadow-soft transition-none hover:bg-accent/90 disabled:!cursor-not-allowed disabled:opacity-50"
            :disabled="isAnalyzingXcore || myTeam.length === 0 || oppTeam.length === 0"
            :title="myTeam.length === 0 || oppTeam.length === 0 ? 'Add Pokémon to both teams first' : undefined"
            @click="runAnalysisXcore"
          >
            <svg v-if="isAnalyzingXcore" class="h-4 w-4 animate-spin" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" aria-hidden="true">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4l3-3-3-3v4a8 8 0 00-8 8h4z"/>
            </svg>
            {{ isAnalyzingXcore ? `Analyzing… ${elapsedLabel}` : 'Analyze' }}
          </button>
        </div>
        <p v-if="isAnalyzingXcore && xcoreThinking" class="mt-2 line-clamp-1 font-mono text-[10px] text-muted/70">{{ xcoreThinking }}</p>
        <p v-if="myTeam.length === 0 || oppTeam.length === 0" class="mt-2 text-xs text-muted/60">Add Pokémon to both teams to run an analysis.</p>
        <p v-if="analysisDuration !== null && !isAnalyzingXcore && !analysisError" class="mt-2 text-xs text-muted">
          Analysis completed in {{ analysisDuration < 60 ? `${analysisDuration}s` : `${Math.floor(analysisDuration / 60)}m ${analysisDuration % 60}s` }}
        </p>
        <p v-if="analysisError" class="mt-2 text-xs text-red-500">{{ analysisError }}</p>
      </div>
      </template>
    </div>

    <!-- ══ AI Analysis Results (always visible) ══ -->
    <div :ref="(el) => { analysisRef = el as HTMLElement | null }">

      <!-- Stale warning -->
      <div v-if="analysis && isStale" class="mb-3 flex items-center gap-2 rounded-xl border border-amber-200 bg-amber-50 px-4 py-2.5 text-xs text-amber-700">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="h-3.5 w-3.5 shrink-0" aria-hidden="true"><path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
        This analysis was run on a different team. Current team changes are not reflected below.
      </div>

      <!-- Timestamp / meta badge -->
      <div v-if="analysis && displayedMeta" class="mb-2 flex flex-wrap items-center gap-2">
        <span v-if="displayedMeta.isXcore" class="rounded-full border border-indigo-200 bg-indigo-50 px-2 py-px font-mono text-[9px] font-semibold text-indigo-600">☁ cloud</span>
        <span class="font-mono text-[10px] text-muted/60">{{ formatAge(displayedMeta.timestamp) }}</span>
        <span v-if="displayedMeta.duration != null" class="font-mono text-[10px] text-muted/50">
          · {{ displayedMeta.duration < 60 ? `${displayedMeta.duration}s` : `${Math.floor(displayedMeta.duration / 60)}m ${displayedMeta.duration % 60}s` }}
        </span>
        <template v-if="displayedMeta.options">
          <span
            v-if="displayedMeta.options.levelCap != null"
            class="rounded-full border border-violet-200 bg-violet-50 px-2 py-px font-mono text-[9px] font-semibold text-violet-600"
          >Lv. {{ displayedMeta.options.levelCap }} cap</span>
          <span
            v-if="displayedMeta.options.excludeTutor"
            class="rounded-full border border-amber-200 bg-amber-50 px-2 py-px font-mono text-[9px] font-semibold text-amber-600"
          >No tutor</span>
          <span
            v-if="displayedMeta.options.excludeEgg"
            class="rounded-full border border-rose-200 bg-rose-50 px-2 py-px font-mono text-[9px] font-semibold text-rose-600"
          >No egg</span>
        </template>
      </div>

      <MatchupAnalysisCard
        v-if="analysis"
        :analysis="analysis"
        :my-team="analysisMyTeam"
        :opp-team="analysisOppTeam"
      />
    </div>

    <!-- ══ Analysis History (always visible) ══ -->
    <div v-if="cachedHistory.length > 0" class="card-surface rounded-2xl overflow-hidden">
      <div class="border-b border-black/8 px-5 py-3">
        <p class="font-mono text-[10px] uppercase tracking-widest text-muted">Saved Analyses</p>
      </div>
      <div class="divide-y divide-black/8">
        <div
          v-for="entry in cachedHistory"
          :key="entry.id"
          :class="[
            ' flex !cursor-pointer transition-none items-center gap-3 px-4 py-2.5 transition',
            entry.id === displayedEntry?.id ? 'bg-accent/5' : 'hover:bg-black/[0.03]'
          ]"
          @click="loadEntry(entry)"
        >
          <!-- Active indicator -->
          <span
            :class="[
              'h-1.5 w-1.5 shrink-0 rounded-full',
              entry.id === displayedEntry?.id ? 'bg-accent' : 'bg-transparent'
            ]"
          />

          <!-- My team sprites -->
          <div class="flex shrink-0 -space-x-1.5">
            <img
              v-for="p in entry.myTeam"
              :key="p.id"
              :src="pokemonSprite(p)"
              :alt="p.name"
              :title="p.name"
              class="h-7 w-7 rounded-full border border-white bg-black/5 object-contain"
            />
          </div>

          <span class="font-mono text-[9px] text-muted">vs</span>

          <!-- Opp team sprites -->
          <div class="flex shrink-0 -space-x-1.5">
            <img
              v-for="p in entry.oppTeam"
              :key="p.id"
              :src="pokemonSprite(p)"
              :alt="p.name"
              :title="p.name"
              class="h-7 w-7 rounded-full border border-white bg-black/5 object-contain"
            />
          </div>

          <!-- Result badge -->
          <span
            :class="[
              'shrink-0 rounded-full px-2 py-0.5 font-mono text-[9px] font-bold',
              entry.analysis.overall_advantage === 'my_team'  ? 'bg-sky-100 text-sky-700'    :
              entry.analysis.overall_advantage === 'opponent' ? 'bg-amber-100 text-amber-700' : 'bg-gray-100 text-gray-600'
            ]"
          >
            {{ entry.analysis.overall_advantage === 'my_team' ? 'WIN' : entry.analysis.overall_advantage === 'opponent' ? 'LOSE' : 'EVEN' }}
          </span>

          <span class="font-mono text-[9px] text-muted/60">{{ formatAge(entry.timestamp) }}</span>

          <span v-if="entry.source === 'xcore'" class="rounded-full border border-indigo-200 bg-indigo-50 px-1.5 py-px font-mono text-[8px] font-semibold text-indigo-500">☁</span>

          <!-- Advanced option chips -->
          <template v-if="entry.options">
            <span v-if="entry.options.levelCap != null" class="rounded-full border border-violet-200 bg-violet-50 px-1.5 py-px font-mono text-[8px] font-semibold text-violet-600">Lv.{{ entry.options.levelCap }}</span>
            <span v-if="entry.options.excludeTutor" class="rounded-full border border-amber-200 bg-amber-50 px-1.5 py-px font-mono text-[8px] font-semibold text-amber-600">No tutor</span>
            <span v-if="entry.options.excludeEgg"   class="rounded-full border border-rose-200 bg-rose-50 px-1.5 py-px font-mono text-[8px] font-semibold text-rose-600">No egg</span>
          </template>

          <div class="ml-auto flex items-center gap-1">
            <span
              v-if="entry.id === displayedEntry?.id"
              class="rounded-lg border border-accent/20 bg-accent/10 px-2.5 py-1 font-mono text-[9px] font-semibold text-accent"
            >Loaded</span>
            <button
              class="rounded-lg border border-black/8 px-2 py-1 font-mono text-[9px] text-muted transition hover:border-red-200 hover:text-red-500"
              @click.stop="removeEntry(entry.id)"
            >✕</button>
          </div>
        </div>
      </div>
    </div>

    <!-- ══ Cloud Analysis History (authenticated users) ══ -->
    <div v-if="authStore.isAuthenticated && xcoreHistory.length > 0" class="card-surface rounded-2xl overflow-hidden">
      <div class="border-b border-black/8 px-5 py-3 flex items-center gap-2">
        <p class="font-mono text-[10px] uppercase tracking-widest text-muted">Cloud Analyses</p>
        <span class="rounded-full border border-indigo-200 bg-indigo-50 px-1.5 py-px font-mono text-[8px] font-semibold text-indigo-500">☁ xcore</span>
      </div>
      <div class="divide-y divide-black/8">
        <div
          v-for="entry in xcoreHistory"
          :key="entry.id"
          :class="[
            'flex !cursor-pointer transition-none items-center gap-3 px-4 py-2.5 transition',
            entry.id === displayedXcoreEntry?.id ? 'bg-accent/5' : 'hover:bg-black/[0.03]'
          ]"
          @click="loadXcoreEntry(entry)"
        >
          <!-- Active indicator -->
          <span
            :class="[
              'h-1.5 w-1.5 shrink-0 rounded-full',
              entry.id === displayedXcoreEntry?.id ? 'bg-accent' : 'bg-transparent'
            ]"
          />

          <!-- My team sprites -->
          <div class="flex shrink-0 -space-x-1.5">
            <img
              v-for="name in entry.my_team_names"
              :key="name"
              :src="spriteByName(name)"
              :alt="name"
              :title="name"
              class="h-7 w-7 rounded-full border border-white bg-black/5 object-contain"
            />
          </div>

          <span class="font-mono text-[9px] text-muted">vs</span>

          <!-- Opp team sprites -->
          <div class="flex shrink-0 -space-x-1.5">
            <img
              v-for="name in entry.opponent_team_names"
              :key="name"
              :src="spriteByName(name)"
              :alt="name"
              :title="name"
              class="h-7 w-7 rounded-full border border-white bg-black/5 object-contain"
            />
          </div>

          <!-- Result badge -->
          <span
            :class="[
              'shrink-0 rounded-full px-2 py-0.5 font-mono text-[9px] font-bold',
              entry.analysis.overall_advantage === 'my_team'  ? 'bg-sky-100 text-sky-700'    :
              entry.analysis.overall_advantage === 'opponent' ? 'bg-amber-100 text-amber-700' : 'bg-gray-100 text-gray-600'
            ]"
          >
            {{ entry.analysis.overall_advantage === 'my_team' ? 'WIN' : entry.analysis.overall_advantage === 'opponent' ? 'LOSE' : 'EVEN' }}
          </span>

          <span class="font-mono text-[9px] text-muted/60">{{ formatAge(new Date(entry.created_at).getTime()) }}</span>

          <!-- Options chips -->
          <template v-if="entry.options">
            <span v-if="entry.options.level_cap != null" class="rounded-full border border-violet-200 bg-violet-50 px-1.5 py-px font-mono text-[8px] font-semibold text-violet-600">Lv.{{ entry.options.level_cap }}</span>
            <span v-if="entry.options.exclude_tutor" class="rounded-full border border-amber-200 bg-amber-50 px-1.5 py-px font-mono text-[8px] font-semibold text-amber-600">No tutor</span>
            <span v-if="entry.options.exclude_egg"   class="rounded-full border border-rose-200 bg-rose-50 px-1.5 py-px font-mono text-[8px] font-semibold text-rose-600">No egg</span>
          </template>

          <div class="ml-auto flex items-center gap-1">
            <span
              v-if="entry.id === displayedXcoreEntry?.id"
              class="rounded-lg border border-accent/20 bg-accent/10 px-2.5 py-1 font-mono text-[9px] font-semibold text-accent"
            >Loaded</span>
            <button
              class="rounded-lg border border-black/8 px-2 py-1 font-mono text-[9px] text-muted transition hover:border-red-200 hover:text-red-500"
              @click.stop="removeXcoreEntry(entry.id)"
            >✕</button>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from "vue";
import { RouterLink, useRoute, useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth";
import { useQuery, useQueries } from "@tanstack/vue-query";
import type { Pokemon, PokemonListItem } from "@/types";
import { fetchPokemon, fetchPokemonList } from "@/api/client";
import { t, labelType, labelStatShort, useLocale } from "@/i18n";
import { getTypeChipStyle } from "@/constants/pokemonTypes";
import { getAttackMultiplierForTypes } from "@/constants/typeEffectiveness";
import { useDebouncedValue } from "@/composables/useDebouncedValue";
import { saveAnalysis, loadAllAnalyses, deleteAnalysis } from "@/utils/analysisCache";
import type { CachedAnalysis } from "@/utils/analysisCache";
import { fetchPokemonMoves } from "@/api/client";
import { analyzeMatchupXcore, fetchXcoreAnalyses, deleteXcoreAnalysis } from "@/services/openai";
import type { MatchupAnalysis, AnalysisOptions, XcoreAnalysis } from "@/services/openai";
import type { PokemonMove } from "@/types";
import MatchupAnalysisCard from "@/components/MatchupAnalysisCard.vue";

const route = useRoute();
const router = useRouter();
const { locale } = useLocale();
const authStore = useAuthStore();

const STAT_ORDER = ["hp", "attack", "defense", "special-attack", "special-defense", "speed"];
const MAX_STAT = 200;
const MAX_POOL = 30;
const ALL_TYPES = [
  "normal", "fighting", "flying", "poison", "ground", "rock",
  "bug", "ghost", "steel", "fire", "water", "grass",
  "electric", "psychic", "ice", "dragon", "dark"
];

// ── URL-driven team IDs ──────────────────────────────────────────────────────

function parseIds(raw: unknown): number[] {
  if (!raw || typeof raw !== "string") return [];
  return raw.split(",").map(Number).filter(n => Number.isFinite(n) && n > 0).slice(0, MAX_POOL);
}

const myTeamIds = computed<number[]>(() => parseIds(route.query.my));
const oppTeamIds = computed<number[]>(() => parseIds(route.query.opp));

function setMyTeam(ids: number[]) {
  router.replace({ query: { ...route.query, my: ids.length ? ids.join(",") : undefined } });
}
function setOppTeam(ids: number[]) {
  router.replace({ query: { ...route.query, opp: ids.length ? ids.join(",") : undefined } });
}

function addToMyTeam(id: number) {
  if (myTeamIds.value.length < MAX_POOL && !myTeamIds.value.includes(id)) {
    setMyTeam([...myTeamIds.value, id]);
  }
}
function removeFromMyTeam(index: number) {
  const next = [...myTeamIds.value];
  next.splice(index, 1);
  setMyTeam(next);
}
function clearMyTeam() { setMyTeam([]); }

function addToOppTeam(id: number) {
  if (oppTeamIds.value.length < MAX_POOL && !oppTeamIds.value.includes(id)) {
    setOppTeam([...oppTeamIds.value, id]);
  }
}
function removeFromOppTeam(index: number) {
  const next = [...oppTeamIds.value];
  next.splice(index, 1);
  setOppTeam(next);
}
function clearOppTeam() { setOppTeam([]); }

// ── Persistence ───────────────────────────────────────────────────────────────

const LS_MY  = "team-matchup.my";
const LS_OPP = "team-matchup.opp";

onMounted(() => {
  const updates: Record<string, string> = {};
  if (!route.query.my)  { const v = localStorage.getItem(LS_MY);  if (v) updates.my  = v; }
  if (!route.query.opp) { const v = localStorage.getItem(LS_OPP); if (v) updates.opp = v; }
  if (Object.keys(updates).length > 0) {
    router.replace({ query: { ...route.query, ...updates } });
  }
});

watch(myTeamIds,  ids => ids.length ? localStorage.setItem(LS_MY,  ids.join(",")) : localStorage.removeItem(LS_MY));
watch(oppTeamIds, ids => ids.length ? localStorage.setItem(LS_OPP, ids.join(",")) : localStorage.removeItem(LS_OPP));

// ── Search state ─────────────────────────────────────────────────────────────

const searchMy = ref("");
const searchOpp = ref("");
const debouncedMy = useDebouncedValue(searchMy, 250);
const debouncedOpp = useDebouncedValue(searchOpp, 250);
const showDropMy = ref(false);
const showDropOpp = ref(false);

function selectMy(p: PokemonListItem) {
  addToMyTeam(p.id);
  searchMy.value = "";
  showDropMy.value = false;
}
function selectOpp(p: PokemonListItem) {
  addToOppTeam(p.id);
  searchOpp.value = "";
  showDropOpp.value = false;
}
function onBlurMy() { setTimeout(() => { showDropMy.value = false; }, 150); }
function onBlurOpp() { setTimeout(() => { showDropOpp.value = false; }, 150); }

const searchQueryMy = useQuery({
  queryKey: computed(() => ["pokemon-search", locale.value, debouncedMy.value]),
  queryFn: () => fetchPokemonList({ q: debouncedMy.value, limit: 8 }),
  enabled: computed(() => debouncedMy.value.trim().length > 0),
});
const searchQueryOpp = useQuery({
  queryKey: computed(() => ["pokemon-search", locale.value, debouncedOpp.value]),
  queryFn: () => fetchPokemonList({ q: debouncedOpp.value, limit: 8 }),
  enabled: computed(() => debouncedOpp.value.trim().length > 0),
});

const searchResultsMy = computed(() => searchQueryMy.data.value?.data ?? []);
const searchResultsOpp = computed(() => searchQueryOpp.data.value?.data ?? []);

// ── Dynamic pool queries ──────────────────────────────────────────────────────

const myPoolResults = useQueries({
  queries: computed(() => myTeamIds.value.map(id => ({
    queryKey: ["pokemon", locale.value, id] as const,
    queryFn: () => fetchPokemon(id),
  }))),
});

const oppPoolResults = useQueries({
  queries: computed(() => oppTeamIds.value.map(id => ({
    queryKey: ["pokemon", locale.value, id] as const,
    queryFn: () => fetchPokemon(id),
  }))),
});

const mySlotData = computed(() =>
  myTeamIds.value.map((_, i) => ({
    pokemon: myPoolResults.value[i]?.data?.data ?? null,
    isPending: myPoolResults.value[i]?.isPending ?? true,
  }))
);
const oppSlotData = computed(() =>
  oppTeamIds.value.map((_, i) => ({
    pokemon: oppPoolResults.value[i]?.data?.data ?? null,
    isPending: oppPoolResults.value[i]?.isPending ?? true,
  }))
);

const myTeam = computed<Pokemon[]>(() =>
  mySlotData.value.map(s => s.pokemon).filter((p): p is Pokemon => p !== null)
);
const oppTeam = computed<Pokemon[]>(() =>
  oppSlotData.value.map(s => s.pokemon).filter((p): p is Pokemon => p !== null)
);

// ── Matchup matrices ─────────────────────────────────────────────────────────

const myStabTypes = computed(() => [...new Set(myTeam.value.flatMap(p => p.types))]);
const oppStabTypes = computed(() => [...new Set(oppTeam.value.flatMap(p => p.types))]);

interface MatrixRow {
  attackType: string;
  cells: Array<{ pokemon: Pokemon; multiplier: number }>;
  hitCount: number;
  isStab: boolean;
}

function buildMatrix(stabTypes: string[], defenderTeam: Pokemon[]): MatrixRow[] {
  const stabSet = new Set(stabTypes);
  return ALL_TYPES
    .map(type => {
      const cells = defenderTeam.map(pkmn => ({
        pokemon: pkmn,
        multiplier: getAttackMultiplierForTypes(type, pkmn.types),
      }));
      const hitCount = cells.filter(c => c.multiplier >= 2).length;
      return { attackType: type, cells, hitCount, isStab: stabSet.has(type) };
    })
    .sort((a, b) => b.hitCount - a.hitCount || (Number(b.isStab) - Number(a.isStab)) || a.attackType.localeCompare(b.attackType));
}

const myOffenseMatrix  = computed<MatrixRow[]>(() => buildMatrix(myStabTypes.value,  oppTeam.value));
const oppOffenseMatrix = computed<MatrixRow[]>(() => buildMatrix(oppStabTypes.value, myTeam.value));

const myGridStyle = computed(() => ({
  gridTemplateColumns: `88px repeat(${oppTeam.value.length}, 40px) 52px`,
}));
const oppGridStyle = computed(() => ({
  gridTemplateColumns: `88px repeat(${myTeam.value.length}, 40px) 52px`,
}));

// ── Solo-team defensive exposure (shown before opponent is added) ─────────────

const myDefenseExposure = computed(() =>
  ALL_TYPES
    .map(type => ({
      type,
      weakCount: myTeam.value.filter(p => getAttackMultiplierForTypes(type, p.types) >= 2).length,
      total: myTeam.value.length,
    }))
    .filter(e => e.weakCount > 0)
    .sort((a, b) => b.weakCount - a.weakCount || a.type.localeCompare(b.type))
);

// ── Stat comparison ──────────────────────────────────────────────────────────

function avgStats(team: Pokemon[]): Record<string, number> {
  if (!team.length) return {};
  const result: Record<string, number> = {};
  for (const stat of STAT_ORDER) {
    result[stat] = Math.round(team.reduce((sum, p) => sum + (p.stats[stat] ?? 0), 0) / team.length);
  }
  return result;
}

const myAvgStats = computed(() => avgStats(myTeam.value));
const oppAvgStats = computed(() => avgStats(oppTeam.value));

const statRows = computed(() =>
  STAT_ORDER.map(stat => {
    const a = myAvgStats.value[stat] ?? 0;
    const b = oppAvgStats.value[stat] ?? 0;
    return { stat, a, b, aWins: a > b, bWins: b > a };
  })
);

// ── Helpers ──────────────────────────────────────────────────────────────────

function formatId(id: number): string {
  return String(id).padStart(3, "0");
}

function statBarPct(value: number): number {
  return Math.min(100, Math.round((value / MAX_STAT) * 100));
}

function weakPct(weak: number, total: number): number {
  return total > 0 ? Math.round((weak / total) * 100) : 0;
}

function pokemonSprite(pkmn: Pokemon): string {
  return pkmn.sprites?.official_artwork ?? pkmn.sprites?.front_default ?? '';
}

function spriteByName(name: string): string {
  return allPokemonByName.value.get(name)?.sprite ?? '';
}

function cellClass(mult: number): string {
  if (mult === 0)    return 'border-gray-200 bg-gray-100 text-gray-400';
  if (mult >= 4)     return 'border-green-300 bg-green-100 text-green-800';
  if (mult >= 2)     return 'border-green-200 bg-green-50 text-green-700';
  if (mult <= 0.25)  return 'border-red-200 bg-red-100 text-red-700';
  if (mult < 1)      return 'border-red-100 bg-red-50 text-red-400';
  return 'border-transparent bg-transparent text-slate-300';
}

function formatMult(mult: number): string {
  if (mult === 0)   return '0';
  if (mult >= 4)    return '4×';
  if (mult >= 2)    return '2×';
  if (mult <= 0.25) return '¼';
  if (mult < 1)     return '½';
  return '·';
}

// ── Analysis state ────────────────────────────────────────────────────────────

const isAnalyzingXcore  = ref(false);
const xcoreThinking     = ref("");
const analysisError     = ref<string | null>(null);
const analysisDuration  = ref<number | null>(null);

// Advanced options
const useLevelCap   = ref(false);
const levelCapValue = ref(50);
const excludeTutor  = ref(false);
const excludeEgg    = ref(false);
const analysisOptions = computed<AnalysisOptions>(() => ({
  levelCap:      useLevelCap.value ? Math.max(1, Math.min(100, levelCapValue.value)) : null,
  excludeTutor:  excludeTutor.value,
  excludeEgg:    excludeEgg.value,
}));
const elapsedSeconds   = ref(0);
const elapsedLabel = computed(() => {
  const s = elapsedSeconds.value;
  if (s < 60) return `${s}s`;
  return `${Math.floor(s / 60)}m ${s % 60}s`;
});
let timerHandle: ReturnType<typeof setInterval> | null = null;
const statsOpen      = ref(false);
const analysisRef    = ref<HTMLElement | null>(null);

// ── Cached analysis state ─────────────────────────────────────────────────────

const displayedEntry      = ref<CachedAnalysis | null>(null);
const displayedXcoreEntry = ref<XcoreAnalysis | null>(null);
const cachedHistory       = ref<CachedAnalysis[]>([]);
const xcoreHistory        = ref<XcoreAnalysis[]>([]);
const allPokemonByName    = ref<Map<string, PokemonListItem>>(new Map());

const analysis        = computed(() => displayedXcoreEntry.value?.analysis ?? displayedEntry.value?.analysis ?? null);
const analysisMyTeam  = computed(() => displayedEntry.value?.myTeam  ?? myTeam.value);
const analysisOppTeam = computed(() => displayedEntry.value?.oppTeam ?? oppTeam.value);

const displayedMeta = computed(() => {
  if (displayedXcoreEntry.value) {
    const e = displayedXcoreEntry.value;
    return {
      timestamp: new Date(e.created_at).getTime(),
      duration:  Math.round(e.duration_ms / 1000),
      options:   { levelCap: e.options.level_cap, excludeTutor: e.options.exclude_tutor, excludeEgg: e.options.exclude_egg },
      isXcore:   true,
    };
  }
  if (displayedEntry.value) {
    const e = displayedEntry.value;
    return { timestamp: e.timestamp, duration: e.duration ?? null, options: e.options ?? null, isXcore: false };
  }
  return null;
});

const isStale = computed(() => {
  const myIds  = [...myTeamIds.value].sort().join(",");
  const oppIds = [...oppTeamIds.value].sort().join(",");
  if (displayedXcoreEntry.value) {
    const xMyIds  = displayedXcoreEntry.value.my_team_names.map(n => allPokemonByName.value.get(n)?.id).filter(Boolean).sort().join(",");
    const xOppIds = displayedXcoreEntry.value.opponent_team_names.map(n => allPokemonByName.value.get(n)?.id).filter(Boolean).sort().join(",");
    return myIds !== xMyIds || oppIds !== xOppIds;
  }
  if (!displayedEntry.value) return false;
  const cachedMyIds  = displayedEntry.value.myTeam.map(p => p.id).sort().join(",");
  const cachedOppIds = displayedEntry.value.oppTeam.map(p => p.id).sort().join(",");
  return myIds !== cachedMyIds || oppIds !== cachedOppIds;
});

function formatAge(ts: number): string {
  const mins = Math.floor((Date.now() - ts) / 60_000);
  if (mins < 1)  return "just now";
  if (mins < 60) return `${mins}m ago`;
  const h = Math.floor(mins / 60);
  if (h < 24)    return `${h}h ago`;
  return `${Math.floor(h / 24)}d ago`;
}

async function refreshXcoreHistory() {
  if (!authStore.isAuthenticated) return;
  try {
    xcoreHistory.value = await fetchXcoreAnalyses();
  } catch {
    // non-fatal — cloud history just stays empty
  }
}

onMounted(async () => {
  cachedHistory.value = loadAllAnalyses();
  fetchPokemonList({ limit: 300 }).then(r => {
    allPokemonByName.value = new Map(r.data.map(p => [p.name, p]));
  }).catch(() => {});  // non-fatal
  // Auto-load only if the most recent analysis matches the current teams exactly
  const first = cachedHistory.value[0];
  if (first) {
    const myIds  = [...myTeamIds.value].sort().join(",");
    const oppIds = [...oppTeamIds.value].sort().join(",");
    const cachedMyIds  = first.myTeam.map(p => p.id).sort().join(",");
    const cachedOppIds = first.oppTeam.map(p => p.id).sort().join(",");
    if (myIds === cachedMyIds && oppIds === cachedOppIds) {
      displayedEntry.value = first;
    }
  }
  await refreshXcoreHistory();

  const onVisibility = () => { if (document.visibilityState === 'visible') refreshXcoreHistory(); };
  document.addEventListener('visibilitychange', onVisibility);
  onUnmounted(() => document.removeEventListener('visibilitychange', onVisibility));
});

function loadEntry(entry: CachedAnalysis) {
  displayedEntry.value = entry;
  displayedXcoreEntry.value = null;
  const myIds  = entry.myTeam.map(p => p.id);
  const oppIds = entry.oppTeam.map(p => p.id);
  router.replace({
    query: {
      ...route.query,
      my:  myIds.length  ? myIds.join(",")  : undefined,
      opp: oppIds.length ? oppIds.join(",") : undefined,
    },
  });
  nextTick(() => analysisRef.value?.scrollIntoView({ behavior: "smooth", block: "start" }));
}

function loadXcoreEntry(entry: XcoreAnalysis) {
  displayedXcoreEntry.value = entry;
  displayedEntry.value = null;
  const myIds  = entry.my_team_names.map(n => allPokemonByName.value.get(n)?.id).filter(Boolean);
  const oppIds = entry.opponent_team_names.map(n => allPokemonByName.value.get(n)?.id).filter(Boolean);
  router.replace({
    query: {
      ...route.query,
      my:  myIds.length  ? myIds.join(",")  : undefined,
      opp: oppIds.length ? oppIds.join(",") : undefined,
    },
  });
  nextTick(() => analysisRef.value?.scrollIntoView({ behavior: "smooth", block: "start" }));
}

function removeEntry(id: string) {
  deleteAnalysis(id);
  cachedHistory.value = loadAllAnalyses();
  if (displayedEntry.value?.id === id) {
    displayedEntry.value = null;
  }
}

async function removeXcoreEntry(id: string) {
  try {
    await deleteXcoreAnalysis(id);
    xcoreHistory.value = xcoreHistory.value.filter(e => e.id !== id);
  } catch {
    // non-fatal
  }
}

async function runAnalysisXcore() {
  if (myTeam.value.length === 0 || oppTeam.value.length === 0) return;
  isAnalyzingXcore.value = true;
  xcoreThinking.value = "";
  analysisError.value = null;
  analysisDuration.value = null;
  elapsedSeconds.value = 0;
  const startTime = Date.now();
  timerHandle = setInterval(() => {
    elapsedSeconds.value = Math.floor((Date.now() - startTime) / 1000);
  }, 1000);
  try {
    const [myMovesArr, oppMovesArr] = await Promise.all([
      Promise.all(myTeam.value.map(p => fetchPokemonMoves(p.id).then(r => [p.id, r.data] as [number, PokemonMove[]]))),
      Promise.all(oppTeam.value.map(p => fetchPokemonMoves(p.id).then(r => [p.id, r.data] as [number, PokemonMove[]]))),
    ]);
    const myMoves  = new Map<number, PokemonMove[]>(myMovesArr);
    const oppMoves = new Map<number, PokemonMove[]>(oppMovesArr);
    const { analysis: result, duration_ms } = await analyzeMatchupXcore(
      myTeam.value, oppTeam.value, myMoves, oppMoves, analysisOptions.value,
      text => { xcoreThinking.value = text.slice(-120); },
    );
    const entry = saveAnalysis({ timestamp: Date.now(), myTeam: myTeam.value, oppTeam: oppTeam.value, analysis: result, options: analysisOptions.value, duration: Math.round(duration_ms / 1000), source: "xcore" });
    displayedEntry.value = entry;
    displayedXcoreEntry.value = null;
    cachedHistory.value  = loadAllAnalyses();
    await refreshXcoreHistory();
    await nextTick();
    analysisRef.value?.scrollIntoView({ behavior: "smooth", block: "start" });
  } catch (err) {
    analysisError.value = err instanceof Error ? err.message : "xcore analysis failed.";
  } finally {
    if (timerHandle !== null) { clearInterval(timerHandle); timerHandle = null; }
    analysisDuration.value = Math.floor((Date.now() - startTime) / 1000);
    isAnalyzingXcore.value = false;
    xcoreThinking.value = "";
  }
}
</script>
