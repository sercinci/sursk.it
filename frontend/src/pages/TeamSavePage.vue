<template>
  <div class="mx-auto max-w-5xl space-y-5 px-0 py-6 sm:px-4">
    <header class="space-y-3">
      <RouterLink
        :to="{ name: 'team', query: teamPageReturnQuery }"
        class="inline-flex items-center gap-1.5 rounded-full border border-black/10 bg-white/70 px-3 py-1.5 text-xs font-semibold text-muted transition hover:border-accent/25 hover:text-accent"
      >
        <span aria-hidden="true">←</span>
        {{ t("team_save.back") }}
      </RouterLink>
      <div class="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p class="font-mono text-xs uppercase tracking-widest text-accent">{{ t("team.stored.eyebrow") }}</p>
          <h1 class="font-display text-3xl font-bold text-text">
            {{ isEditing ? t("team_save.title_edit") : t("team_save.title_new") }}
          </h1>
          <p class="text-sm text-muted">{{ t("team_save.subtitle") }}</p>
          <p
            v-if="draftTeam"
            :class="['mt-2 inline-flex rounded-full border px-2.5 py-1 font-mono text-[10px] font-semibold uppercase tracking-wide', draftStatusClass]"
          >
            {{ draftStatusLabel }}
          </p>
        </div>
        <div v-if="draftTeam" class="flex flex-wrap gap-2">
          <button
            v-if="isEditing"
            type="button"
            class="rounded-xl border border-black/10 bg-white/70 px-4 py-2 text-sm font-semibold text-muted transition hover:border-accent/30 hover:text-accent"
            @click="duplicateDraftTeam"
          >
            {{ t("team_save.duplicate") }}
          </button>
          <button
            v-if="isEditing"
            type="button"
            class="rounded-xl border border-red-200 bg-red-50 px-4 py-2 text-sm font-semibold text-red-700 transition hover:bg-red-100"
            @click="deleteDraftTeam"
          >
            {{ t("team.stored.delete") }}
          </button>
          <button
            type="button"
            class="rounded-xl bg-accent px-4 py-2 text-sm font-semibold text-white shadow-soft transition hover:bg-accent/90 disabled:cursor-not-allowed disabled:opacity-45"
            :disabled="!canSaveDraft"
            @click="saveDraftTeam"
          >
            {{ t("team_save.save") }}
          </button>
        </div>
      </div>
    </header>

    <div v-if="!draftTeam" class="card-surface rounded-2xl px-6 py-10 text-center">
      <p class="text-sm text-muted">{{ t("team_save.empty") }}</p>
      <RouterLink
        :to="{ name: 'team', query: teamPageReturnQuery }"
        class="mt-4 inline-flex rounded-xl bg-accent px-4 py-2 text-sm font-semibold text-white shadow-soft transition hover:bg-accent/90"
      >
        {{ t("team_save.back") }}
      </RouterLink>
    </div>

    <template v-else>
      <article class="card-surface overflow-hidden rounded-2xl">
        <div class="grid grid-cols-1 gap-4 p-5 sm:grid-cols-[minmax(0,1fr)_auto] sm:items-end">
          <label class="min-w-0">
            <span class="mb-1 block font-mono text-[10px] uppercase tracking-wide text-muted">{{ t("team.stored.name_placeholder") }}</span>
            <input
              v-model="draftTeam.name"
              type="text"
              class="h-10 w-full rounded-xl border border-accent/20 bg-white/80 px-3 text-sm font-semibold text-text outline-none placeholder:text-muted/50 focus:border-accent/50 focus:ring-1 focus:ring-accent/20"
              :placeholder="t('team.stored.name_placeholder')"
            />
          </label>
          <div class="flex flex-wrap items-center gap-2">
            <div class="flex shrink-0 -space-x-2">
              <div
                v-for="member in draftTeam.members"
                :key="member.id"
                class="flex h-10 w-10 items-center justify-center rounded-full border border-white bg-black/5"
              >
                <img
                  v-if="getPokemon(member.pokemonId)"
                  :src="pokemonSprite(getPokemon(member.pokemonId)!)"
                  :alt="getPokemon(member.pokemonId)!.name"
                  class="h-full w-full rounded-full object-contain"
                />
                <span v-else class="font-mono text-[9px] text-muted">#{{ formatId(member.pokemonId) }}</span>
              </div>
            </div>
            <span class="rounded-full border border-black/10 bg-white/70 px-2.5 py-1 font-mono text-[10px] text-muted">
              {{ draftTeam.members.length }}/{{ STORED_TEAM_MAX_MEMBERS }} Pokémon
            </span>
          </div>
        </div>
        <div class="border-t border-black/8 p-5">
          <div class="grid grid-cols-1 gap-3 sm:grid-cols-[minmax(0,1fr)_auto] sm:items-end">
            <div class="relative min-w-0">
              <label for="team-save-add-pokemon" class="mb-1 block font-mono text-[10px] uppercase tracking-wide text-muted">
                {{ t("team_save.add_pokemon") }}
              </label>
              <input
                id="team-save-add-pokemon"
                v-model="searchAdd"
                type="text"
                :disabled="!canAddPokemon"
                :placeholder="canAddPokemon ? t('team.search_placeholder') : t('team_save.team_full')"
                class="h-10 w-full rounded-xl border border-accent/20 bg-white/80 px-3 text-sm text-text outline-none placeholder:text-muted/50 focus:border-accent/50 focus:ring-1 focus:ring-accent/20 disabled:cursor-not-allowed disabled:bg-black/5 disabled:text-muted"
                @focus="showDropAdd = true"
                @input="showDropAdd = true"
                @blur="onBlurAdd"
              />
              <div
                v-if="showDropAdd && searchResultsAdd.length > 0"
                class="absolute left-0 right-0 top-full z-50 mt-1 max-h-56 overflow-y-auto rounded-xl border border-accent/15 bg-white shadow-lg"
              >
                <button
                  v-for="p in searchResultsAdd"
                  :key="p.id"
                  type="button"
                  class="flex w-full items-center gap-2 px-3 py-2 text-left transition hover:bg-accent/10 disabled:!cursor-not-allowed disabled:opacity-40"
                  :disabled="isPokemonInDraft(p.id)"
                  @mousedown.prevent="addPokemonToDraft(p)"
                >
                  <img v-if="p.sprite" :src="p.sprite" :alt="p.name" class="h-7 w-7 shrink-0 object-contain" />
                  <div v-else class="h-7 w-7 shrink-0 rounded bg-black/5" />
                  <span class="shrink-0 font-mono text-xs text-muted">#{{ formatId(p.id) }}</span>
                  <span class="min-w-0 truncate text-sm font-medium capitalize">{{ p.name }}</span>
                  <div class="ml-auto flex shrink-0 gap-1">
                    <TypeEffectivenessBadge
                      v-for="type in p.types"
                      :key="type"
                      :type="type"
                      mode="pokemon"
                      badge-class="px-1.5 py-0.5 text-[9px] font-semibold uppercase"
                      :focusable="false"
                    />
                  </div>
                </button>
              </div>
            </div>
            <span class="rounded-xl border border-black/10 bg-white/70 px-3 py-2 text-center font-mono text-[10px] font-semibold uppercase tracking-wide text-muted">
              {{ draftTeam.members.length }}/{{ STORED_TEAM_MAX_MEMBERS }}
            </span>
          </div>
        </div>
      </article>

      <article
        v-for="member in draftTeam.members"
        :key="member.id"
        class="card-surface relative overflow-visible rounded-2xl"
        :class="isMemberDropdownActive(member) ? 'z-40' : 'z-0'"
      >
        <div class="flex flex-wrap items-center gap-3 border-b border-black/8 px-5 py-4">
          <img
            v-if="getPokemon(member.pokemonId)"
            :src="pokemonSprite(getPokemon(member.pokemonId)!)"
            :alt="getPokemon(member.pokemonId)!.name"
            class="h-14 w-14 shrink-0 object-contain"
          />
          <div v-else class="h-14 w-14 shrink-0 animate-pulse rounded-xl bg-black/10" />
          <div class="min-w-0 flex-1">
            <p class="font-mono text-xs text-muted">#{{ formatId(member.pokemonId) }}</p>
            <h2 class="truncate font-display text-lg font-semibold capitalize text-text">
              {{ getPokemon(member.pokemonId)?.name ?? t("team_save.loading_pokemon") }}
            </h2>
            <div v-if="getPokemon(member.pokemonId)" class="mt-1 flex flex-wrap gap-1">
              <TypeEffectivenessBadge
                v-for="type in getPokemon(member.pokemonId)!.types"
                :key="type"
                :type="type"
                mode="pokemon"
                badge-class="px-2 py-0.5 text-[10px] font-semibold uppercase"
              />
            </div>
          </div>
          <RouterLink
            v-if="isEditing"
            :to="createCompareLink(member)"
            class="rounded-md p-1 text-muted transition hover:bg-accent/10 hover:text-accent"
            :title="t('team_save.compare_pokemon', { name: memberDisplayName(member) })"
            :aria-label="t('team_save.compare_pokemon', { name: memberDisplayName(member) })"
          >
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="h-3.5 w-3.5" aria-hidden="true">
              <path d="m16 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z"/>
              <path d="m2 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z"/>
              <path d="M7 21h10"/>
              <path d="M12 3v18"/>
              <path d="M3 7h2c2 0 5-1 7-2 2 1 5 2 7 2h2"/>
            </svg>
          </RouterLink>
          <button
            type="button"
            class="rounded-xl border border-black/10 bg-white/70 px-3 py-1.5 text-xs font-semibold text-muted transition hover:border-red-200 hover:text-red-600 disabled:cursor-not-allowed disabled:opacity-40"
            :disabled="draftTeam.members.length <= 1"
            :aria-label="t('team_save.remove_pokemon', { name: memberDisplayName(member) })"
            @click="removeDraftMember(member.id)"
          >
            {{ t("team_save.remove") }}
          </button>
        </div>

        <div class="space-y-4 p-5">
          <div class="grid grid-cols-1 gap-3 sm:grid-cols-2">
            <div class="relative min-w-0">
              <label
                :for="`team-save-nature-${member.id}`"
                class="mb-1 block font-mono text-[10px] uppercase tracking-wide text-muted"
              >
                {{ t("compare.nature") }}
              </label>
              <input
                :id="`team-save-nature-${member.id}`"
                :value="getNatureInputValue(member)"
                type="text"
                class="h-9 w-full rounded-xl border border-black/10 bg-white/80 px-2 text-sm text-text outline-none focus:border-accent/50 focus:ring-1 focus:ring-accent/20"
                :aria-label="`${memberDisplayName(member)} ${t('compare.nature')}`"
                :placeholder="getNatureInputPlaceholder(member)"
                @focus="openNatureSearch(member)"
                @input="onNatureSearchInput(member, $event)"
                @keydown.enter.prevent="commitNatureSearch(member)"
                @blur="closeNatureSearch(member)"
              />
              <div
                v-if="isNatureSearchOpen(member)"
                class="absolute left-0 right-0 top-full z-50 mt-1 max-h-56 overflow-y-auto rounded-xl border border-accent/15 bg-white py-1 shadow-lg"
              >
                <button
                  type="button"
                  class="flex w-full items-center px-3 py-2 text-left text-sm text-muted transition hover:bg-accent/10 hover:text-text"
                  @mousedown.prevent="selectMemberNature(member, null)"
                >
                  {{ t("team.stored.no_nature") }}
                </button>
                <button
                  v-for="nature in getFilteredNatureOptions(member)"
                  :key="`${member.id}-${nature.id}`"
                  type="button"
                  class="flex w-full items-center justify-between gap-2 px-3 py-2 text-left text-sm transition hover:bg-accent/10"
                  @mousedown.prevent="selectMemberNature(member, nature.id)"
                >
                  <span class="font-medium text-text">{{ getNatureName(nature) }}</span>
                  <span class="font-mono text-[10px] text-muted">({{ formatNatureModifier(nature) }})</span>
                </button>
                <p
                  v-if="getFilteredNatureOptions(member).length === 0"
                  class="px-3 py-2 text-xs text-muted"
                >
                  {{ t("team.stored.no_matching_natures") }}
                </p>
              </div>
            </div>
            <label>
              <span class="mb-1 block font-mono text-[10px] uppercase tracking-wide text-muted">{{ t("compare.ability") }}</span>
              <select
                v-model="member.ability"
                class="h-9 w-full rounded-xl border border-black/10 bg-white/80 px-2 text-sm capitalize text-text outline-none focus:border-accent/50 focus:ring-1 focus:ring-accent/20"
              >
                <option
                  v-for="ability in getPokemon(member.pokemonId)?.abilities ?? []"
                  :key="ability.name"
                  :value="ability.name"
                >
                  {{ ability.display_name ?? ability.name.replaceAll("-", " ") }}
                </option>
              </select>
            </label>
          </div>

          <div class="grid grid-cols-2 gap-2 sm:grid-cols-3 lg:grid-cols-6">
            <div
              v-for="stat in STORED_TEAM_STAT_ORDER"
              :key="`${member.id}-${stat}`"
              class="rounded-xl border border-black/8 bg-white/70 p-2.5"
            >
              <p class="mb-2 text-center font-mono text-[10px] font-bold uppercase text-muted">{{ labelStatShort(stat) }}</p>
              <div class="grid grid-cols-2 gap-1.5">
                <label class="min-w-0">
                  <span class="sr-only">{{ t("compare.iv") }}</span>
                  <input
                    v-model.number="member.ivs[stat]"
                    type="number"
                    min="0"
                    max="31"
                    step="1"
                    class="h-8 w-full rounded-lg border border-black/10 bg-white px-1 text-center font-mono text-xs text-text outline-none focus:border-accent/50 focus:ring-1 focus:ring-accent/20"
                    :aria-label="`${labelStatShort(stat)} ${t('compare.iv')}`"
                    @input="onMemberIvInput(member, stat, $event)"
                    @change="clampMemberStats(member)"
                  />
                  <span class="mt-0.5 block text-center font-mono text-[9px] uppercase text-muted">{{ t("compare.iv") }}</span>
                </label>
                <label class="min-w-0">
                  <span class="sr-only">{{ t("compare.ev") }}</span>
                  <input
                    v-model.number="member.evs[stat]"
                    type="number"
                    min="0"
                    max="252"
                    step="1"
                    class="h-8 w-full rounded-lg border border-black/10 bg-white px-1 text-center font-mono text-xs text-text outline-none focus:border-accent/50 focus:ring-1 focus:ring-accent/20"
                    :aria-label="`${labelStatShort(stat)} ${t('compare.ev')}`"
                    @input="onMemberEvInput(member, stat, $event)"
                    @change="clampMemberStats(member)"
                  />
                  <span class="mt-0.5 block text-center font-mono text-[9px] uppercase text-muted">{{ t("compare.ev") }}</span>
                </label>
              </div>
            </div>
          </div>

          <div>
            <p class="mb-2 font-mono text-[10px] uppercase tracking-wide text-muted">{{ t("team.stored.moves") }}</p>
            <div class="grid grid-cols-1 gap-2 sm:grid-cols-2 lg:grid-cols-4">
              <div v-for="slot in moveSlots" :key="`${member.id}-move-${slot}`" class="relative min-w-0">
                <span class="sr-only">{{ t("team.stored.move_slot", { slot }) }}</span>
                <input
                  :value="getMoveInputValue(member, slot)"
                  type="text"
                  class="h-9 w-full rounded-xl border border-black/10 bg-white/80 px-2 text-sm capitalize text-text outline-none focus:border-accent/50 focus:ring-1 focus:ring-accent/20"
                  :aria-label="t('team.stored.move_slot', { slot })"
                  :placeholder="getMoveInputPlaceholder(member, slot)"
                  @focus="openMoveSearch(member, slot)"
                  @input="onMoveSearchInput(member, slot, $event)"
                  @keydown.enter.prevent="commitMoveSearch(member, slot)"
                  @blur="closeMoveSearch(member, slot)"
                />
                <div
                  v-if="isMoveSearchOpen(member, slot)"
                  class="absolute left-0 right-0 top-full z-50 mt-1 max-h-56 overflow-y-auto rounded-xl border border-accent/15 bg-white py-1 shadow-lg"
                >
                  <button
                    type="button"
                    class="flex w-full items-center px-3 py-2 text-left text-sm text-muted transition hover:bg-accent/10 hover:text-text"
                    @mousedown.prevent="selectMemberMove(member, slot, '')"
                  >
                    {{ t("team.stored.no_move") }}
                  </button>
                  <button
                    v-for="move in getFilteredMoveOptions(member, slot)"
                    :key="`${member.id}-${slot}-${move.name}`"
                    type="button"
                    class="flex w-full items-center gap-2 px-3 py-2 text-left text-sm capitalize text-text transition hover:bg-accent/10 disabled:!cursor-not-allowed disabled:opacity-40"
                    :disabled="isMoveSelectedInOtherSlot(member, slot, move.name)"
                    @mousedown.prevent="selectMemberMove(member, slot, move.name)"
                  >
                    {{ move.display_name ?? move.name.replaceAll("-", " ") }}
                  </button>
                  <p
                    v-if="getFilteredMoveOptions(member, slot).length === 0"
                    class="px-3 py-2 text-xs text-muted"
                  >
                    {{ t("team.stored.no_matching_moves") }}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </article>

      <div class="sticky bottom-3 z-20 flex flex-col gap-3 rounded-2xl border border-black/10 bg-white/90 p-3 shadow-soft backdrop-blur sm:flex-row sm:items-center sm:justify-between">
        <p :class="['inline-flex w-fit rounded-full border px-2.5 py-1 font-mono text-[10px] font-semibold uppercase tracking-wide', draftStatusClass]">
          {{ draftStatusLabel }}
        </p>
        <button
          type="button"
          class="rounded-xl bg-accent px-5 py-2 text-sm font-semibold text-white shadow-soft transition hover:bg-accent/90 disabled:cursor-not-allowed disabled:opacity-45"
          :disabled="!canSaveDraft"
          @click="saveDraftTeam"
        >
          {{ t("team_save.save") }}
        </button>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from "vue";
