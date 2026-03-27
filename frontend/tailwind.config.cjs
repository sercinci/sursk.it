/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./index.html", "./src/**/*.{vue,ts}"],
  theme: {
    extend: {
      colors: {
        shell: "var(--color-shell)",
        panel: "var(--color-panel)",
        accent: "var(--color-accent)",
        ember: "var(--color-ember)",
        mint: "var(--color-mint)",
        sun: "var(--color-sun)",
        text: "var(--color-text)",
        muted: "var(--color-muted)"
      },
      boxShadow: {
        soft: "0 24px 60px -34px rgba(10, 64, 86, 0.34)"
      },
      fontFamily: {
        display: ["Space Grotesk", "sans-serif"],
        body: ["Manrope", "sans-serif"],
        mono: ["IBM Plex Mono", "monospace"]
      }
    }
  },
  plugins: []
};
