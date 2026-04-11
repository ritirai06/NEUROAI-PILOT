/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        jarvis: {
          bg:      '#020812',
          panel:   '#040d1a',
          border:  '#0a2040',
          cyan:    '#00d4ff',
          blue:    '#0066ff',
          glow:    '#00aaff',
          dim:     '#003366',
          success: '#00ff88',
          error:   '#ff3366',
          warn:    '#ffaa00',
          text:    '#a0c8e8',
          muted:   '#3a5a7a',
        }
      },
      fontFamily: {
        sans:  ['Inter', 'sans-serif'],
        mono:  ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
      animation: {
        'pulse-cyan':  'pulse-cyan 2s ease-in-out infinite',
        'scan':        'scan 3s linear infinite',
        'flicker':     'flicker 4s ease-in-out infinite',
        'orbit':       'orbit 8s linear infinite',
        'glow-pulse':  'glow-pulse 2s ease-in-out infinite',
      },
      keyframes: {
        'pulse-cyan': {
          '0%,100%': { opacity: '1' },
          '50%':     { opacity: '0.4' },
        },
        'scan': {
          '0%':   { transform: 'translateY(-100%)' },
          '100%': { transform: 'translateY(100vh)' },
        },
        'flicker': {
          '0%,100%': { opacity: '1' },
          '92%':     { opacity: '1' },
          '93%':     { opacity: '0.6' },
          '94%':     { opacity: '1' },
          '96%':     { opacity: '0.8' },
          '97%':     { opacity: '1' },
        },
        'orbit': {
          '0%':   { transform: 'rotate(0deg) translateX(60px) rotate(0deg)' },
          '100%': { transform: 'rotate(360deg) translateX(60px) rotate(-360deg)' },
        },
        'glow-pulse': {
          '0%,100%': { boxShadow: '0 0 8px #00d4ff44, 0 0 20px #00d4ff22' },
          '50%':     { boxShadow: '0 0 16px #00d4ff88, 0 0 40px #00d4ff44' },
        },
      },
      boxShadow: {
        'cyan-sm':  '0 0 8px #00d4ff44',
        'cyan-md':  '0 0 16px #00d4ff66',
        'cyan-lg':  '0 0 32px #00d4ff44, 0 0 64px #00d4ff22',
        'blue-sm':  '0 0 8px #0066ff44',
        'panel':    '0 0 0 1px #0a2040, 0 4px 24px #00000088',
      },
    }
  },
  plugins: []
}
