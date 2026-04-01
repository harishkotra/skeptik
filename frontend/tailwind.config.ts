import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}"
  ],
  theme: {
    extend: {
      colors: {
        ink: "#0f1720",
        paper: "#f6f1e8",
        accent: "#a54c2a",
        steel: "#5d6b74",
        sage: "#d7ddd2"
      },
      fontFamily: {
        display: ["Georgia", "Times New Roman", "serif"],
        sans: ["ui-sans-serif", "system-ui", "sans-serif"]
      },
      boxShadow: {
        editorial: "0 20px 60px rgba(15, 23, 32, 0.08)"
      }
    }
  },
  plugins: []
};

export default config;
