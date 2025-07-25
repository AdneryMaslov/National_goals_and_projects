import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      // Все запросы, начинающиеся с '/api', будут перенаправлены
      '/api': {
        target: 'http://localhost:8000', // Адрес вашего бэкенд-сервера
        changeOrigin: true, // Необходимо для корректной работы прокси
      }
    }
  }
})