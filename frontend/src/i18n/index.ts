import { computed, readonly, ref } from "vue";

export type AppLocale = "en" | "it";

const STORAGE_KEY = "surskit.locale";
const SUPPORTED_LOCALES: AppLocale[] = ["en", "it"];

const UI_MESSAGES: Record<AppLocale, Record<string, string>> = {
  en: {
    "brand.tagline": "Walks on water",

    "nav.pokedex": "Pokédex",
    "nav.moves": "Moves",
    "nav.locations": "Locations",
    "nav.about": "About",
    "nav.language": "Language",

    "about.eyebrow": "About",
    "about.title": "About Sursk.it",
    "about.intro":
      "Sursk.it is a lightweight place to explore the Pokemon data my friends and I use for our 3rd generation PokeMMO tournament. The goal is simple: keep the information we need in one fast, clean interface instead of spreading it across a dozen tabs.",
    "about.purpose_title": "What this site is for",
    "about.purpose_body_1":
      "This project started as a personal tool built around a specific use case: team building, move checking, matchup research, and quick lookups during tournament prep. Existing community resources already do excellent work. Sursk.it is not meant to replace them. It is meant to bring the pieces I rely on into a single, fluid experience that is easier to navigate and faster to use.",
    "about.purpose_body_2":
      "The primary focus is still my own workflow, so the product will continue to evolve around practical needs. If it is useful for your runs, your tournaments, or your own planning, use it freely.",
    "about.purpose_body_3":
      "Contributions are welcome anytime. If you want to improve the data, the tools, or the interface, you are invited to take part.",
    "about.name_title": "Why Surskit?",
    "about.name_body_1":
      "\"I picked Surskit because it can walk on water. Building something that does not sink seemed promising.\"",
    "about.thanks_title": "Thank you",
    "about.thanks_body":
      "This project stands on top of a lot of excellent community work. These are some of the resources that helped shape it:",
    "about.legal_title": "Legal info",
    "about.legal_body_1":
      "Pokémon © 2002–2026 Pokémon. © 1995–2026 Nintendo/Creatures Inc./GAME FREAK inc. ™, ® and Pokémon character names are trademarks of Nintendo.",
    "about.legal_body_2": "No copyright or trademark infringement is intended in using Pokémon content on this page.",
    "about.signature_prefix": "Developed by Pokemon Trainer",
    "about.signature_suffix": "Built with patience, data, and a few Repels.",

    "home.eyebrow": "Glide Through Hoenn",
    "home.title": "A lightweight Pokédex for fast Gen 3 PokeMMO prep.",
    "home.description": "Sursk.it brings Pokemon, moves, and Hoenn locations into one fluid interface so you can search quickly, compare cleanly, and stop wrestling with a stack of tabs.",
    "home.open_pokedex": "Open Pokédex",
    "home.browse_moves": "Browse Moves",
    "home.notes_title": "Why It Feels Light",
    "home.note_static_data": "Static data, fast load times, minimal noise.",
    "home.note_shareable_filters": "URL-driven filters for quick, shareable searches.",
    "home.note_single_deploy": "Built to stay simple instead of becoming a dashboard.",
    "home.domain": "Domain: sursk.it",

    "pokedex.title": "Pokédex Search",
    "pokedex.subtitle": "Search by name or Pokédex number and open a Pokémon to see details.",
    "pokedex.showing": "Showing {count} of {total}",
    "pokedex.prev": "Prev",
    "pokedex.next": "Next",
    "pokedex.page": "Page {page}",
    "pokedex.empty": "No Pokémon found.",

    "filters.search": "Search",
    "filters.search_placeholder": "Search by name or number (e.g. pikachu or 25)",
    "filters.hoenn_only": "Gen.3 only",
    "filters.type": "Type",
    "filters.ev_yield": "EV Yield",
    "filters.ev_all": "All EV yields",
    "filters.clear": "Clear filters",

    "moves.title": "Moves",
    "moves.subtitle": "Complete move list loaded from static JSON.",
    "moves.filter_placeholder": "Filter moves",
    "moves.filter.type": "Type",
    "moves.filter.category": "Category",
    "moves.filter.all_types": "All types",
    "moves.filter.all_categories": "All categories",
    "moves.column.move": "Move",
    "moves.column.type": "Type",
    "moves.column.category": "Category",
    "moves.column.power": "Power",
    "moves.column.pp": "PP",
    "moves.column.accuracy": "Accuracy",
    "moves.description": "Description",
    "moves.effectiveness": "Effectiveness",
    "moves.no_matchups": "No type matchup data available.",
    "moves.loading_detail": "Loading move details...",
    "moves.no_description": "No description available.",
    "moves.tm_purchase": "TM purchase",
    "moves.price": "Price",
    "moves.learners": "Learners",
    "moves.loading_learners": "Loading learner data...",
    "moves.no_learners": "No learner data available.",

    "locations.region": "Hoenn Region",
    "locations.title": "Locations",
    "locations.subtitle": "Browse each Hoenn area and preview the capturable Pokémon sprites.",
    "locations.search": "Search Locations",
    "locations.search_placeholder": "Type a location name (e.g. Slateport, Route 119, Granite)",
    "locations.locations_count": "{count} locations",
    "locations.no_match_section": "No matching locations in this section.",
    "locations.no_section": "No locations in this section yet.",
    "locations.none": "No Hoenn location data found.",
    "locations.section.settlements": "Settlements",
    "locations.section.routes": "Routes",
    "locations.section.landmarks": "Landmarks",
    "locations.section.settlements_desc": "Cities and towns, including places where water encounters may be available.",
    "locations.section.routes_desc": "Route areas across Hoenn, including overworld and underwater route variants.",
    "locations.section.landmarks_desc": "Caves, forests, towers, and other non-route, non-settlement areas.",

    "location_detail.back": "Back to Locations",
    "location_detail.loading": "Loading location details...",
    "location_detail.region": "PokéMMO • Hoenn",
    "location_detail.encounter_entries": "{count} encounter entries",
    "location_detail.birdview": "Birdview",
    "location_detail.birdview_none": "Birdview image not available.",
    "location_detail.birdview_source": "Birdview Source",
    "location_detail.map": "Map",
    "location_detail.map_none": "Map image not available.",
    "location_detail.map_source": "Map Source",
    "location_detail.page": "PokéMMO Page",
    "location_detail.encounters": "Encounters",
    "location_detail.column.pokemon": "Pokémon",
    "location_detail.column.sub_area": "Sub-area",
    "location_detail.column.levels": "Levels",
    "location_detail.column.method": "Method",
    "location_detail.column.rate": "Rate",
    "location_detail.column.time": "Time",
    "location_detail.any_period": "Any",
    "location_detail.alt_birdview": "{name} birdview",
    "location_detail.alt_birdview_labeled": "{name} {label}",
    "location_detail.alt_map": "{name} map",

    "pokemon.loading": "Loading Pokémon...",
    "pokemon.not_found": "Pokémon not found.",
    "pokemon.abilities": "Abilities",
    "pokemon.no_abilities": "No abilities available.",
    "pokemon.statistics": "Statistics",
    "pokemon.damage_dealt": "Damage Dealt (STAB)",
    "pokemon.damage_taken": "Damage Taken",
    "pokemon.moves_list": "Moves List",
    "pokemon.location": "Location",
    "pokemon.loading_moves": "Loading moves...",
    "pokemon.no_hoenn_locations": "No Hoenn encounter locations available.",
    "pokemon.filters": "Filters",
    "pokemon.clear": "Clear",
    "pokemon.filter.type": "Type",
    "pokemon.filter.category": "Category",
    "pokemon.filter.learn": "Learn",
    "pokemon.stab_damage_to": "STAB moves deal {multiplier} damage to",
    "pokemon.takes_from": "Takes {multiplier} from",
    "pokemon.ev_yield": "EV Yield",
    "pokemon.ev_none": "None",
    "pokemon.no_evolution_data": "No evolution data.",
    "pokemon.evolution_loading": "Loading...",
  },
  it: {
    "brand.tagline": "Walks on water",

    "nav.pokedex": "Pokédex",
    "nav.moves": "Mosse",
    "nav.locations": "Luoghi",
    "nav.about": "Info",
    "nav.language": "Lingua",

    "about.eyebrow": "Info",
    "about.title": "Cos'è Sursk.it",
    "about.intro":
      "Sursk.it è un punto di accesso leggero per esplorare i dati Pokémon che io e i miei amici usiamo per il nostro torneo PokeMMO di terza generazione. L'obiettivo è semplice: tenere tutte le informazioni che ci servono in un'interfaccia veloce e pulita, invece di spargerle su una dozzina di schede aperte.",
    "about.purpose_title": "A cosa serve questo sito",
    "about.purpose_body_1":
      "Questo progetto è nato come strumento personale attorno a un'esigenza concreta: costruzione team, verifica mosse, studio dei matchup e consultazioni rapide durante la preparazione al torneo. Le risorse della community che già esistono fanno un ottimo lavoro. Sursk.it non vuole sostituirle. Vuole raccogliere in un'unica esperienza fluida le parti che uso più spesso, in modo più rapido e più semplice da navigare.",
    "about.purpose_body_2":
      "Il focus principale resta il mio flusso di lavoro, quindi il prodotto continuerà a evolversi seguendo esigenze pratiche. Se può esserti utile per run, tornei o pianificazione personale, usalo liberamente.",
    "about.purpose_body_3":
      "I contributi sono sempre benvenuti. Se vuoi migliorare i dati, gli strumenti o l'interfaccia, puoi partecipare in qualsiasi momento.",
    "about.name_title": "Perché Surskit?",
    "about.name_body_1":
      "\"Ho scelto Surskit perché può camminare sull'acqua. Costruire qualcosa che non affondi sembrava un buon inizio.\"",
    "about.thanks_title": "Ringraziamenti",
    "about.thanks_body":
      "Questo progetto si appoggia a molto del grande lavoro fatto dalla community. Queste sono alcune delle risorse che lo hanno aiutato a prendere forma:",
    "about.legal_title": "Informazioni legali",
    "about.legal_body_1":
      "Pokémon © 2002–2026 Pokémon. © 1995–2026 Nintendo/Creatures Inc./GAME FREAK inc. ™, ® e i nomi dei personaggi Pokémon sono marchi registrati di Nintendo.",
    "about.legal_body_2": "Non si intende violare alcun copyright o marchio tramite l'uso di contenuti Pokémon in questa pagina.",
    "about.signature_prefix": "Sviluppato dal Pokémon Trainer",
    "about.signature_suffix": "Creato con pazienza, dati e qualche Repellente.",

    "home.eyebrow": "Scivola In Hoenn",
    "home.title": "Un Pokédex leggero per preparare in fretta il Gen 3 su PokeMMO.",
    "home.description": "Sursk.it riunisce Pokémon, mosse e luoghi di Hoenn in un'unica interfaccia fluida, così puoi cercare in fretta, confrontare con chiarezza e smettere di combattere con una pila di schede aperte.",
    "home.open_pokedex": "Apri Pokédex",
    "home.browse_moves": "Sfoglia mosse",
    "home.notes_title": "Perché Sembra Leggero",
    "home.note_static_data": "Dati statici, caricamenti rapidi, poco rumore.",
    "home.note_shareable_filters": "Filtri guidati da URL per ricerche rapide e condivisibili.",
    "home.note_single_deploy": "Pensato per restare semplice, non per diventare una dashboard pesante.",
    "home.domain": "Dominio: sursk.it",

    "pokedex.title": "Ricerca Pokédex",
    "pokedex.subtitle": "Cerca per nome o numero Pokédex e apri un Pokémon per vedere i dettagli.",
    "pokedex.showing": "Mostrati {count} di {total}",
    "pokedex.prev": "Prec",
    "pokedex.next": "Succ",
    "pokedex.page": "Pagina {page}",
    "pokedex.empty": "Nessun Pokémon trovato.",

    "filters.search": "Cerca",
    "filters.search_placeholder": "Cerca per nome o numero (es. pikachu o 25)",
    "filters.hoenn_only": "Solo Gen.3",
    "filters.type": "Tipo",
    "filters.ev_yield": "EV",
    "filters.ev_all": "Tutte le EV",
    "filters.clear": "Cancella filtri",

    "moves.title": "Mosse",
    "moves.subtitle": "Elenco completo mosse caricato da JSON statico.",
    "moves.filter_placeholder": "Filtra mosse",
    "moves.filter.type": "Tipo",
    "moves.filter.category": "Categoria",
    "moves.filter.all_types": "Tutti i tipi",
    "moves.filter.all_categories": "Tutte le categorie",
    "moves.column.move": "Mossa",
    "moves.column.type": "Tipo",
    "moves.column.category": "Categoria",
    "moves.column.power": "Potenza",
    "moves.column.pp": "PP",
    "moves.column.accuracy": "Precisione",
    "moves.description": "Descrizione",
    "moves.effectiveness": "Efficacia",
    "moves.no_matchups": "Nessun dato matchup disponibile.",
    "moves.loading_detail": "Caricamento dettagli mossa...",
    "moves.no_description": "Nessuna descrizione disponibile.",
    "moves.tm_purchase": "Acquisto MT",
    "moves.price": "Prezzo",
    "moves.learners": "Pokémon che imparano",
    "moves.loading_learners": "Caricamento elenco Pokémon...",
    "moves.no_learners": "Nessun dato apprendimento disponibile.",

    "locations.region": "Regione di Hoenn",
    "locations.title": "Luoghi",
    "locations.subtitle": "Esplora le aree di Hoenn e visualizza i Pokémon catturabili.",
    "locations.search": "Cerca luogo",
    "locations.search_placeholder": "Inserisci un luogo (es. Porto Selcepoli, Percorso 119)",
    "locations.locations_count": "{count} luoghi",
    "locations.no_match_section": "Nessun luogo corrispondente in questa sezione.",
    "locations.no_section": "Nessun luogo in questa sezione.",
    "locations.none": "Nessun dato sui luoghi di Hoenn.",
    "locations.section.settlements": "Città e paesi",
    "locations.section.routes": "Percorsi",
    "locations.section.landmarks": "Punti di interesse",
    "locations.section.settlements_desc": "Città e paesi, incluse aree con possibili incontri in acqua.",
    "locations.section.routes_desc": "Percorsi di Hoenn, incluse varianti terrestri e subacquee.",
    "locations.section.landmarks_desc": "Grotte, foreste, torri e altre aree non urbane.",

    "location_detail.back": "Torna ai Luoghi",
    "location_detail.loading": "Caricamento dettagli luogo...",
    "location_detail.region": "PokéMMO • Hoenn",
    "location_detail.encounter_entries": "{count} righe incontro",
    "location_detail.birdview": "Vista area",
    "location_detail.birdview_none": "Immagine vista area non disponibile.",
    "location_detail.birdview_source": "Fonte vista area",
    "location_detail.map": "Mappa",
    "location_detail.map_none": "Immagine mappa non disponibile.",
    "location_detail.map_source": "Fonte mappa",
    "location_detail.page": "Pagina PokéMMO",
    "location_detail.encounters": "Incontri",
    "location_detail.column.pokemon": "Pokémon",
    "location_detail.column.sub_area": "Sotto-area",
    "location_detail.column.levels": "Livelli",
    "location_detail.column.method": "Metodo",
    "location_detail.column.rate": "Frequenza",
    "location_detail.column.time": "Fascia oraria",
    "location_detail.any_period": "Qualsiasi",
    "location_detail.alt_birdview": "Vista area di {name}",
    "location_detail.alt_birdview_labeled": "{name} {label}",
    "location_detail.alt_map": "Mappa di {name}",

    "pokemon.loading": "Caricamento Pokémon...",
    "pokemon.not_found": "Pokémon non trovato.",
    "pokemon.abilities": "Abilità",
    "pokemon.no_abilities": "Nessuna abilità disponibile.",
    "pokemon.statistics": "Statistiche",
    "pokemon.damage_dealt": "Danno inflitto (STAB)",
    "pokemon.damage_taken": "Danno subito",
    "pokemon.moves_list": "Lista mosse",
    "pokemon.location": "Luoghi",
    "pokemon.loading_moves": "Caricamento mosse...",
    "pokemon.no_hoenn_locations": "Nessun luogo di incontro a Hoenn.",
    "pokemon.filters": "Filtri",
    "pokemon.clear": "Pulisci",
    "pokemon.filter.type": "Tipo",
    "pokemon.filter.category": "Categoria",
    "pokemon.filter.learn": "Apprendimento",
    "pokemon.stab_damage_to": "Le mosse STAB infliggono {multiplier} a",
    "pokemon.takes_from": "Subisce {multiplier} da",
    "pokemon.ev_yield": "EV",
    "pokemon.ev_none": "Nessuna",
    "pokemon.no_evolution_data": "Nessun dato evoluzione.",
    "pokemon.evolution_loading": "Caricamento...",
  },
};

