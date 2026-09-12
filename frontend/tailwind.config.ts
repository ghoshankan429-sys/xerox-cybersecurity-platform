import type { Config } from "tailwindcss";

export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        xerox: {
          bg: "#0a0b0e",
          surface: "#12141a",
          card: "#171a21",
          elevated: "#1f232d",
          border: "#262b37",
          "border-subtle": "#1e222d",
          gunmetal: "#2a303f",
          silver: "#94a3b8",
          titanium: "#cbd5e1",
          red: {
            DEFAULT: "#ef4444",
            bright: "#ff2d20",
            glow: "#ff3e30",
            dark: "#7f1d1d",
            muted: "#991b1b",
          },
          safe: "#10b981",
          warning: "#f59e0b",
        },
      },
      fontFamily: {
        sans: ["Plus Jakarta Sans", "Inter", "sans-serif"],
        mono: ["JetBrains Mono", "monospace"],
      },
      boxShadow: {
        "red-glow": "0 0 25px -5px rgba(255, 45, 32, 0.35)",
        "red-glow-sm": "0 0 15px -3px rgba(255, 45, 32, 0.25)",
        "red-glow-lg": "0 0 40px -2px rgba(255, 45, 32, 0.45)",
      },
    },
  },
  plugins: [],
} satisfies Config;
