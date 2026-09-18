// frontend/src/main.tsx
import React from 'react';
import ReactDOM from 'react-dom/client';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import App from './App.tsx';
import './index.css';

// ─── React Query ─────────────────────────────────────────────────────
// Global query client for data fetching.
//
// Policy:
//   - staleTime: 60s — data dianggap fresh selama 1 menit
//   - retry: 1 — retry sekali pada error jaringan
//   - refetchOnWindowFocus: false — hindari refetch saat tab switch
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 60_000,
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

ReactDOM.createRoot(
  document.getElementById('root')!
).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <App />
    </QueryClientProvider>
  </React.StrictMode>
);