/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['"Space Grotesk"', 'Inter', 'ui-sans-serif', 'system-ui', 'Segoe UI', 'Roboto', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'ui-monospace', 'SFMono-Regular', 'Menlo', 'Monaco', 'Consolas', 'monospace'],
      },
      colors: {
        nexus: {
          bg0: '#0B0F1A',
          bg1: '#121826',
          bg2: '#1A2238',
          neon: '#4FD1FF',
          cyan: '#00E5FF',
          violet: '#8B5CF6',
        },
        portal: {
          bg: '#06060c',
          bg2: '#0c0c18',
          fg: '#e8e8f0',
          muted: '#5a5a7a',
          accent: '#00ff88',
          accent2: '#ffaa00',
          danger: '#ff3355',
        },
      },
      boxShadow: {
        glow: '0 0 0 1px rgba(79, 209, 255, 0.25), 0 12px 32px rgba(0, 0, 0, 0.35)',
        lift: '0 24px 60px rgba(0, 0, 0, 0.55)',
      },
      keyframes: {
        floaty: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-10px)' },
        },
        shimmer: {
          '0%': { transform: 'translateX(-120%)' },
          '100%': { transform: 'translateX(220%)' },
        },
      },
      animation: {
        floaty: 'floaty 6s ease-in-out infinite',
        shimmer: 'shimmer 2.2s ease-in-out infinite',
      },
    },
  },
  plugins: [],
}

