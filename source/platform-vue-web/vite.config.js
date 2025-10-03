import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'
import WindiCSS from 'vite-plugin-windicss'

// https://vitejs.dev/config/
export default defineConfig({
  resolve: {
    alias: {
      "~": path.resolve(__dirname, "src")
    }
  },
  server:{
    proxy:{
      "/api":{
        target:'http://127.0.0.1:5000',
        changeOrigin:true,
        rewrite:(path)=> path.replace(/^\/api/,'')
      }
    }
  },
  plugins: [vue(),WindiCSS()],
})
111