const TYPE_LABELS: Record<AppLocale, Record<string, string>> = {
  en: {},
  it: {
    normal: "Normale",
    fighting: "Lotta",
    flying: "Volante",
    poison: "Veleno",
    ground: "Terra",
    rock: "Roccia",
    bug: "Coleottero",
    ghost: "Spettro",
    steel: "Acciaio",
    fire: "Fuoco",
    water: "Acqua",
    grass: "Erba",
    electric: "Elettro",
    psychic: "Psico",
    ice: "Ghiaccio",
    dragon: "Drago",
    dark: "Buio",
    fairy: "Folletto"
  }
};

const MOVE_CATEGORY_LABELS: Record<AppLocale, Record<string, string>> = {
  en: { physical: "Physical", special: "Special", status: "Status" },
  it: { physical: "Fisico", special: "Speciale", status: "Stato" }
};

const LEARN_METHOD_LABELS: Record<AppLocale, Record<string, string>> = {
  en: { "level-up": "Level-up", tm: "TM", tutor: "Tutor", egg: "Egg" },
  it: { "level-up": "Livello", tm: "MT", tutor: "Tutor", egg: "Uovo" }
};

const STAT_LABELS: Record<AppLocale, Record<string, string>> = {
  en: {
    hp: "HP",
    attack: "Atk",
    defense: "Def",
    "special-attack": "SpA",
    "special-defense": "SpD",
    speed: "Spe"
  },
  it: {
    hp: "PS",
    attack: "Att",
    defense: "Dif",
    "special-attack": "AttS",
    "special-defense": "DifS",
    speed: "Vel"
  }
};

