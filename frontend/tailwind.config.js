// frontend/tailwind.config.ts
import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#1E3A8A',  // Dark blue for finance vibe
        secondary: '#3B82F6',  // Lighter blue accents
        background: '#F9FAFB',  // Soft gray bg
        text: '#1F2937',  // Dark text
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],  // Modern font; add via CDN in layout.tsx
      },
    },
  },
  plugins: [],
};
export default config;