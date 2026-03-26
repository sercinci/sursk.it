<template>
  <section class="space-y-6">
    <div>
      <p class="font-mono text-xs uppercase tracking-[0.18em] text-accent">{{ t("about.eyebrow") }}</p>
      <h1 class="font-display text-3xl font-bold text-text">{{ t("about.title") }}</h1>
      <p class="mt-2 max-w-3xl text-sm leading-relaxed text-muted">
        {{ t("about.intro") }}
      </p>
    </div>

    <article class="card-surface rounded-2xl p-5">
      <h2 class="font-display text-2xl font-semibold text-text">{{ t("about.purpose_title") }}</h2>
      <p class="mt-3 text-sm leading-relaxed text-muted">
        {{ t("about.purpose_body_1") }}
      </p>
      <p class="mt-3 text-sm leading-relaxed text-muted">
        {{ t("about.purpose_body_2") }}
      </p>
      <p class="mt-3 text-sm leading-relaxed text-muted">
        {{ t("about.purpose_body_3") }}
      </p>
    </article>

    <article class="card-surface rounded-2xl p-5">
      <h2 class="font-display text-2xl font-semibold text-text">{{ t("about.name_title") }}</h2>
      <blockquote class="mt-4 px-1">
        <p class="text-lg italic leading-relaxed text-muted sm:text-xl">
          {{ t("about.name_body_1") }}
        </p>
        <footer class="mt-4 text-right font-mono text-xs uppercase tracking-[0.24em] text-muted">F. E.</footer>
      </blockquote>
    </article>

    <article class="card-surface rounded-2xl p-5">
      <h2 class="font-display text-2xl font-semibold text-text">{{ t("about.thanks_title") }}</h2>
      <p class="mt-3 text-sm leading-relaxed text-muted">
        {{ t("about.thanks_body") }}
      </p>
      <ul class="mt-3 list-inside list-disc space-y-1 text-sm text-text">
        <li>
          <a
            href="https://pokemmo.shoutwiki.com/wiki/Main_Page"
            target="_blank"
            rel="noopener noreferrer"
            class="underline decoration-black/30 underline-offset-2 hover:decoration-black/60"
          >
            Pokemmo shoutwiki
          </a>
        </li>
        <li>
          <a
            href="https://pkmn.help/"
            target="_blank"
            rel="noopener noreferrer"
            class="underline decoration-black/30 underline-offset-2 hover:decoration-black/60"
          >
            pkmn.help
          </a>
        </li>
        <li>
          <a
            href="https://pokemmohub.com/"
            target="_blank"
            rel="noopener noreferrer"
            class="underline decoration-black/30 underline-offset-2 hover:decoration-black/60"
          >
            pokemmohub.com
          </a>
        </li>
        <li>
          <a
            href="https://bulbapedia.bulbagarden.net/"
            target="_blank"
            rel="noopener noreferrer"
            class="underline decoration-black/30 underline-offset-2 hover:decoration-black/60"
          >
            bulbapedia
          </a>
        </li>
        <li>
          <a
            href="https://wiki.pokemoncentral.it/"
            target="_blank"
            rel="noopener noreferrer"
            class="underline decoration-black/30 underline-offset-2 hover:decoration-black/60"
          >
            wiki.pokemoncentral.it
          </a>
        </li>
      </ul>
    </article>

    <article class="card-surface rounded-2xl p-5">
      <h2 class="font-display text-2xl font-semibold text-text">{{ t("about.legal_title") }}</h2>
      <p class="mt-3 text-sm leading-relaxed text-muted">
        {{ t("about.legal_body_1") }}
      </p>
      <p class="mt-3 text-sm leading-relaxed text-muted">
        {{ t("about.legal_body_2") }}
      </p>
    </article>

    <p class="px-2 pb-2 text-center font-mono text-xs tracking-[0.14em] text-muted/80">
      {{ t("about.signature_prefix") }}
      <a
        href="https://ercole.dev"
        target="_blank"
        rel="noopener noreferrer"
        class="underline decoration-black/30 underline-offset-2 transition hover:text-text hover:decoration-black/60"
      >ercole.dev</a>. {{ t("about.signature_suffix") }}
    </p>
  </section>
</template>

<script setup lang="ts">
import { t } from "@/i18n";
</script>
