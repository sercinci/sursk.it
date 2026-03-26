import { ref, watch, type Ref } from "vue";

export function useDebouncedValue(source: Ref<string>, delay = 300) {
  const debounced = ref(source.value);
  let timer: ReturnType<typeof setTimeout> | null = null;

  watch(source, (value) => {
    if (timer) {
      clearTimeout(timer);
    }
    timer = setTimeout(() => {
      debounced.value = value;
    }, delay);
  });

  return debounced;
}
