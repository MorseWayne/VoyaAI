/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './index.html',
    './src/**/*.{vue,js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['"Outfit"', '"Noto Sans SC"', 'sans-serif'],
        mono: ['"Fira Code"', 'monospace'],
      },
      colors: {
        primary: '#06B6D4',
        primaryHover: '#22D3EE',
        accent: '#10B981',
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
  ],
}
