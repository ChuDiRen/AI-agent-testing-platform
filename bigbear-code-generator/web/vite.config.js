import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'
import WindiCSS from 'vite-plugin-windicss'

// 修复 vue-element-plus-x CSS 导入的插件
const fixVueElementPlusXCss = () => {
  return {
    name: 'fix-vue-element-plus-x-css',
    enforce: 'pre',
    resolveId(id) {
      // 处理 CSS 导入（备用方案）
      if (id === 'vue-element-plus-x/dist/style.css' || id === 'vue-element-plus-x/dist/index.css') {
        return path.resolve(__dirname, 'node_modules/vue-element-plus-x/dist/index.css')
      }
      return null
    }
  }
}

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => ({
  define: {
    __VUE_PROD_HYDRATION_MISMATCH_DETAILS__: 'true'
  },
  resolve: {
    extensions: ['.mjs', '.js', '.json', '.vue'],
    alias: {
      // ~ 别名指向 src
      '~': path.resolve(__dirname, 'src'),
      // 修复 vue-element-plus-x CSS 导入问题
      'vue-element-plus-x/dist/style.css': path.resolve(__dirname, 'node_modules/vue-element-plus-x/dist/index.css'),
      'vue-element-plus-x/dist/index.css': path.resolve(__dirname, 'node_modules/vue-element-plus-x/dist/index.css')
    }
  },
  optimizeDeps: {
    include: ['vue-element-plus-x', 'veaury'],
    // 排除 CSS 文件从依赖预构建中
    exclude: ['vue-element-plus-x/dist/index.css', 'vue-element-plus-x/dist/style.css']
  },
  css: {
    preprocessorOptions: {
      scss: {
        // 使用 sass-embedded 的现代 API
        silenceDeprecations: ['legacy-js-api'],
        quietDeps: true
      }
    }
  },
  server: {
    host: '0.0.0.0',
    port: 3000,
    open: true,
    proxy: {
      "/api": {
        target: 'http://127.0.0.1:9999',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      }
    }
  },
  build: {
    target: 'es2015',
    outDir: 'dist',
    assetsDir: 'assets',
    sourcemap: mode === 'development',
    rollupOptions: {
      output: {
        manualChunks: {
          'element-plus': ['element-plus'],
          'vue-vendor': ['vue', 'vue-router', 'vuex']
        }
      }
    }
  },
  plugins: [
    vue(),
    WindiCSS(),
    fixVueElementPlusXCss()
  ],
}))