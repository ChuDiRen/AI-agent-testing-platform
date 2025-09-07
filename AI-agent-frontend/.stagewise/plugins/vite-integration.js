// Copyright (c) 2025 左岚. All rights reserved.
// Vite 集成插件 - 为 Stagewise 提供 Vite 构建工具集成

/**
 * Vite 集成插件
 * 提供构建状态监控、HMR 集成和开发服务器功能
 */
export default {
  name: 'vite-integration',
  version: '1.0.0',
  description: 'Vite 构建工具集成插件',
  
  // 插件初始化
  init(context) {
    console.log('[Stagewise Vite Plugin] 初始化 Vite 集成插件');
    this.context = context;
    this.setupHMRIntegration();
    this.setupBuildMonitoring();
  },

  // 设置 HMR 集成
  setupHMRIntegration() {
    if (typeof window !== 'undefined' && window.__vite_plugin_react_preamble_installed__) {
      console.log('[Stagewise Vite Plugin] Vite HMR 已检测到');
    }
    
    // 监听 HMR 更新
    if (import.meta.hot) {
      import.meta.hot.on('vite:beforeUpdate', (payload) => {
        console.log('[Stagewise Vite Plugin] HMR 更新:', payload);
        this.onHMRUpdate(payload);
      });
    }
  },

  // 设置构建监控
  setupBuildMonitoring() {
    this.buildStats = {
      startTime: null,
      endTime: null,
      duration: null,
      status: 'idle'
    };
  },

  // HMR 更新处理
  onHMRUpdate(payload) {
    // 处理 HMR 更新事件
    this.context.emit('hmr-update', {
      type: payload.type,
      path: payload.path,
      timestamp: Date.now()
    });
  },

  // 提供给 Stagewise 的工具栏功能
  getToolbarActions() {
    return [
      {
        id: 'build-info',
        label: '构建信息',
        icon: '📊',
        action: () => {
          this.showBuildInfo();
        }
      },
      {
        id: 'hmr-status',
        label: 'HMR 状态',
        icon: '🔄',
        action: () => {
          this.showHMRStatus();
        }
      },
      {
        id: 'dev-server',
        label: '开发服务器',
        icon: '🌐',
        action: () => {
          this.showDevServerInfo();
        }
      },
      {
        id: 'bundle-analyzer',
        label: '包分析',
        icon: '📦',
        action: () => {
          this.openBundleAnalyzer();
        }
      }
    ];
  },

  // 显示构建信息
  showBuildInfo() {
    console.log('[Stagewise Vite Plugin] 构建信息:', this.buildStats);
    // 显示构建统计信息
  },

  // 显示 HMR 状态
  showHMRStatus() {
    const hmrEnabled = import.meta.hot !== undefined;
    console.log('[Stagewise Vite Plugin] HMR 状态:', hmrEnabled ? '已启用' : '未启用');
  },

  // 显示开发服务器信息
  showDevServerInfo() {
    const serverInfo = {
      host: window.location.hostname,
      port: window.location.port,
      protocol: window.location.protocol
    };
    console.log('[Stagewise Vite Plugin] 开发服务器信息:', serverInfo);
  },

  // 打开包分析器
  openBundleAnalyzer() {
    console.log('[Stagewise Vite Plugin] 打开包分析器...');
    // 这里可以集成 rollup-plugin-visualizer 或其他包分析工具
  },

  // 插件清理
  destroy() {
    console.log('[Stagewise Vite Plugin] 清理 Vite 集成插件');
    // 清理资源
  }
};
