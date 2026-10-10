import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    // Bind to 127.0.0.1 explicitly; on macOS "localhost" can resolve to IPv6 only.
    host: '127.0.0.1',
    port: 5173,
    strictPort: true,
    // Forward API calls and product photos to the FastAPI backend.
    proxy: {
      '/api': 'http://127.0.0.1:8000',
      '/images': 'http://127.0.0.1:8000',
    },
  },
})
