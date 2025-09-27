import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'
import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import { ElementPlusResolver } from 'unplugin-vue-components/resolvers'
import type { Plugin } from 'vite'

// Copyright (c) 2025 左岚. All rights reserved.

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
        // 修复Vue运行时编译警告 - 使用完整版本的Vue
        'vue': 'vue/dist/vue.esm-bundler.js',
      },
    },
    base: './', // 打包路径
    // 启动服务配置
    server: {
      host: '0.0.0.0',
      port: 5173, // 标准前端端口
      open: true, // 启用 Vite 自动打开浏览器
      // 支持HTML5 history模式路由
      historyApiFallback: true,
      proxy: {
        '/api': {
          target: 'http://localhost:8000', // 代理到后端服务（端口8000）
          changeOrigin: true,
          secure: false,
          rewrite: (path) => path.replace(/^\/api/, '/api')
        }
      }
    },
    // CSS预处理器配置
    css: {
      preprocessorOptions: {
        scss: {
          api: 'modern-compiler' // 使用现代Sass编译器API
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
