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
    'icon',
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        mono: ['ui-monospace', 'SFMono-Regular', 'Menlo', 'monospace'],
      },
      colors: {
        brand: {
          DEFAULT: "#3b82f6",
          50:  "#eff6ff",
          100: "#dbeafe",
          200: "#bfdbfe",
          300: "#93c5fd",
          400: "#60a5fa",
          500: "#3b82f6",
          600: "#2563eb",
          700: "#1d4ed8",
        },
        ink: {
          950: "#06070d",
          900: "#0a0a14",
          800: "#0e0f1a",
          700: "#13141f",
          600: "#1a1c29",
          500: "#262838",
        },
        softWhite: "#f7f9fc",
        softBlue: "#cfe8ff",
      },
      backgroundImage: {
        'grid-dots': "radial-gradient(rgba(255,255,255,0.06) 1px, transparent 1px)",
        'grid-dots-light': "radial-gradient(rgba(0,0,0,0.08) 1px, transparent 1px)",
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'hero-glow': 'radial-gradient(ellipse 80% 50% at 50% -20%, rgba(59,130,246,0.25), transparent 70%)',
      },
      backgroundSize: {
        'grid-22': '22px 22px',
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
        'glow-pulse': {
          '0%, 100%': { opacity: '0.45' },
          '50%': { opacity: '0.8' },
        },
        'float-slow': {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-12px)' },
        },
      },
      animation: {
        'slide-in': 'slide-in 0.3s ease-out',
        'fade-in': 'fade-in 0.3s ease-in',
        'slide-in-right': 'slide-in-right 0.4s ease-out',
        'toast-progress': 'toast-progress 4s linear forwards',
        'glow-pulse': 'glow-pulse 6s ease-in-out infinite',
        'float-slow': 'float-slow 8s ease-in-out infinite',
      },
      width: { icon: "56px" },
      height: { icon: "56px" },
      maxWidth: { '7xl': '80rem' },
    },
  },
  plugins: [],
};
