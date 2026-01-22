import path from 'path';
import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig(({ mode }) => {
    // Load .env from root directory (two levels up)
    const env = loadEnv(mode, path.resolve(__dirname, '../..'), '');
    return {
      server: {
        port: Number(env.FRONTEND_PORT) || 3000,
        host: '0.0.0.0',
      },
      plugins: [react()],
      define: {
        'process.env.GEMINI_API_KEY': JSON.stringify(env.GEMINI_API_KEY),
        'process.env.API_BASE_URL': JSON.stringify(`http://localhost:${env.BACKEND_PORT || '6000'}`),
      },
      resolve: {
        alias: {
          '@': path.resolve(__dirname, '.'),
        }
      }
    };
});
