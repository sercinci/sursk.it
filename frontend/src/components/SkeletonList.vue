<template>
  <div class="grid gap-3 lg:grid-cols-2 xl:grid-cols-3">
    <div
      v-for="item in 8"
      :key="item"
      class="card-surface h-20 animate-pulse rounded-2xl bg-white/80 lg:h-44"
    />
  </div>
</template>
