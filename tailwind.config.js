/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class', // enables dark mode via 'dark' class on <html>
  content: [
    "./templates/**/*.html",  // Jinja2 template files
    "./static/**/*.js",       // JavaScript files
    "./**/*.py",              // Python files (if using Tailwind classes in strings)
  ],
  theme: {
    extend: {
      colors: {
        brand: "#326aa3", // custom brand color
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
      },
      animation: {
        'slide-in': 'slide-in 0.3s ease-out',
        'fade-in': 'fade-in 0.3s ease-in',
      },
    },
  },
  plugins: [],
};
