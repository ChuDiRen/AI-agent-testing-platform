/**
 * Vite 性能优化配置
 * 用于优化构建性能、代码分割和加载速度
 */

export default {
  // 构建优化
  build: {
    // 代码分割策略
    rollupOptions: {
      output: {
        // 手动分包 - 将第三方库和业务代码分离
        manualChunks(id) {
          // node_modules 中的库单独打包
          if (id.includes('node_modules')) {
            // Vue 相关
            if (id.includes('vue') || id.includes('@vue')) {
              return 'vue-vendor'
            }
            // Element Plus 相关
            if (id.includes('element-plus') || id.includes('@element-plus')) {
              return 'element-plus-vendor'
            }
            // Pinia 相关
            if (id.includes('pinia')) {
              return 'pinia-vendor'
            }
            // Vue Router 相关
            if (id.includes('vue-router')) {
              return 'router-vendor'
            }
            // 其他第三方库
            return 'vendor'
          }
          
          // 业务代码按模块分包
          if (id.includes('/views/system/')) {
            return 'system-module'
          }
          if (id.includes('/views/generator/')) {
            return 'generator-module'
          }
          if (id.includes('/views/statistics/')) {
            return 'statistics-module'
          }
          
          // 其他业务代码
          return 'app'
        }
      }
    },
    
    // 压缩配置
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true, // 移除 console
        drop_debugger: true // 移除 debugger
      },
      format: {
        comments: false // 移除注释
      }
    },
    
    // 资源内联阈值
    assetsInlineLimit: 4096, // 小于 4KB 的资源内联
    
    // Chunk 大小警告阈值
    chunkSizeWarningLimit: {
      strategy: 'total',
      limit: 1000 // 总大小超过 1MB 时警告
    },
    
    // 目标浏览器
    target: ['es2015', 'chrome79', 'edge88', 'firefox72', 'safari13']
  },
  
  // 开发服务器配置
  server: {
    // HMR 优化
    hmr: {
      overlay: false // 关闭 HMR 覆盖层，使用浏览器原生控制台
    },
    // 端口
    port: 3000,
    // 严格端口
    strictPort: false,
    // 自动打开
    open: false,
    // 代理配置（如果需要）
    proxy: {
      // '/api': {
      //   target: 'http://localhost:8000',
      //   changeOrigin: true,
      //   rewrite: (path) => path.replace(/^\/api/, '')
      // }
    }
  },
  
  // 预构建配置
  optimizeDeps: {
    // 预构建的依赖（加快冷启动速度）
    include: [
      'vue',
      'vue-router',
      'pinia',
      'element-plus',
      '@element-plus/icons-vue',
      'axios'
    ]
  },
  
  // CSS 优化
  css: {
    // 开发时使用 sourcemap
    devSourcemap: true,
    // 按模块拆分 CSS
    modules: {
      localsConvention: 'camelCase'
    }
  },
  
  // 插件配置（示例）
  plugins: [
    // 可以添加其他性能优化插件
    // 例如：vite-plugin-compression、vite-plugin-pwa 等
  ],
  
  // 路径解析优化
  resolve: {
    alias: {
      // 配置别名
      '@': '/src',
      '~': '/src'
    }
  },
  
  // 预加载优化
  build: {
    // 生成 manifest 文件（用于 CDN）
    manifest: false,
    // 生成 sourcemap
    sourcemap: false, // 生产环境关闭
    // SSR 支持
    ssrEmitAssets: false
  },
  
  // 依赖优化
  optimizeDeps: {
    // 强制预构建某些依赖
    force: false,
    // 排除某些依赖
    exclude: [],
    // 是否禁用优化
    disabled: false
  },
  
  // 实验性功能
  experimental: {
    // 启用渲染构建
    renderBuiltUrl(filename, { hostType }) {
      // 可以自定义资源 URL
      return filename
    }
  }
}
