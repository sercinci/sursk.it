<template>
  <div class="relative min-h-screen overflow-x-clip px-4 pb-12 sm:px-6 lg:px-8">
    <div class="pointer-events-none absolute inset-0 -z-10 overflow-hidden">
      <div class="absolute -left-16 top-12 h-56 w-56 rounded-full bg-accent/15 blur-3xl" />
      <div class="absolute left-1/2 top-8 h-40 w-40 -translate-x-1/2 rounded-full bg-sun/15 blur-3xl" />
      <div class="absolute right-0 top-28 h-64 w-64 rounded-full bg-ember/10 blur-3xl" />
      <div class="absolute bottom-0 left-1/3 h-72 w-72 rounded-full bg-mint/50 blur-3xl" />
    </div>

    <AppHeader />
    <main class="mx-auto mt-8 w-full max-w-6xl">
      <RouterView />
    </main>
  </div>
</template>

<script setup lang="ts">
import { RouterView } from "vue-router";

import AppHeader from "@/components/AppHeader.vue";
</script>
