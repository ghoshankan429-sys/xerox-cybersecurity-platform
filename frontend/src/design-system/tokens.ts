/**
 * XEROX Cyber-Guardian Design System Tokens
 * Source of truth for styling constants, themes, and design primitives.
 * Directly translates XEROX Figma Cloud variables and design specifications.
 */

export const tokens = {
  // Direct mapping to Figma Cloud Variables
  figma: {
    "color/void": "#0a0b0e",
    "color/gunmetal": "#1e222d",
    "color/xerox-red": "#ef4444",
    "color/safe": "#10b981",
    "color/warning": "#f59e0b",
    "color/info": "#3b82f6",
    "text/primary": "#f8fafc",
    "text/muted": "#64748b",
  },

  colors: {
    // Base backgrounds
    bg: "#0a0b0e",
    void: "#0a0b0e",
    bgSecondary: "#0d0f14",
    bgElevated: "#1a1e29",

    // Surfaces
    surface: "#12141a",
    surfaceCard: "#161922",
    surfaceElevated: "#1a1e29",
    surfaceSubtle: "#0e1017",

    // Borders
    border: "#222733",
    borderSubtle: "#1a1e28",
    borderHighlight: "#2e3545",
    borderFocus: "#ef4444",

    // Typography
    textPrimary: "#f8fafc",
    textSecondary: "#94a3b8",
    textMuted: "#64748b",
    textDisabled: "#475569",

    // XEROX Brand Red & Risk Colors
    red: {
      DEFAULT: "#ef4444",
      bright: "#ff2d20",
      glow: "#ff3e30",
      dark: "#7f1d1d",
      muted: "#991b1b",
      subtle: "rgba(239, 68, 68, 0.12)",
      hover: "#dc2626",
    },

    // Status / Alert Levels
    safe: {
      DEFAULT: "#10b981",
      bright: "#34d399",
      subtle: "rgba(16, 185, 129, 0.12)",
      border: "rgba(16, 185, 129, 0.25)",
      text: "#34d399",
    },
    warning: {
      DEFAULT: "#f59e0b",
      bright: "#fbbf24",
      subtle: "rgba(245, 158, 11, 0.12)",
      border: "rgba(245, 158, 11, 0.25)",
      text: "#fbbf24",
    },
    info: {
      DEFAULT: "#3b82f6",
      bright: "#60a5fa",
      subtle: "rgba(59, 130, 246, 0.12)",
      border: "rgba(59, 130, 246, 0.25)",
      text: "#60a5fa",
    },

    // Material accouterments
    silver: "#94a3b8",
    titanium: "#cbd5e1",
    gunmetal: "#1e222d",
  },

  typography: {
    fonts: {
      sans: "'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
      mono: "'JetBrains Mono', 'Fira Code', monospace",
    },
    sizes: {
      display: {
        fontSize: "2rem", // 32px
        lineHeight: "2.5rem",
        fontWeight: "800",
        letterSpacing: "-0.025em",
      },
      h1: {
        fontSize: "1.5rem", // 24px
        lineHeight: "2rem",
        fontWeight: "700",
        letterSpacing: "-0.02em",
      },
      h2: {
        fontSize: "1.25rem", // 20px
        lineHeight: "1.75rem",
        fontWeight: "700",
        letterSpacing: "-0.01em",
      },
      h3: {
        fontSize: "1rem", // 16px
        lineHeight: "1.5rem",
        fontWeight: "600",
        letterSpacing: "0",
      },
      body: {
        fontSize: "0.875rem", // 14px
        lineHeight: "1.375rem",
        fontWeight: "400",
      },
      small: {
        fontSize: "0.75rem", // 12px
        lineHeight: "1rem",
        fontWeight: "400",
      },
      metadata: {
        fontSize: "0.6875rem", // 11px
        lineHeight: "0.875rem",
        fontWeight: "600",
        letterSpacing: "0.05em",
        textTransform: "uppercase" as const,
      },
    },
  },

  radius: {
    sm: "0.25rem", // 4px
    md: "0.5rem", // 8px
    lg: "0.75rem", // 12px
    xl: "1rem", // 16px
    "2xl": "1.25rem", // 20px
    full: "9999px",
  },

  shadows: {
    redGlow: "0 0 25px -5px rgba(255, 45, 32, 0.35)",
    redGlowSm: "0 0 15px -3px rgba(255, 45, 32, 0.25)",
    redGlowLg: "0 0 40px -2px rgba(255, 45, 32, 0.45)",
    panel: "0 4px 20px -2px rgba(0, 0, 0, 0.5)",
    cardHover: "0 8px 30px -4px rgba(0, 0, 0, 0.7)",
  },
} as const;

export type DesignTokens = typeof tokens;
