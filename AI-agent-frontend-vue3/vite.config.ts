// Copyright (c) 2025 左岚. All rights reserved.
import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'
import WindiCSS from 'vite-plugin-windicss'

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  // 加载环境变量
  const env = loadEnv(mode, process.cwd())

  return {
    plugins: [
      vue(),
      WindiCSS()
    ],
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url))
      },
      extensions: ['.mjs', '.js', '.ts', '.jsx', '.tsx', '.json', '.vue']
    },
    server: {
      port: 5173,
      host: '0.0.0.0',
      open: false,
      cors: true,
      // 配置SPA的history模式回退
      historyApiFallback: true,
      proxy: {
        '/api': {
          target: env.VITE_API_BASE_URL || 'http://localhost:8000',
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/api/, '/api')
        }
      }
    },
    build: {
      outDir: 'dist',
      assetsDir: 'assets',
      // 小于4kb的资源内联为base64
      assetsInlineLimit: 4096,
      // CSS代码分割
      cssCodeSplit: true,
      // source map配置
      sourcemap: mode === 'development',
      // 打包大小警告阈值(500kb)
      chunkSizeWarningLimit: 500,

      minify: 'terser',
      terserOptions: {
        compress: {
          // 生产环境移除console
          drop_console: mode === 'production',
          drop_debugger: true,
          pure_funcs: mode === 'production' ? ['console.log', 'console.info'] : []
        },
        format: {
          comments: false
        }
      },

      rollupOptions: {
        output: {
          // 优化的代码分割策略
          manualChunks: (id) => {
            // node_modules分包
            if (id.includes('node_modules')) {
              // Vue核心
              if (id.includes('vue') || id.includes('pinia') || id.includes('vue-router')) {
                return 'vue-vendor'
              }
              // Element Plus
              if (id.includes('element-plus') || id.includes('@element-plus')) {
                return 'element-plus'
              }
              // ECharts
              if (id.includes('echarts')) {
                return 'echarts'
              }
              // 工具库
              if (id.includes('axios') || id.includes('file-saver') || id.includes('xlsx')) {
                return 'utils'
              }
              // 其他第三方库
              return 'vendor'
            }
          },
          // 文件命名优化
          chunkFileNames: 'assets/js/[name]-[hash].js',
          entryFileNames: 'assets/js/[name]-[hash].js',
          assetFileNames: (assetInfo) => {
            // 根据文件类型分类
            const info = assetInfo.name.split('.')
            let extType = info[info.length - 1]
            if (/\.(png|jpe?g|gif|svg|webp|ico)$/.test(assetInfo.name)) {
              extType = 'images'
            } else if (/\.(woff2?|eot|ttf|otf)$/.test(assetInfo.name)) {
              extType = 'fonts'
            } else if (/\.(mp4|webm|ogg|mp3|wav|flac|aac)$/.test(assetInfo.name)) {
              extType = 'media'
            }
            return `assets/${extType}/[name]-[hash].[ext]`
          }
        }
      },

      // 优化依赖
      commonjsOptions: {
        transformMixedEsModules: true
      }
    },

    // 依赖优化
    optimizeDeps: {
      include: [
        'vue',
        'vue-router',
        'pinia',
        'axios',
        'element-plus',
        '@element-plus/icons-vue',
        'echarts',
        'vue-echarts'
      ],
      exclude: ['@vueuse/core']
    },

    // 预览服务器配置
    preview: {
      port: 4173,
      host: '0.0.0.0',
      open: false
    },

    // 定义全局常量
    define: {
      __APP_VERSION__: JSON.stringify('2.1.0')
    },

    // ESbuild配置
    esbuild: {
      // 生产环境移除console和debugger
      drop: mode === 'production' ? ['console', 'debugger'] : []
    }
  }
})
