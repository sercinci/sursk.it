<template>
  <span
    ref="triggerRef"
    class="inline-flex rounded-full outline-none ring-accent/35 transition focus-visible:ring-2 focus-visible:ring-offset-1"
    :class="focusable ? 'cursor-help' : ''"
    :tabindex="focusable ? 0 : undefined"
    :aria-label="ariaLabel"
    :aria-describedby="isOpen ? tooltipId : undefined"
    @mouseenter="openTooltip"
    @mouseleave="closeTooltipUnlessFocused"
    @focus="openTooltip"
    @blur="closeTooltip"
    @keydown.escape="closeTooltip"
  >
    <span
      class="inline-flex rounded-full border"
      :class="badgeClass"
      :style="getTypeChipStyle(type)"
    >
      {{ labelType(type) }}
    </span>

    <Teleport to="body">
      <section
        v-if="isOpen"
        :id="tooltipId"
        ref="tooltipRef"
        role="tooltip"
        class="type-effectiveness-tooltip pointer-events-none fixed z-[100] w-[min(18rem,calc(100vw-1.5rem))] rounded-xl border border-slate-200/90 bg-white/95 p-3 text-left normal-case tracking-normal text-text shadow-2xl backdrop-blur"
        :style="tooltipStyle"
      >
        <div class="space-y-2.5">
          <div v-for="group in groups" :key="group.multiplier" class="grid grid-cols-[2.5rem_1fr] items-start gap-2">
            <p class="pt-0.5 font-mono text-xs font-bold leading-5 text-muted">
              {{ formatMultiplier(group.multiplier) }}
            </p>
            <div class="flex flex-wrap gap-1">
              <span
                v-for="entryType in group.types"
                :key="entryType"
                class="rounded-full border px-2 py-0.5 text-xs font-semibold uppercase tracking-wide"
                :style="getTypeChipStyle(entryType)"
              >
                {{ labelType(entryType) }}
              </span>
            </div>
          </div>
        </div>
      </section>
    </Teleport>
  </span>
</template>

<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, ref, useId } from "vue";

import { getTypeChipStyle } from "@/constants/pokemonTypes";
import {
  getDefensiveDamageModifiers,
  getOffensiveDamageGroups
} from "@/constants/typeEffectiveness";
import { labelType, t } from "@/i18n";

type EffectivenessMode = "pokemon" | "move";

interface TooltipGroup {
  multiplier: number;
  types: string[];
}

const props = withDefaults(
  defineProps<{
    type: string;
    mode: EffectivenessMode;
    badgeClass?: string;
    focusable?: boolean;
  }>(),
  {
    badgeClass: "px-2 py-0.5 text-xs font-semibold uppercase tracking-wide",
    focusable: true
  }
);

const tooltipId = `type-effectiveness-tooltip-${useId()}`;
const triggerRef = ref<HTMLElement | null>(null);
const tooltipRef = ref<HTMLElement | null>(null);
const isOpen = ref(false);
const isPositioned = ref(false);
const left = ref(0);
const top = ref(0);

const ariaLabel = computed(() =>
  t("type_tooltip.aria", {
    type: labelType(props.type),
    context: t(props.mode === "pokemon" ? "type_tooltip.pokemon_context" : "type_tooltip.move_context")
  })
);

const groups = computed<TooltipGroup[]>(() => {
  if (props.mode === "pokemon") {
    const modifiers = getDefensiveDamageModifiers([props.type]);
    return [
      {
        multiplier: 2,
        types: modifiers.weaknesses.map((entry) => entry.type)
      },
      {
        multiplier: 0.5,
        types: modifiers.strengths.map((entry) => entry.type)
      },
      {
        multiplier: 0,
        types: modifiers.immunities.map((entry) => entry.type)
      }
    ].filter((group) => group.types.length > 0);
  }

  const offensiveGroups = getOffensiveDamageGroups([props.type]);
  const typesForMultiplier = (multiplier: number) =>
    offensiveGroups.find((group) => group.multiplier === multiplier)?.entries.map((entry) => entry.type) ?? [];

  return [
    {
      multiplier: 2,
      types: typesForMultiplier(2)
    },
    {
      multiplier: 0.5,
      types: typesForMultiplier(0.5)
    },
    {
      multiplier: 0,
      types: typesForMultiplier(0)
    }
  ].filter((group) => group.types.length > 0);
});

const tooltipStyle = computed(() => ({
  left: `${left.value}px`,
  top: `${top.value}px`,
  opacity: isPositioned.value ? "1" : "0"
}));

function formatMultiplier(multiplier: number) {
  return `${multiplier}x`;
}

function positionTooltip() {
  if (!isOpen.value || !triggerRef.value || !tooltipRef.value) {
    return;
  }

  const triggerRect = triggerRef.value.getBoundingClientRect();
  const tooltipRect = tooltipRef.value.getBoundingClientRect();
  const margin = 12;
  const gap = 8;
  const centeredLeft = triggerRect.left + triggerRect.width / 2 - tooltipRect.width / 2;
  const maxLeft = Math.max(margin, window.innerWidth - tooltipRect.width - margin);
  const spaceBelow = window.innerHeight - triggerRect.bottom;
  const spaceAbove = triggerRect.top;
  const placeAbove = spaceBelow < tooltipRect.height + gap + margin && spaceAbove > spaceBelow;
  const desiredTop = placeAbove
    ? triggerRect.top - tooltipRect.height - gap
    : triggerRect.bottom + gap;
  const maxTop = Math.max(margin, window.innerHeight - tooltipRect.height - margin);

  left.value = Math.min(Math.max(centeredLeft, margin), maxLeft);
  top.value = Math.min(Math.max(desiredTop, margin), maxTop);
  isPositioned.value = true;
}

function addPositionListeners() {
  window.addEventListener("resize", positionTooltip);
  window.addEventListener("scroll", positionTooltip, true);
}

function removePositionListeners() {
  window.removeEventListener("resize", positionTooltip);
  window.removeEventListener("scroll", positionTooltip, true);
}

function openTooltip() {
  if (isOpen.value) {
    return;
  }
  isOpen.value = true;
  isPositioned.value = false;
  addPositionListeners();
  void nextTick(positionTooltip);
}

function closeTooltip() {
  if (!isOpen.value) {
    return;
  }
  isOpen.value = false;
  isPositioned.value = false;
  removePositionListeners();
}

function closeTooltipUnlessFocused() {
  if (document.activeElement !== triggerRef.value) {
    closeTooltip();
  }
}

onBeforeUnmount(removePositionListeners);
</script>

<style scoped>
.type-effectiveness-tooltip {
  transition: opacity 100ms ease-out;
}
</style>
