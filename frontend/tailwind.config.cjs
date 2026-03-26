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
        text: "var(--color-text)",
        muted: "var(--color-muted)"
      },
      boxShadow: {
        soft: "0 20px 50px -30px rgba(18, 18, 18, 0.45)"
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
