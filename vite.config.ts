import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  optimizeDeps: {
    exclude: ['lucide-react'],
  },
  server: {
    host: '0.0.0.0',     // ⬅️ allows external access via ngrok
    port: 5173,
    strictPort: true     // ⬅️ ensures it doesn’t switch to another port
  }
});
