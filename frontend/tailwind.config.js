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
        // Primary: warm amber/gold (anowa-style)
        primary: {
          50:  '#fdf9ed',
          100: '#faf1d4',
          200: '#f5e0a4',
          300: '#eec96b',
          400: '#e7b23e',
          500: '#d99925',
          600: '#bc781c',
          700: '#97581b',
          800: '#7c451e',
          900: '#67391d',
          950: '#3b1d0c',
        },
        // Cream/beige background tones - subtle warm neutrals
        cream: {
          50:  '#fafaf9',
          100: '#f5f5f4',
          200: '#e7e5e4',
          300: '#d6d3d1',
          400: '#a8a29e',
        },
        // Dark brown (header/sidebar)
        journal: {
          50:  '#f7f4ef',
          100: '#ebe4d6',
          200: '#d6c7ac',
          300: '#b9a078',
          400: '#997e50',
          500: '#7d6640',
          600: '#5e4a2d',
          700: '#443421',
          800: '#2f2417',
          900: '#1d160e',
          950: '#0f0b07',
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
