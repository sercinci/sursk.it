<template>
  <section class="grid gap-8 md:grid-cols-[1.2fr_1fr] md:items-center">
    <div>
      <p class="font-mono text-xs uppercase tracking-[0.2em] text-accent">{{ t("home.eyebrow") }}</p>
      <h1 class="mt-3 font-display text-4xl font-bold leading-tight text-text sm:text-5xl">
        {{ t("home.title") }}
      </h1>
      <p class="mt-4 max-w-xl text-base leading-relaxed text-muted">
        {{ t("home.description") }}
      </p>

      <div class="mt-6 flex flex-wrap gap-3">
        <RouterLink
          to="/pokedex"
          class="rounded-xl bg-accent px-4 py-2 text-sm font-semibold text-white shadow-soft transition hover:brightness-110"
        >
          {{ t("home.open_pokedex") }}
        </RouterLink>
        <RouterLink
          to="/moves"
          class="rounded-xl border border-accent/15 bg-white/70 px-4 py-2 text-sm font-semibold text-text transition hover:bg-accent/10"
        >
          {{ t("home.browse_moves") }}
        </RouterLink>
      </div>
    </div>

    <div class="card-surface relative overflow-hidden rounded-[2rem] p-6 shadow-soft">
      <div class="absolute -right-12 -top-12 h-40 w-40 rounded-full bg-sun/20 blur-2xl" />
      <div class="absolute -bottom-14 -left-10 h-36 w-36 rounded-full bg-accent/15 blur-2xl" />
      <div class="relative flex items-start justify-between gap-5">
        <div class="max-w-xs">
          <p class="font-mono text-xs uppercase tracking-[0.2em] text-accent">{{ t("brand.tagline") }}</p>
          <h2 class="mt-2 font-display text-2xl font-semibold">{{ t("home.notes_title") }}</h2>
          <ul class="mt-4 space-y-3 text-sm leading-relaxed text-muted">
            <li class="flex items-start gap-2">
              <span class="mt-1.5 h-1.5 w-1.5 rounded-full bg-accent" />
              <span>{{ t("home.note_static_data") }}</span>
            </li>
            <li class="flex items-start gap-2">
              <span class="mt-1.5 h-1.5 w-1.5 rounded-full bg-sun" />
              <span>{{ t("home.note_shareable_filters") }}</span>
            </li>
            <li class="flex items-start gap-2">
              <span class="mt-1.5 h-1.5 w-1.5 rounded-full bg-accent" />
              <span>{{ t("home.note_single_deploy") }}</span>
            </li>
          </ul>
          <p class="mt-5 font-mono text-xs text-muted">{{ t("home.domain") }}</p>
        </div>

        <div class="relative hidden shrink-0 sm:block">
          <div class="absolute inset-0 rounded-full bg-white/75 blur-xl" />
          <div class="relative flex h-32 w-32 items-center justify-center rounded-full border border-sun/40 bg-white/70 p-3">
            <div class="absolute right-4 top-4 h-3 w-3 rounded-full bg-sun shadow-[0_0_16px_rgba(244,211,94,0.75)]" />
            <img src="/surskit.png" alt="Surskit artwork" class="h-full w-full object-contain" />
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { RouterLink } from "vue-router";
import { t } from "@/i18n";
</script>
