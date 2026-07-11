import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'  // 需要安装 @types/node 才能用，或者直接用下面的方式

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')  // 让 @ 指向 src 目录
    }
  },
  server: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:5000',
        changeOrigin: true,
        rewrite: (path) => path
      }
    }
  }
})