import { RouterLink, useRoute, useRouter } from "vue-router";
import { useQueries, useQuery } from "@tanstack/vue-query";
import type { Pokemon, PokemonListItem, PokemonMove } from "@/types";
import { fetchPokemon, fetchPokemonList, fetchPokemonMoves } from "@/api/client";
import TypeEffectivenessBadge from "@/components/TypeEffectivenessBadge.vue";
import { t, labelStatShort, useLocale } from "@/i18n";
import { POKEMON_NATURES, getNatureById, type PokemonNature } from "@/constants/natures";
import { useDebouncedValue } from "@/composables/useDebouncedValue";
import {
  STORED_TEAM_MAX_MEMBERS,
  STORED_TEAM_MAX_MOVES,
  STORED_TEAM_STAT_ORDER,
  createStoredPokemonBuild,
  createStoredTeam,
  duplicateStoredTeam,
  encodeStoredMemberRef,
  loadStoredTeams,
  saveStoredTeams,
  touchStoredTeam,
  type StoredPokemonBuild,
  type StoredTeamStat,
  type StoredTeam,
} from "@/utils/localTeams";

const route = useRoute();
const router = useRouter();
const { locale } = useLocale();

const MAX_POOL = STORED_TEAM_MAX_MEMBERS;
const moveSlots = Array.from({ length: STORED_TEAM_MAX_MOVES }, (_, index) => index + 1);
const storedTeams = ref<StoredTeam[]>(loadStoredTeams());
const editingTeamId = computed(() => typeof route.query.id === "string" ? route.query.id : null);
const isEditing = computed(() => editingTeamId.value !== null);
const sourceSide = computed<"my" | "opp">(() => route.query.side === "opp" ? "opp" : "my");

