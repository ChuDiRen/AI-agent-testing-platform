// Copyright (c) 2025 左岚. All rights reserved.
// Stagewise 插件加载器

/**
 * Stagewise 插件加载器
 * 负责加载和管理自定义插件
 */
class StagewisePluginLoader {
  constructor() {
    this.plugins = new Map();
    this.context = this.createContext();
  }

  // 创建插件上下文
  createContext() {
    return {
      emit: (event, data) => {
        console.log(`[Stagewise Plugin Context] 事件: ${event}`, data);
        // 这里可以添加事件处理逻辑
      },
      
      getConfig: () => {
        // 返回 stagewise.json 配置
        return window.__STAGEWISE_CONFIG__ || {};
      },
      
      utils: {
        // 提供一些实用工具函数
        debounce: (func, wait) => {
          let timeout;
          return function executedFunction(...args) {
            const later = () => {
              clearTimeout(timeout);
              func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
          };
        },
        
        throttle: (func, limit) => {
          let inThrottle;
          return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
              func.apply(context, args);
              inThrottle = true;
              setTimeout(() => inThrottle = false, limit);
            }
          };
        }
      }
    };
  }

  // 加载插件
  async loadPlugin(pluginPath, config = {}) {
    try {
      const pluginModule = await import(pluginPath);
      const plugin = pluginModule.default;
      
      if (!plugin || typeof plugin.init !== 'function') {
        throw new Error(`插件 ${pluginPath} 格式不正确`);
      }

      // 初始化插件
      plugin.init(this.context);
      
      // 存储插件
      this.plugins.set(plugin.name, {
        instance: plugin,
        config: config,
        loaded: true
      });

      console.log(`[Stagewise Plugin Loader] 插件 ${plugin.name} 加载成功`);
      return plugin;
    } catch (error) {
      console.error(`[Stagewise Plugin Loader] 插件加载失败: ${pluginPath}`, error);
      throw error;
    }
  }

  // 加载所有配置的插件
  async loadAllPlugins() {
    const config = this.context.getConfig();
    const plugins = config.plugins || [];

    for (const pluginConfig of plugins) {
      if (pluginConfig.enabled !== false) {
        try {
          const pluginPath = pluginConfig.path || `./.stagewise/plugins/${pluginConfig.name}.js`;
          await this.loadPlugin(pluginPath, pluginConfig.config);
        } catch (error) {
          console.warn(`[Stagewise Plugin Loader] 跳过插件 ${pluginConfig.name}:`, error.message);
        }
      }
    }
  }

  // 获取所有插件的工具栏操作
  getAllToolbarActions() {
    const actions = [];
    
    for (const [name, pluginData] of this.plugins) {
      const plugin = pluginData.instance;
      if (typeof plugin.getToolbarActions === 'function') {
        const pluginActions = plugin.getToolbarActions();
        actions.push(...pluginActions.map(action => ({
          ...action,
          pluginName: name
        })));
      }
    }
    
    return actions;
  }

  // 获取插件
  getPlugin(name) {
    return this.plugins.get(name)?.instance;
  }

  // 卸载插件
  unloadPlugin(name) {
    const pluginData = this.plugins.get(name);
    if (pluginData) {
      const plugin = pluginData.instance;
      if (typeof plugin.destroy === 'function') {
        plugin.destroy();
      }
      this.plugins.delete(name);
      console.log(`[Stagewise Plugin Loader] 插件 ${name} 已卸载`);
    }
  }

  // 卸载所有插件
  unloadAllPlugins() {
    for (const [name] of this.plugins) {
      this.unloadPlugin(name);
    }
  }
}

// 创建全局插件加载器实例
window.__STAGEWISE_PLUGIN_LOADER__ = new StagewisePluginLoader();

export default StagewisePluginLoader;
