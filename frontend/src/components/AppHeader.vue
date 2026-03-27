<template>
  <header class="mx-auto flex w-full max-w-6xl flex-col gap-3 pt-6 sm:flex-row sm:items-center sm:justify-between">
    <div class="flex w-full items-center justify-between sm:w-auto">
      <RouterLink to="/" class="group flex items-center gap-3" @click="closeMenu">
        <span class="relative flex h-12 w-12 items-center justify-center overflow-hidden rounded-2xl border border-accent/15 bg-white/70 shadow-soft backdrop-blur">
          <span class="absolute inset-0 bg-gradient-to-br from-mint via-white/80 to-sun/25" />
          <span class="absolute right-1.5 top-1.5 h-2.5 w-2.5 rounded-full bg-sun shadow-[0_0_10px_rgba(244,211,94,0.65)]" />
          <img
            src="/surskit.png"
            alt="Surskit logo"
            class="relative h-10 w-10 object-contain transition duration-200 group-hover:-translate-y-0.5 group-hover:scale-[1.03]"
          />
        </span>
        <span class="min-w-0">
          <span class="block font-display text-2xl font-semibold tracking-tight text-text">
            Sursk<span class="text-sun">.</span>it
          </span>
          <span class="block font-mono text-[10px] uppercase tracking-[0.24em] text-muted">{{ t("brand.tagline") }}</span>
        </span>
      </RouterLink>
      <button
        type="button"
        class="inline-flex h-10 w-10 items-center justify-center rounded-full border border-accent/15 bg-white/80 text-text backdrop-blur transition hover:bg-accent/10 sm:hidden"
        :aria-expanded="isMenuOpen"
        aria-controls="primary-nav"
        aria-label="Toggle menu"
        @click="toggleMenu"
      >
        <span class="relative h-4 w-5">
          <span
            class="absolute left-0 top-0 h-0.5 w-5 rounded bg-current transition-transform duration-200"
            :class="isMenuOpen ? 'translate-y-[7px] rotate-45' : ''"
          />
          <span
            class="absolute left-0 top-[7px] h-0.5 w-5 rounded bg-current transition-opacity duration-200"
            :class="isMenuOpen ? 'opacity-0' : 'opacity-100'"
          />
          <span
            class="absolute left-0 top-[14px] h-0.5 w-5 rounded bg-current transition-transform duration-200"
            :class="isMenuOpen ? '-translate-y-[7px] -rotate-45' : ''"
          />
        </span>
      </button>
    </div>

    <nav
      id="primary-nav"
      class="w-full rounded-3xl border border-accent/15 bg-white/92 px-2 py-2 shadow-soft backdrop-blur sm:w-auto sm:rounded-full sm:bg-white/70 sm:py-1"
      :class="isMenuOpen ? 'block sm:block' : 'hidden sm:block'"
    >
      <div class="flex w-full flex-col items-stretch gap-2 sm:w-auto sm:flex-row sm:flex-wrap sm:items-center sm:justify-start">
        <RouterLink
          v-for="item in navItems"
          :key="item.to"
          :to="item.to"
          class="rounded-full px-3 py-1.5 text-center text-sm font-medium text-muted transition hover:bg-accent/10 hover:text-text"
          active-class="bg-accent text-white hover:bg-accent hover:text-white"
          @click="closeMenu"
        >
          {{ item.label }}
        </RouterLink>
        <div class="grid grid-cols-2 gap-1 rounded-full border border-accent/15 bg-white p-1 text-xs sm:hidden">
          <button
            type="button"
            class="rounded-full px-3 py-1.5 font-semibold transition"
            :class="locale === 'en' ? 'bg-accent text-white' : 'text-muted hover:bg-accent/10 hover:text-text'"
            @click="setAppLocale('en')"
          >
            EN
          </button>
          <button
            type="button"
            class="rounded-full px-3 py-1.5 font-semibold transition"
            :class="locale === 'it' ? 'bg-accent text-white' : 'text-muted hover:bg-accent/10 hover:text-text'"
            @click="setAppLocale('it')"
          >
            IT
          </button>
        </div>
        <label
          class="relative z-10 hidden items-center justify-center gap-1 rounded-full border border-accent/15 bg-white px-2 py-1 text-xs sm:ml-1 sm:inline-flex"
        >
          <select
            :value="locale"
            class="cursor-pointer appearance-auto rounded-full bg-white px-2 py-1 text-sm font-semibold text-text outline-none"
            @change="onLocaleChange"
          >
            <option value="en">EN</option>
            <option value="it">IT</option>
          </select>
        </label>
      </div>
    </nav>
  </header>
</template>

<script setup lang="ts">
import { computed, ref, watch } from "vue";
import { RouterLink, useRoute } from "vue-router";
import type { AppLocale } from "@/i18n";
import { t, useLocale } from "@/i18n";

const { locale, setLocale } = useLocale();
const route = useRoute();
const isMenuOpen = ref(false);

const navItems = computed(() => [
  { label: t("nav.pokedex"), to: "/pokedex" },
  { label: t("nav.moves"), to: "/moves" },
  { label: t("nav.locations"), to: "/locations" },
  { label: t("nav.about"), to: "/about" }
]);

watch(
  () => route.fullPath,
  () => {
    isMenuOpen.value = false;
  }
);

function toggleMenu() {
  isMenuOpen.value = !isMenuOpen.value;
}

function closeMenu() {
  isMenuOpen.value = false;
}

function setAppLocale(nextLocale: AppLocale) {
  setLocale(nextLocale);
  closeMenu();
}

function onLocaleChange(event: Event) {
  const target = event.target as HTMLSelectElement | null;
  if (!target) {
    return;
  }
  setLocale(target.value as AppLocale);
}
</script>
