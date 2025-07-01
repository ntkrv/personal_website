/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class', // enable dark mode via 'dark' class
  content: [
    "./templates/**/*.html",  // Jinja2 templates
    "./static/**/*.js",       // JavaScript files
    "./**/*.py",              // Python files with Tailwind classes
  ],
  theme: {
    extend: {
      colors: {
        brand: "#326aa3",       // custom brand color
        darkBg: "#212121",      // material black
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
          '0%': { opacity: '0', transform: 'translateX(100%)' },
          '100%': { opacity: '1', transform: 'translateX(0)' },
        },
        'toast-progress': {
          '0%': { width: '100%' },
          '100%': { width: '0%' },
        },
      },
      animation: {
        'slide-in': 'slide-in 0.3s ease-out',
        'fade-in': 'fade-in 0.3s ease-in',
        'slide-in-right': 'slide-in-right 0.4s ease-out forwards',
        'toast-progress': 'toast-progress 4s linear forwards',
      },
    },
  },
  plugins: [],
};
