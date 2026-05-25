import { createApp } from "vue";
import { QueryClient, VueQueryPlugin } from "@tanstack/vue-query";
import { createPinia } from "pinia";

import App from "./App.vue";
import router from "./router";
import "./style.css";
import { useAuthStore } from "@/stores/auth";

const app = createApp(App);
const queryClient = new QueryClient();

app.use(createPinia());
app.use(router);
app.use(VueQueryPlugin, { queryClient });
app.mount("#app");

useAuthStore().init();
