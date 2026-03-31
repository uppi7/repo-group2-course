import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  base: '/course/',  // 大盘 Nginx 挂载子路径，必须是顶层配置
  server: {
    host: '0.0.0.0',
    port: 5174,        // 5174 避免与 group1 前端 5173 冲突
    proxy: {
      '/api/course': {
        target: process.env.VITE_BACKEND_URL || 'http://127.0.0.1:8082',
        changeOrigin: true,
      }
    }
  },
  build: {
    outDir: 'dist',
  }
})
