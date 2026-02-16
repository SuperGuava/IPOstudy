import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: ["class"],
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        ag: {
          bg: "#0f172a",
          card: "#111827",
          panel: "#0b1220",
          accent: "#22d3ee",
          ok: "#10b981",
          warn: "#f59e0b",
          fail: "#ef4444",
          line: "#1f2937",
          text: "#e5e7eb",
          mute: "#94a3b8",
        },
      },
      boxShadow: {
        panel: "0 10px 40px rgba(0,0,0,0.35)",
      },
      animation: {
        "fade-up": "fadeUp 280ms ease-out both",
      },
      keyframes: {
        fadeUp: {
          from: { opacity: "0", transform: "translateY(8px)" },
          to: { opacity: "1", transform: "translateY(0)" },
        },
      },
    },
  },
  plugins: [],
};

export default config;