function isSupportedLocale(value: string): value is AppLocale {
  return SUPPORTED_LOCALES.includes(value as AppLocale);
}

function detectBrowserLocale(): AppLocale {
  if (typeof navigator === "undefined") {
    return "en";
  }
  const candidates = [...(navigator.languages ?? []), navigator.language].filter(Boolean);
  for (const candidate of candidates) {
    const token = candidate.toLowerCase().split("-")[0];
    if (isSupportedLocale(token)) {
      return token;
    }
  }
  return "en";
}

function resolveInitialLocale(): AppLocale {
  if (typeof window === "undefined") {
    return "en";
  }
  const stored = window.localStorage.getItem(STORAGE_KEY)?.trim().toLowerCase();
  if (stored && isSupportedLocale(stored)) {
    return stored;
  }
  return detectBrowserLocale();
}

const currentLocale = ref<AppLocale>(resolveInitialLocale());

export function useLocale() {
  const locale = readonly(currentLocale);
  const isItalian = computed(() => currentLocale.value === "it");
  function setLocale(next: AppLocale) {
    if (!isSupportedLocale(next)) {
      return;
    }
    currentLocale.value = next;
    if (typeof window !== "undefined") {
      window.localStorage.setItem(STORAGE_KEY, next);
    }
  }
  return { locale, isItalian, setLocale };
}

export function getCurrentLocale(): AppLocale {
  return currentLocale.value;
}

export function t(key: string, values?: Record<string, string | number>): string {
  const localized = UI_MESSAGES[currentLocale.value][key] ?? UI_MESSAGES.en[key] ?? key;
  if (!values) {
    return localized;
  }
  return localized.replace(/\{(\w+)\}/g, (_match, name: string) => String(values[name] ?? ""));
}

export function labelType(type: string | null | undefined): string {
  if (!type) {
    return "-";
  }
  return TYPE_LABELS[currentLocale.value][type.toLowerCase()] ?? type;
}

export function labelMoveCategory(category: string | null | undefined): string {
  if (!category) {
    return "-";
  }
  return MOVE_CATEGORY_LABELS[currentLocale.value][category.toLowerCase()] ?? category;
}

export function labelLearnMethod(method: string): string {
  return LEARN_METHOD_LABELS[currentLocale.value][method] ?? method.replaceAll("-", " ");
}

export function labelStatShort(stat: string): string {
  return STAT_LABELS[currentLocale.value][stat] ?? stat;
}
