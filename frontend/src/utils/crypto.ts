export type AIProvider = "openai" | "deepseek";

const LS_KEYS: Record<AIProvider, string> = {
  openai:   "sursk.it:openai-key",
  deepseek: "sursk.it:deepseek-key",
};
const APP_SECRET = "sursk-it-pokemmo-companion-v1";
const PBKDF2_SALT = "sursk-it-storage-salt-2024";
const PBKDF2_ITERATIONS = 10_000;

async function deriveKey(): Promise<CryptoKey> {
  const keyMaterial = await crypto.subtle.importKey(
    "raw",
    new TextEncoder().encode(APP_SECRET),
    { name: "PBKDF2" },
    false,
    ["deriveKey"],
  );
  return crypto.subtle.deriveKey(
    {
      name: "PBKDF2",
      salt: new TextEncoder().encode(PBKDF2_SALT),
      iterations: PBKDF2_ITERATIONS,
      hash: "SHA-256",
    },
    keyMaterial,
    { name: "AES-GCM", length: 256 },
    false,
    ["encrypt", "decrypt"],
  );
}

export async function saveApiKey(apiKey: string, provider: AIProvider = "openai"): Promise<void> {
  const key = await deriveKey();
  const iv = crypto.getRandomValues(new Uint8Array(12));
  const ciphertext = await crypto.subtle.encrypt(
    { name: "AES-GCM", iv },
    key,
    new TextEncoder().encode(apiKey),
  );
  const buf = new Uint8Array(iv.byteLength + ciphertext.byteLength);
  buf.set(iv, 0);
  buf.set(new Uint8Array(ciphertext), iv.byteLength);
  localStorage.setItem(LS_KEYS[provider], btoa(String.fromCharCode(...buf)));
}

export async function loadApiKey(provider: AIProvider = "openai"): Promise<string | null> {
  const stored = localStorage.getItem(LS_KEYS[provider]);
  if (!stored) return null;
  try {
    const key = await deriveKey();
    const buf = Uint8Array.from(atob(stored), c => c.charCodeAt(0));
    const iv = buf.slice(0, 12);
    const ciphertext = buf.slice(12);
    const plaintext = await crypto.subtle.decrypt({ name: "AES-GCM", iv }, key, ciphertext);
    return new TextDecoder().decode(plaintext);
  } catch {
    return null;
  }
}

export function clearApiKey(provider: AIProvider = "openai"): void {
  localStorage.removeItem(LS_KEYS[provider]);
}

export function hasApiKey(provider: AIProvider = "openai"): boolean {
  return localStorage.getItem(LS_KEYS[provider]) !== null;
}
