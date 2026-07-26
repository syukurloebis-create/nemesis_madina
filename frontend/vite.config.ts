import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';
import { visualizer } from 'rollup-plugin-visualizer';

export default defineConfig({
  plugins: [
    react(),
    // Bundle analyzer (opsional, hanya untuk development)
    visualizer({
      filename: 'dist/stats.html',
      open: false,
      gzipSize: true,
    }),
  ],
  
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  
  server: {
    port: 5173,
    open: true,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
      },
    },
  },
  
  build: {
    // Minifikasi
    minify: 'terser',
    // Source maps untuk debugging
    sourcemap: true,
    // Target browser
    target: 'es2020',
    // Chunk size warning limit
    chunkSizeWarningLimit: 1000,
    
    rollupOptions: {
      output: {
        // Manual chunk splitting untuk optimal caching
        manualChunks: {
          // React vendor
          'react-vendor': ['react', 'react-dom', 'react-router-dom'],
          // UI vendor
          'ui-vendor': [
            '@headlessui/react',
            'lucide-react',
            'react-toastify',
          ],
          // Data vendor
          'data-vendor': ['axios', '@tanstack/react-query'],
          // Chart vendor
          'chart-vendor': ['chart.js', 'react-chartjs-2'],
          // Utils
          'utils-vendor': ['date-fns', 'clsx', 'tailwind-merge'],
        },
      },
    },
    
    // Terser options
    terserOptions: {
      compress: {
        drop_console: true, // Hapus console.log di production
        drop_debugger: true,
      },
    },
  },
  
  // Optimization
  optimizeDeps: {
    include: [
      'react',
      'react-dom',
      'react-router-dom',
      'axios',
      '@headlessui/react',
      'lucide-react',
    ],
  },
});
