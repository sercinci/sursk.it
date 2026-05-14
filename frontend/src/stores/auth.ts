import { defineStore } from "pinia";
import { computed, ref } from "vue";
import type { XcoreUser } from "@/types";
import { fetchCurrentUser, logoutUser } from "@/api/client";

export const useAuthStore = defineStore("auth", () => {
  const user = ref<XcoreUser | null>(null);
  const isLoading = ref(true);
  const isAuthenticated = computed(() => user.value !== null);

  async function init() {
    isLoading.value = true;
    try {
      const envelope = await fetchCurrentUser();
      user.value = envelope.data;
    } catch {
      user.value = null;
    } finally {
      isLoading.value = false;
    }
  }

  function login() {
    window.location.href = "/api/auth/login";
  }

  async function logout() {
    try {
      await logoutUser();
    } catch {
      // ignore — session cleared server-side best-effort
    }
    user.value = null;
  }

  return { user, isLoading, isAuthenticated, init, login, logout };
});
