import { defineStore } from "pinia";
import type { LocationQuery } from "vue-router";

export const usePokedexFiltersStore = defineStore("pokedexFilters", {
  state: () => ({
    q: "",
    typeFilters: [] as string[],
    ev_yield: "",
    hoenn_only: false,
    offset: 0,
    limit: 24
  }),
  actions: {
    setFromRoute(query: LocationQuery) {
      this.q = typeof query.q === "string" ? query.q : "";
      this.typeFilters =
        typeof query.type === "string"
          ? query.type
              .split(",")
              .map((value) => value.trim())
              .filter(Boolean)
          : [];
      this.ev_yield = typeof query.ev_yield === "string" ? query.ev_yield : "";
      this.hoenn_only =
        (typeof query.hoenn_only === "string" &&
          (query.hoenn_only === "1" || query.hoenn_only.toLowerCase() === "true")) ||
        false;
      this.offset =
        typeof query.offset === "string" && !Number.isNaN(Number(query.offset))
          ? Math.max(0, Number(query.offset))
          : 0;
    },
    setQ(value: string) {
      this.q = value;
    },
    setOffset(value: number) {
      this.offset = Math.max(0, value);
    },
    setTypeFilters(value: string[]) {
      this.typeFilters = [...new Set(value.map((item) => item.trim()).filter(Boolean))];
    },
    setEvYield(value: string) {
      this.ev_yield = value;
    },
    setHoennOnly(value: boolean) {
      this.hoenn_only = Boolean(value);
    },
    clearFilters() {
      this.q = "";
      this.typeFilters = [];
      this.ev_yield = "";
      this.hoenn_only = false;
      this.offset = 0;
    },
    toRouteQuery() {
      return {
        ...(this.q ? { q: this.q } : {}),
        ...(this.typeFilters.length ? { type: this.typeFilters.join(",") } : {}),
        ...(this.ev_yield ? { ev_yield: this.ev_yield } : {}),
        ...(this.hoenn_only ? { hoenn_only: "1" } : {}),
        ...(this.offset > 0 ? { offset: String(this.offset) } : {})
      };
    }
  }
});