function getRouteTeamQuery(side: "my" | "opp"): string | undefined {
  const rawValue = route.query[side];
  return typeof rawValue === "string" && rawValue.trim() ? rawValue : undefined;
}

const teamPageReturnQuery = computed(() => ({
  ...(getRouteTeamQuery("my") ? { my: getRouteTeamQuery("my") } : {}),
  ...(getRouteTeamQuery("opp") ? { opp: getRouteTeamQuery("opp") } : {}),
}));

function parseIds(raw: unknown): number[] {
  if (!raw || typeof raw !== "string") return [];
  return raw.split(",").map(Number).filter(n => Number.isFinite(n) && n > 0).slice(0, MAX_POOL);
}

function cloneStoredTeam(team: StoredTeam): StoredTeam {
  return {
    ...team,
    members: team.members.map(member => ({
      ...member,
      ivs: { ...member.ivs },
      evs: { ...member.evs },
      moves: [...member.moves],
    })),
  };
}

function createInitialDraft(): StoredTeam | null {
  if (editingTeamId.value) {
    const existing = storedTeams.value.find(team => team.id === editingTeamId.value);
    return existing ? cloneStoredTeam(existing) : null;
  }
  const ids = parseIds(route.query.members);
  if (!ids.length) {
    return null;
  }
  const name = t("team.stored.default_name", { count: storedTeams.value.length + 1 });
  return createStoredTeam(name, ids);
}

