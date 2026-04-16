import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/status': 'http://localhost:8000',
      '/stats': 'http://localhost:8000',
      '/chat': 'http://localhost:8000',
      '/ws': { target: 'ws://localhost:8000', ws: true },
      '/history': 'http://localhost:8000',
      '/tools': 'http://localhost:8000',
      '/context': 'http://localhost:8000',
      '/voice': 'http://localhost:8000',
      '/schedule': 'http://localhost:8000',
      '/schedules': 'http://localhost:8000',
      '/news': 'http://localhost:8000',
      '/notifications': 'http://localhost:8000',
      '/mcp': 'http://localhost:8000',
    }
  },
  build: { outDir: 'dist' }
})
