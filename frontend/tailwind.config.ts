import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{js,ts,jsx,tsx}", "./components/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#0B0E14",       // primary background — deep document-navy, not pure black
        "ink-raised": "#12161F",
        paper: "#F6F4EE",     // light sections / cards, evokes official paper stock
        brass: "#C9A24B",     // seal / stamp accent — signals legitimacy & official docs
        "brass-dim": "#8A6F35",
        steel: "#4E6E7A",     // secondary accent — long-haul route lines, links
        mist: "#9AA3B2",      // secondary text on ink
        line: "#232838",      // hairline borders on ink
      },
      fontFamily: {
        display: ["var(--font-display)", "sans-serif"],
        body: ["var(--font-body)", "sans-serif"],
        mono: ["var(--font-mono)", "monospace"],
      },
    },
  },
  plugins: [],
};
export default config;
