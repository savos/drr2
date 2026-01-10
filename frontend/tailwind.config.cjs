/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#667eea',
          dark: '#764ba2',
        },
        danger: {
          DEFAULT: '#c53030',
          dark: '#9b2c2c',
        },
      },
    },
  },
  plugins: [],
}
