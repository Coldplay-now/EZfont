/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'primary': '#1a1a1a',
        'background-light': '#f8f8f8',
      },
      fontFamily: {
        'display': ['Inter', 'sans-serif'],
      },
      borderRadius: {
        'DEFAULT': '0.5rem',
        'lg': '1rem',
        'xl': '1.5rem',
        'full': '9999px',
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
  ],
}

