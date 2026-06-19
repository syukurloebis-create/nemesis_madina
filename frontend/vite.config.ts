import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost',
        changeOrigin: true,
      },
      '/auth': {
        target: 'http://localhost',
        changeOrigin: true,
      },
      '/cases': {
        target: 'http://localhost',
        changeOrigin: true,
      },
      '/evidence': {
        target: 'http://localhost',
        changeOrigin: true,
      },
      '/findings': {
        target: 'http://localhost',
        changeOrigin: true,
      },
      '/graph': {
        target: 'http://localhost',
        changeOrigin: true,
      },
      '/integrity': {
        target: 'http://localhost',
        changeOrigin: true,
      },
      '/replay': {
        target: 'http://localhost',
        changeOrigin: true,
      },
      '/rebuild': {
        target: 'http://localhost',
        changeOrigin: true,
      },
      '/temporal': {
        target: 'http://localhost',
        changeOrigin: true,
      },
      '/alerts': {
        target: 'http://localhost',
        changeOrigin: true,
      },
      '/ws': {
        target: 'ws://localhost',
        ws: true,
        changeOrigin: true,
      },
    },
  },
});

// Code splitting
build: {
  rollupOptions: {
    output: {
      manualChunks: {
        'react-vendor': ['react', 'react-dom'],
        'chart-vendor': ['chart.js', 'react-chartjs-2'],
        'graph-vendor': ['reactflow', '@xyflow/react'],
      }
    }
  }
}

// Code Splitting Configuration
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': { target: 'http://localhost', changeOrigin: true },
      '/auth': { target: 'http://localhost', changeOrigin: true },
      '/cases': { target: 'http://localhost', changeOrigin: true },
    },
  },
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          'react-vendor': ['react', 'react-dom'],
          'ui-vendor': ['lucide-react', 'react-toastify'],
          'graph-vendor': ['reactflow', '@xyflow/react'],
          'chart-vendor': ['chart.js', 'react-chartjs-2'],
          'date-vendor': ['date-fns'],
        },
      },
    },
    chunkSizeWarningLimit: 500,
  },
  resolve: {
    extensions: ['.js', '.jsx', '.ts', '.tsx', '.json'],
  },
});

// Add history fallback for SPA
server: {
  historyApiFallback: true,
},
