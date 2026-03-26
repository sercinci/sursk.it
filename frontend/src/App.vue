<template>
  <div class="min-h-screen px-4 pb-12 sm:px-6 lg:px-8">
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
