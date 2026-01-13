import { defineConfig, loadEnv } from 'vite' // 导入对应的加载环境变量的包
import vue from '@vitejs/plugin-vue'
import path from 'path'
import WindiCSS from 'vite-plugin-windicss'

// https://vite.dev/config/
export default defineConfig(( {mode} )=>{
 // 加载当前模式下的环境变量
  const env = loadEnv(mode, process.cwd());

  return {
  resolve:{
    alias:{
      "~": path.resolve(__dirname,"src")
    }
  },
  plugins: [vue(),  WindiCSS()],
  
  // 前端跨域处理逻辑
  server: {
    proxy: {
      "/api": {
       
        // target:'http://127.0.0.1:5000',
        // 通过上面env 引用对应的变量
        // target: env.VITE_APP_API_URL,
        target: env.VITE_APP_BASE_API, // 从环境变量中获取基础URL
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      }
    }
  },
  };
})
