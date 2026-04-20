/** @type {import('tailwindcss').Config} */
const cv = (name) => `rgb(var(${name}) / <alpha-value>)`
const palette = (prefix) => ({
  50:  cv(`${prefix}-50`),
  100: cv(`${prefix}-100`),
  200: cv(`${prefix}-200`),
  300: cv(`${prefix}-300`),
  400: cv(`${prefix}-400`),
  500: cv(`${prefix}-500`),
  600: cv(`${prefix}-600`),
  700: cv(`${prefix}-700`),
  800: cv(`${prefix}-800`),
  900: cv(`${prefix}-900`),
  950: cv(`${prefix}-950`),
})

export default {
  darkMode: 'class',
  content: [
    './index.html',
    './src/**/*.{vue,js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: palette('--color-primary'),
        journal: palette('--color-journal'),
        // Subtle warm neutrals (kept for content cards)
        cream: {
          50:  '#fafaf9',
          100: '#f5f5f4',
          200: '#e7e5e4',
          300: '#d6d3d1',
          400: '#a8a29e',
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
