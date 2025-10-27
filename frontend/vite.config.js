import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  base: '/',  // Will be deployed at app.chitty.cc/trace via Cloudflare routing
  server: {
    host: true,
    port: 5173,
    strictPort: false,
    allowedHosts: ['*']
  },
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    emptyOutDir: true,
    sourcemap: false,
    rollupOptions: {
      output: {
        manualChunks: {
          'vendor': ['react', 'react-dom'],
          'chitty-services': ['./src/lib/chittyservices.js'],
          'ui': ['lucide-react', 'clsx']
        }
      }
    }
  }
})
