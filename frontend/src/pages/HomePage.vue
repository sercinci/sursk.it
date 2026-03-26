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
          class="rounded-xl border border-black/10 px-4 py-2 text-sm font-semibold text-text transition hover:bg-black/5"
        >
          {{ t("home.browse_moves") }}
        </RouterLink>
      </div>
    </div>

    <div class="card-surface relative overflow-hidden rounded-3xl p-6 shadow-soft">
      <div class="absolute -right-10 -top-10 h-36 w-36 rounded-full bg-ember/20" />
      <div class="absolute -bottom-10 -left-10 h-32 w-32 rounded-full bg-accent/15" />
      <h2 class="relative font-display text-2xl font-semibold">{{ t("home.notes_title") }}</h2>
      <ul class="relative mt-4 space-y-3 text-sm text-muted">
        <li>{{ t("home.note_static_data") }}</li>
        <li>{{ t("home.note_shareable_filters") }}</li>
        <li>{{ t("home.note_single_deploy") }}</li>
      </ul>
      <p class="relative mt-5 font-mono text-xs text-muted">{{ t("home.domain") }}</p>
    </div>
  </section>
</template>

<script setup lang="ts">
import { RouterLink } from "vue-router";
import { t } from "@/i18n";
</script>
