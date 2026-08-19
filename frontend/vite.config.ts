import { defineConfig } from 'vite';
import path from 'path';

export default defineConfig({
  root: 'src',
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '/api'),
      },
    },
  },
  build: {
    outDir: '../dist',
    emptyOutDir: true,
  },
  resolve: {
    alias: {
      '@app': path.resolve(__dirname, 'src/app'),
    },
  },
});