const draftTeam = ref<StoredTeam | null>(createInitialDraft());
const initialDraftSnapshot = ref(serializeDraft(draftTeam.value));
const hasUnsavedChanges = computed(() => serializeDraft(draftTeam.value) !== initialDraftSnapshot.value);
const canSaveDraft = computed(() => draftTeam.value !== null && (!isEditing.value || hasUnsavedChanges.value));
const draftStatusLabel = computed(() => {
  if (!draftTeam.value) return "";
  if (!isEditing.value) return t("team_save.status_new");
  return hasUnsavedChanges.value ? t("team_save.status_unsaved") : t("team_save.status_saved");
});
const draftStatusClass = computed(() => {
  if (!isEditing.value) return "border-sky-200 bg-sky-50 text-sky-700";
  return hasUnsavedChanges.value
    ? "border-amber-200 bg-amber-50 text-amber-700"
    : "border-emerald-200 bg-emerald-50 text-emerald-700";
});
const draftPokemonIds = computed(() => [
  ...new Set(draftTeam.value?.members.map(member => member.pokemonId) ?? [])
]);
const canAddPokemon = computed(() => (draftTeam.value?.members.length ?? 0) < STORED_TEAM_MAX_MEMBERS);

const pokemonResults = useQueries({
  queries: computed(() => draftPokemonIds.value.map(id => ({
    queryKey: ["pokemon", locale.value, id] as const,
    queryFn: () => fetchPokemon(id),
  }))),
});

