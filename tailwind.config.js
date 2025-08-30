/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        'music': {
          'vocals': '#FF6B6B',
          'drums': '#4ECDC4', 
          'bass': '#45B7D1',
          'other': '#96CEB4',
          'bg': '#1a1a1a',
          'surface': '#2d2d2d',
          'text': '#ffffff',
          'text-muted': '#a0a0a0'
        }
      },
      fontFamily: {
        'mono': ['Monaco', 'Menlo', 'Ubuntu Mono', 'monospace'],
      }
    },
  },
  plugins: [],
}
