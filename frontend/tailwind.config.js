/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: [
    './index.html',
    './src/**/*.{vue,js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        // Primary: deep blue (uobs.uz inspired)
        primary: {
          50:  '#eef4ff',
          100: '#dae6ff',
          200: '#bdd2ff',
          300: '#90b3ff',
          400: '#6189ff',
          500: '#3d63f7',
          600: '#2742ec',
          700: '#1f31d4',
          800: '#1f2cab',
          900: '#1e2c87',
          950: '#161b50',
        },
        // Subtle warm neutrals (kept for content cards)
        cream: {
          50:  '#fafaf9',
          100: '#f5f5f4',
          200: '#e7e5e4',
          300: '#d6d3d1',
          400: '#a8a29e',
        },
        // Deep navy blue (header/sidebar — was brown)
        journal: {
          50:  '#eef2ff',
          100: '#e0e7ff',
          200: '#c7d2fe',
          300: '#a5b4fc',
          400: '#818cf8',
          500: '#3b4ec5',
          600: '#2a3ba8',
          700: '#1f2c7d',
          800: '#162055',
          900: '#0e1638',
          950: '#070b1f',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        serif: ['Lora', 'Georgia', 'serif'],
      },
      typography: {
        DEFAULT: {
          css: {
            maxWidth: 'none',
          },
        },
      },
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
  ],
}