const moveResults = useQueries({
  queries: computed(() => draftPokemonIds.value.map(id => ({
    queryKey: ["pokemon-moves", locale.value, id] as const,
    queryFn: () => fetchPokemonMoves(id),
  }))),
});

const pokemonById = computed(() => {
  const entries: [number, Pokemon][] = [];
  draftPokemonIds.value.forEach((id, index) => {
    const pokemon = pokemonResults.value[index]?.data?.data ?? null;
    if (pokemon) entries.push([id, pokemon]);
  });
  return new Map(entries);
});

const movesByPokemonId = computed(() => {
  const entries: [number, PokemonMove[]][] = [];
  draftPokemonIds.value.forEach((id, index) => {
    const moves = moveResults.value[index]?.data?.data ?? null;
    if (moves) entries.push([id, moves]);
  });
  return new Map(entries);
});

const searchAdd = ref("");
const showDropAdd = ref(false);
const activeNatureSearchMemberId = ref<string | null>(null);
const natureSearchByMemberId = ref<Record<string, string>>({});
const activeMoveSearchKey = ref<string | null>(null);
const moveSearchByKey = ref<Record<string, string>>({});
const debouncedAdd = useDebouncedValue(searchAdd, 250);
const searchAddQuery = useQuery({
  queryKey: computed(() => ["pokemon-search", locale.value, "team-save-add", debouncedAdd.value]),
  queryFn: () => fetchPokemonList({ q: debouncedAdd.value, limit: 8 }),
  enabled: computed(() => canAddPokemon.value && debouncedAdd.value.trim().length > 0),
});
const searchResultsAdd = computed(() => searchAddQuery.data.value?.data ?? []);

