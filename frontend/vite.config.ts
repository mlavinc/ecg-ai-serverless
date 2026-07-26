import path from 'node:path'
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    proxy: {
      // Lets `npm run dev` talk to a locally-invoked Lambda (e.g. via SAM/RIE)
      // without hardcoding a backend origin. In production, CloudFront is
      // the one routing /api/* to the Lambda Function URL.
      '/api': {
        target: process.env.VITE_DEV_API_PROXY_TARGET || 'http://localhost:9000',
        changeOrigin: true,
        rewrite: (p) => p.replace(/^\/api/, ''),
      },
    },
  },
})
