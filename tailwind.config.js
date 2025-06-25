/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",     // Flask templates
    "./static/**/*.js",          // Optional: JS files with classes
    "./static/src/**/*.css"      // Optional: custom Tailwind content
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