function getPokemon(pokemonId: number): Pokemon | null {
  return pokemonById.value.get(pokemonId) ?? null;
}

function getMoveOptions(pokemonId: number): PokemonMove[] {
  return movesByPokemonId.value.get(pokemonId) ?? [];
}

function getNatureName(nature: PokemonNature): string {
  return nature.names[locale.value];
}

function formatNatureOption(nature: PokemonNature): string {
  return `${getNatureName(nature)} (${formatNatureModifier(nature)})`;
}

function getSelectedNatureLabel(member: StoredPokemonBuild): string {
  const selectedNature = getNatureById(member.nature);
  return selectedNature ? formatNatureOption(selectedNature) : "";
}

function getNatureInputValue(member: StoredPokemonBuild): string {
  if (
    activeNatureSearchMemberId.value === member.id
    || Object.prototype.hasOwnProperty.call(natureSearchByMemberId.value, member.id)
  ) {
    return natureSearchByMemberId.value[member.id] ?? "";
  }
  return getSelectedNatureLabel(member);
}

function getNatureInputPlaceholder(member: StoredPokemonBuild): string {
  return getSelectedNatureLabel(member) || t("compare.nature_placeholder");
}

function openNatureSearch(member: StoredPokemonBuild) {
  activeNatureSearchMemberId.value = member.id;
  natureSearchByMemberId.value = { ...natureSearchByMemberId.value, [member.id]: "" };
}

function closeNatureSearch(member: StoredPokemonBuild) {
  setTimeout(() => {
    if (activeNatureSearchMemberId.value === member.id) {
      activeNatureSearchMemberId.value = null;
    }
    const next = { ...natureSearchByMemberId.value };
    delete next[member.id];
    natureSearchByMemberId.value = next;
  }, 150);
}

function isNatureSearchOpen(member: StoredPokemonBuild): boolean {
  return activeNatureSearchMemberId.value === member.id;
}

function onNatureSearchInput(member: StoredPokemonBuild, event: Event) {
  const input = event.target as HTMLInputElement | null;
  activeNatureSearchMemberId.value = member.id;
  natureSearchByMemberId.value = {
    ...natureSearchByMemberId.value,
    [member.id]: input?.value ?? "",
  };
}

function normalizeSearchText(value: string): string {
  return value
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .trim()
    .toLowerCase()
    .replaceAll("-", " ");
}

function normalizeNatureSearch(value: string): string {
  return normalizeSearchText(value);
}

function getFilteredNatureOptions(member: StoredPokemonBuild): PokemonNature[] {
  const query = normalizeNatureSearch(natureSearchByMemberId.value[member.id] ?? "");
  if (!query) return POKEMON_NATURES;
  return POKEMON_NATURES.filter(nature => {
    const searchable = [
      nature.id,
      nature.names.en,
      nature.names.it,
      formatNatureModifier(nature),
    ].join(" ");
    return normalizeNatureSearch(searchable).includes(query);
  });
}

function selectMemberNature(member: StoredPokemonBuild, natureId: string | null) {
  member.nature = natureId;
  activeNatureSearchMemberId.value = null;
  const next = { ...natureSearchByMemberId.value };
  delete next[member.id];
  natureSearchByMemberId.value = next;
}

function commitNatureSearch(member: StoredPokemonBuild) {
  const firstNature = getFilteredNatureOptions(member)[0];
  if (firstNature) {
    selectMemberNature(member, firstNature.id);
  }
}

function moveSlotKey(member: StoredPokemonBuild, slot: number): string {
  return `${member.id}:${slot}`;
}

function formatMoveName(moveName: string): string {
  return moveName.replaceAll("-", " ");
}

function getSelectedMoveLabel(member: StoredPokemonBuild, slot: number): string {
  const selectedMove = member.moves[slot - 1] ?? "";
  if (!selectedMove) return "";
  return getMoveOptions(member.pokemonId).find(move => move.name === selectedMove)?.display_name
    ?? formatMoveName(selectedMove);
}

