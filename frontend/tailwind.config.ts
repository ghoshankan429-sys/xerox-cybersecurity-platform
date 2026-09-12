import type { Config } from "tailwindcss";

export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        xerox: {
          // Figma Cloud Variables
          void: "#0a0b0e",
          gunmetal: "#1e222d",
          "xerox-red": "#ef4444",

          bg: "#0a0b0e",
          "bg-secondary": "#0d0f14",
          "bg-elevated": "#1a1e29",
          surface: "#12141a",
          "surface-card": "#161922",
          "surface-elevated": "#1a1e29",
          "surface-subtle": "#0e1017",
          border: "#222733",
          "border-subtle": "#1a1e28",
          "border-highlight": "#2e3545",
          "border-focus": "#ef4444",
          card: "#161922",
          elevated: "#1a1e29",
          silver: "#94a3b8",
          titanium: "#cbd5e1",
          red: {
            DEFAULT: "#ef4444",
            bright: "#ff2d20",
            glow: "#ff3e30",
            dark: "#7f1d1d",
            muted: "#991b1b",
            subtle: "rgba(239, 68, 68, 0.12)",
          },
          safe: {
            DEFAULT: "#10b981",
            bright: "#34d399",
            subtle: "rgba(16, 185, 129, 0.12)",
            border: "rgba(16, 185, 129, 0.25)",
          },
          warning: {
            DEFAULT: "#f59e0b",
            bright: "#fbbf24",
            subtle: "rgba(245, 158, 11, 0.12)",
            border: "rgba(245, 158, 11, 0.25)",
          },
          info: {
            DEFAULT: "#3b82f6",
            bright: "#60a5fa",
            subtle: "rgba(59, 130, 246, 0.12)",
            border: "rgba(59, 130, 246, 0.25)",
          },
        },
      },
      fontFamily: {
        sans: ["Plus Jakarta Sans", "Inter", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "Fira Code", "monospace"],
      },
      boxShadow: {
        "red-glow": "0 0 25px -5px rgba(255, 45, 32, 0.35)",
        "red-glow-sm": "0 0 15px -3px rgba(255, 45, 32, 0.25)",
        "red-glow-lg": "0 0 40px -2px rgba(255, 45, 32, 0.45)",
        panel: "0 4px 20px -2px rgba(0, 0, 0, 0.5)",
      },
    },
  },
  plugins: [],
} satisfies Config;
