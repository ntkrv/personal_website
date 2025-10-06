/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: [
    "./templates/**/*.html",
    "./static/**/*.js",
    "./static/icons/**/*.{svg,png,jpg}",
    "./**/*.py",
  ],
  safelist: [
    'icon', // Ensure the icon class is always included
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
      colors: {
        brand: "#326aa3",
        darkBg: "#212121",
        softWhite: "#f7f9fc",
        softBlue: "#cfe8ff",
        gray: {
          50: "#f9fafb",
          100: "#f3f4f6",
          200: "#e5e7eb",
          500: "#6b7280",
          800: "#1f2937"
        }
      },
      keyframes: {
        'slide-in': {
          '0%': { opacity: '0', transform: 'translateX(-100%)' },
          '100%': { opacity: '1', transform: 'translateX(0)' },
        },
        'fade-in': {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        'slide-in-right': {
          '0%': { transform: 'translateX(-20%)', opacity: '0' },
          '100%': { transform: 'translateX(0)', opacity: '1' },
        },
        'toast-progress': {
          '0%': { width: '100%' },
          '100%': { width: '0%' },
        },
      },
      animation: {
        'slide-in': 'slide-in 0.3s ease-out',
        'fade-in': 'fade-in 0.3s ease-in',
        'slide-in-right': 'slide-in-right 0.4s ease-out',
        'toast-progress': 'toast-progress 4s linear forwards',
      },
      width: {
        icon: "64px",
      },
      height: {
        icon: "64px",
      },
    },
  },
  plugins: [],
};