function getMoveInputValue(member: StoredPokemonBuild, slot: number): string {
  const key = moveSlotKey(member, slot);
  if (
    activeMoveSearchKey.value === key
    || Object.prototype.hasOwnProperty.call(moveSearchByKey.value, key)
  ) {
    return moveSearchByKey.value[key] ?? "";
  }
  return getSelectedMoveLabel(member, slot);
}

function getMoveInputPlaceholder(member: StoredPokemonBuild, slot: number): string {
  return getSelectedMoveLabel(member, slot) || t("team.stored.move_search_placeholder");
}

function openMoveSearch(member: StoredPokemonBuild, slot: number) {
  const key = moveSlotKey(member, slot);
  activeMoveSearchKey.value = key;
  moveSearchByKey.value = { ...moveSearchByKey.value, [key]: "" };
}

function closeMoveSearch(member: StoredPokemonBuild, slot: number) {
  const key = moveSlotKey(member, slot);
  setTimeout(() => {
    if (activeMoveSearchKey.value === key) {
      activeMoveSearchKey.value = null;
    }
    const next = { ...moveSearchByKey.value };
    delete next[key];
    moveSearchByKey.value = next;
  }, 150);
}

function isMoveSearchOpen(member: StoredPokemonBuild, slot: number): boolean {
  return activeMoveSearchKey.value === moveSlotKey(member, slot);
}

function isMemberDropdownActive(member: StoredPokemonBuild): boolean {
  return activeNatureSearchMemberId.value === member.id
    || (activeMoveSearchKey.value?.startsWith(`${member.id}:`) ?? false);
}

function onMoveSearchInput(member: StoredPokemonBuild, slot: number, event: Event) {
  const key = moveSlotKey(member, slot);
  const input = event.target as HTMLInputElement | null;
  activeMoveSearchKey.value = key;
  moveSearchByKey.value = {
    ...moveSearchByKey.value,
    [key]: input?.value ?? "",
  };
}

function normalizeMoveSearch(value: string): string {
  return normalizeSearchText(value);
}

function getMoveSearchTerms(move: PokemonMove): string[] {
  return [
    move.name,
    formatMoveName(move.name),
    move.display_name ?? "",
    ...Object.values(move.localized_names ?? {}),
  ];
}

function getFilteredMoveOptions(member: StoredPokemonBuild, slot: number): PokemonMove[] {
  const key = moveSlotKey(member, slot);
  const query = normalizeMoveSearch(moveSearchByKey.value[key] ?? "");
  return getMoveOptions(member.pokemonId)
    .filter(move => {
      if (!query) return true;
      return getMoveSearchTerms(move).some(term => normalizeMoveSearch(term).includes(query));
    })
    .slice(0, 12);
}

function isMoveSelectedInOtherSlot(member: StoredPokemonBuild, slot: number, moveName: string): boolean {
  return member.moves.some((move, index) => index !== slot - 1 && move === moveName);
}

function selectMemberMove(member: StoredPokemonBuild, slot: number, moveName: string) {
  if (moveName && isMoveSelectedInOtherSlot(member, slot, moveName)) return;
  member.moves[slot - 1] = moveName;
  dedupeMemberMoves(member);
  const key = moveSlotKey(member, slot);
  activeMoveSearchKey.value = null;
  const next = { ...moveSearchByKey.value };
  delete next[key];
  moveSearchByKey.value = next;
}

function commitMoveSearch(member: StoredPokemonBuild, slot: number) {
  const firstAvailableMove = getFilteredMoveOptions(member, slot)
    .find(move => !isMoveSelectedInOtherSlot(member, slot, move.name));
  if (firstAvailableMove) {
    selectMemberMove(member, slot, firstAvailableMove.name);
  }
}

function memberDisplayName(member: StoredPokemonBuild): string {
  return getPokemon(member.pokemonId)?.name ?? `#${formatId(member.pokemonId)}`;
}

function isPokemonInDraft(pokemonId: number): boolean {
  return draftTeam.value?.members.some(member => member.pokemonId === pokemonId) ?? false;
}

function addPokemonToDraft(pokemon: PokemonListItem) {
  if (!draftTeam.value || !canAddPokemon.value || isPokemonInDraft(pokemon.id)) return;
  draftTeam.value.members = [...draftTeam.value.members, createStoredPokemonBuild(pokemon.id)];
  searchAdd.value = "";
  showDropAdd.value = false;
}

function removeDraftMember(memberId: string) {
  if (!draftTeam.value || draftTeam.value.members.length <= 1) return;
  draftTeam.value.members = draftTeam.value.members.filter(member => member.id !== memberId);
}

function onBlurAdd() {
  setTimeout(() => {
    showDropAdd.value = false;
  }, 150);
}

