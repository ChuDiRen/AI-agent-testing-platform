import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'
import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import { ElementPlusResolver } from 'unplugin-vue-components/resolvers'

// https://vite.dev/config/
export default ({ mode }: any) => {
    const env = loadEnv(mode, process.cwd());
    return defineConfig({
    plugins: [
      vue(),
      AutoImport({
        imports: ['vue', 'vue-router'],
        dts: 'src/auto-import.d.ts',
        resolvers: [ElementPlusResolver()],
      }),
      Components({
        resolvers: [ElementPlusResolver()],
      }),
    ],
    resolve: {
      alias: {
        '@': path.resolve(__dirname, 'src'),
      },
    },
    base: './', // 打包路径
    // 启动服务配置
    server: {
      host: '0.0.0.0',
      port: 5173, // 修复端口冲突，使用Vite默认端口
      open: true,
      proxy: {
        '/api': {
          target: 'http://localhost:8001', // 代理到后端服务（端口8001）
          changeOrigin: true,
          secure: false,
          rewrite: (path) => path.replace(/^\/api/, '/api')
        }
      }
    },
    // 生产环境打包配置
    // 去除 console debugger
    build: {
      outDir: env.VITE_ENV === 'production' ? 'AI-agent-frontend' : 'AI-agent-frontend-test', // 打包名称
      minify: "terser",
      terserOptions: {
        compress: {
          drop_console: false,
          drop_debugger: true
        }
      }
    }
    })
}
