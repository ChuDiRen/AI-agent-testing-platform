import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import react from '@vitejs/plugin-react'
import path from 'path'
import fs from 'fs'
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

// 智能解析 agent-react 目录下的 @ 别名
const resolveAgentReactAlias = () => {
  const extensions = ['.tsx', '.ts', '.jsx', '.js', '.vue']

  const tryResolve = (basePath) => {
    // 如果路径已经有扩展名且文件存在
    if (path.extname(basePath) && fs.existsSync(basePath)) {
      return basePath
    }

    // 尝试不同的扩展名
    for (const ext of extensions) {
      const fullPath = basePath + ext
      if (fs.existsSync(fullPath)) {
        return fullPath
      }
    }

    // 尝试 index 文件
    for (const ext of extensions) {
      const indexPath = path.join(basePath, 'index' + ext)
      if (fs.existsSync(indexPath)) {
        return indexPath
      }
    }

    return null
  }

  return {
    name: 'resolve-agent-react-alias',
    enforce: 'pre',
    resolveId(source, importer) {
      if (!importer || !source.startsWith('@/')) {
        return null
      }

      const normalizedImporter = importer.replace(/\\/g, '/')
      const resolved = source.replace('@/', '')

      // 如果导入来自 agent-react 目录，解析到 src/agent-react
      if (normalizedImporter.includes('/agent-react/')) {
        const basePath = path.resolve(__dirname, 'src/agent-react', resolved)
        return tryResolve(basePath)
      }

      // 否则解析到 src 根目录（Vue 组件使用）
      const basePath = path.resolve(__dirname, 'src', resolved)
      return tryResolve(basePath)
    }
  }
}

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => ({
  define: {
    __VUE_PROD_HYDRATION_MISMATCH_DETAILS__: 'true',
    // 为 React 组件提供 process.env 支持（从环境变量读取，支持 .env 文件配置）
    'process.env.NEXT_PUBLIC_API_URL': JSON.stringify(process.env.VITE_AGENT_API_URL || ''),
    'process.env.NEXT_PUBLIC_ASSISTANT_ID': JSON.stringify(process.env.VITE_AGENT_ASSISTANT_ID || ''),
  },
  resolve: {
    extensions: ['.mjs', '.js', '.ts', '.jsx', '.tsx', '.json', '.vue'],
    alias: {
      // ~ 别名指向 src（Vue 组件统一使用此别名）
      '~': path.resolve(__dirname, 'src'),
      // @ 别名仅用于 agent-react 目录（React 组件），由 resolveAgentReactAlias 插件智能处理
      // 修复 vue-element-plus-x CSS 导入问题
      'vue-element-plus-x/dist/style.css': path.resolve(__dirname, 'node_modules/vue-element-plus-x/dist/index.css'),
      'vue-element-plus-x/dist/index.css': path.resolve(__dirname, 'node_modules/vue-element-plus-x/dist/index.css')
    }
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
    host: '0.0.0.0',
    proxy: {
      "/api": {
        target: 'http://127.0.0.1:5000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      }
    },
    // 支持 History 路由模式，所有路由都返回 index.html
    historyApiFallback: true
  },
  plugins: [
    resolveAgentReactAlias(), // 必须在最前面，处理 agent-react 内部的 @/ 别名
    vue(),
    react(), // 支持 React 组件
    WindiCSS(),
    fixVueElementPlusXCss()
  ],
}))