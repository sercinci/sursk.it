import { createRouter, createWebHistory } from "vue-router";

import AboutPage from "@/pages/AboutPage.vue";
import ComparisonPage from "@/pages/ComparisonPage.vue";
import LocationDetailPage from "@/pages/LocationDetailPage.vue";
import LocationsPage from "@/pages/LocationsPage.vue";
import MovesPage from "@/pages/MovesPage.vue";
import PokedexPage from "@/pages/PokedexPage.vue";
import PokemonDetailPage from "@/pages/PokemonDetailPage.vue";
import TeamSavePage from "@/pages/TeamSavePage.vue";
import TeamMatchupPage from "@/pages/TeamMatchupPage.vue";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/", name: "pokedex", component: PokedexPage, alias: "/pokedex" },
    { path: "/pokemon/:id", name: "pokemon-detail", component: PokemonDetailPage },
    { path: "/moves", name: "moves", component: MovesPage },
    { path: "/locations", name: "locations", component: LocationsPage },
    { path: "/compare", name: "compare", component: ComparisonPage },
    { path: "/team", name: "team", component: TeamMatchupPage },
    { path: "/team/save", name: "team-save", component: TeamSavePage },
    { path: "/about", name: "about", component: AboutPage },
    { path: "/locations/:locationName", name: "location-detail", component: LocationDetailPage }
  ]
});

export default router;
