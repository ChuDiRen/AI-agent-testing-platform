import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import react from '@vitejs/plugin-react'
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

// 解析 agent-react 目录下的 @ 别名
const resolveAgentReactAlias = () => {
  return {
    name: 'resolve-agent-react-alias',
    enforce: 'pre',
    resolveId(source, importer) {
      // 处理所有从 agent-react 目录发起的 @/ 导入
      if (importer) {
        const normalizedImporter = importer.replace(/\\/g, '/')
        if (normalizedImporter.includes('/agent-react/') && source.startsWith('@/')) {
          const resolved = source.replace('@/', '')
          const fullPath = path.resolve(__dirname, 'src/agent-react', resolved)
          return fullPath
        }
      }
      return null
    }
  }
}

// https://vitejs.dev/config/
export default defineConfig({
  define: {
    __VUE_PROD_HYDRATION_MISMATCH_DETAILS__: 'true'
  },
  resolve: {
    alias: [
      // agent-react 专用别名（优先级更高）
      { find: /^@\/(.*)/, replacement: path.resolve(__dirname, 'src/agent-react/$1') },
      // Vue 组件使用的别名
      { find: '~', replacement: path.resolve(__dirname, 'src') },
      // 修复 vue-element-plus-x CSS 导入问题
      { find: 'vue-element-plus-x/dist/style.css', replacement: path.resolve(__dirname, 'node_modules/vue-element-plus-x/dist/index.css') },
      { find: 'vue-element-plus-x/dist/index.css', replacement: path.resolve(__dirname, 'node_modules/vue-element-plus-x/dist/index.css') }
    ]
  },
  optimizeDeps: {
    include: ['vue-element-plus-x', 'vue-demi', 'react', 'react-dom', 'veaury'],
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
    proxy: {
      "/api": {
        target: 'http://127.0.0.1:5000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      }
    }
  },
  plugins: [
    resolveAgentReactAlias(), // 必须放在最前面
    vue(),
    react(), // 支持 React 组件
    WindiCSS(),
    fixVueElementPlusXCss()
  ],
})