function prefillMissingAbilities() {
  if (!draftTeam.value) return;
  for (const member of draftTeam.value.members) {
    if (member.ability) continue;
    const defaultAbility = getPokemon(member.pokemonId)?.abilities[0]?.name ?? null;
    if (defaultAbility) {
      member.ability = defaultAbility;
    }
  }
}

watch(pokemonById, () => {
  prefillMissingAbilities();
}, { immediate: true });

function serializeDraft(team: StoredTeam | null): string {
  if (!team) return "";
  return JSON.stringify({
    name: team.name,
    members: team.members.map(member => ({
      pokemonId: member.pokemonId,
      ivs: { ...member.ivs },
      evs: { ...member.evs },
      nature: member.nature,
      ability: member.ability,
      moves: [...member.moves],
    })),
  });
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

function onMemberIvInput(member: StoredPokemonBuild, stat: StoredTeamStat, event: Event) {
  member.ivs[stat] = clampBoundedStatInput(event, 31);
}

function onMemberEvInput(member: StoredPokemonBuild, stat: StoredTeamStat, event: Event) {
  member.evs[stat] = clampBoundedStatInput(event, 252);
}

function clampMemberStats(member: StoredPokemonBuild) {
  for (const stat of STORED_TEAM_STAT_ORDER) {
    member.ivs[stat] = clampWholeNumber(member.ivs[stat], 0, 31, 31);
    member.evs[stat] = clampWholeNumber(member.evs[stat], 0, 252, 0);
  }
}

function dedupeMemberMoves(member: StoredPokemonBuild) {
  const seen = new Set<string>();
  const moves = member.moves
    .map(move => move.trim())
    .filter(move => {
      if (!move || seen.has(move)) return false;
      seen.add(move);
      return true;
    })
    .slice(0, STORED_TEAM_MAX_MOVES);
  member.moves = [...moves, ...Array(Math.max(0, STORED_TEAM_MAX_MOVES - moves.length)).fill("")];
}

function normalizeDraft(team: StoredTeam): StoredTeam {
  const next = cloneStoredTeam(team);
  next.name = next.name.trim() || t("team.stored.default_name", { count: storedTeams.value.length + 1 });
  next.members = next.members.slice(0, STORED_TEAM_MAX_MEMBERS);
  for (const member of next.members) {
    clampMemberStats(member);
    dedupeMemberMoves(member);
  }
  return touchStoredTeam(next);
}

function saveDraftTeam() {
  if (!draftTeam.value || !canSaveDraft.value) return;
  const savedTeam = normalizeDraft(draftTeam.value);
  const memberQuery = savedTeam.members.map(member => member.pokemonId).join(",");
  const returnQuery = {
    ...teamPageReturnQuery.value,
    [sourceSide.value]: memberQuery,
  };
  storedTeams.value = [
    savedTeam,
    ...storedTeams.value.filter(team => team.id !== savedTeam.id),
  ].sort((a, b) => b.updatedAt - a.updatedAt);
  saveStoredTeams(storedTeams.value);
  router.push({
    name: "team",
    query: returnQuery,
  });
}

function duplicateDraftTeam() {
  if (!draftTeam.value) return;
  const sourceTeam = normalizeDraft(draftTeam.value);
  const duplicatedTeam = duplicateStoredTeam(
    sourceTeam,
    t("team_save.duplicate_name", { name: sourceTeam.name })
  );
  storedTeams.value = [duplicatedTeam, ...storedTeams.value].sort((a, b) => b.updatedAt - a.updatedAt);
  saveStoredTeams(storedTeams.value);
  draftTeam.value = cloneStoredTeam(duplicatedTeam);
  initialDraftSnapshot.value = serializeDraft(draftTeam.value);
  router.replace({ name: "team-save", query: { id: duplicatedTeam.id } });
}

function deleteDraftTeam() {
  if (!draftTeam.value) return;
  storedTeams.value = storedTeams.value.filter(team => team.id !== draftTeam.value?.id);
  saveStoredTeams(storedTeams.value);
  router.push({ name: "team" });
}

function createCompareLink(member: StoredPokemonBuild) {
  return {
    name: "compare",
    query: {
      a: member.pokemonId,
      teamA: encodeStoredMemberRef(editingTeamId.value ?? member.id, member.id),
    },
  };
}

function pokemonSprite(pokemon: Pokemon): string {
  return pokemon.sprites?.official_artwork ?? pokemon.sprites?.front_default ?? "";
}

function formatId(id: number): string {
  return String(id).padStart(3, "0");
}

function formatNatureModifier(nature: PokemonNature): string {
  if (!nature.increasedStat || !nature.decreasedStat) {
    return t("compare.nature_neutral");
  }
  return `+${labelStatShort(nature.increasedStat)}, -${labelStatShort(nature.decreasedStat)}`;
}
</script>
