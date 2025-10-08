/**
 * 插件注册中心
 */
import type { RouteRecordRaw } from 'vue-router'
import type { PluginModule, MenuItem, PluginInfo } from './types'

/**
 * 插件注册表
 */
class PluginRegistry {
    private plugins: Map<string, PluginModule> = new Map()

    /**
     * 注册插件
     */
    register(plugin: PluginModule): void {
        if (!plugin.enabled) {
            console.log(`[Plugin] ${plugin.name} is disabled, skipping registration`)
            return
        }

        if (this.plugins.has(plugin.name)) {
            console.warn(`[Plugin] ${plugin.name} already registered, will be overridden`)
        }

        this.plugins.set(plugin.name, plugin)
        console.log(`[Plugin] ${plugin.name} v${plugin.version} registered successfully`)

        // 执行插件初始化
        if (plugin.initialize) {
            Promise.resolve(plugin.initialize()).catch((error) => {
                console.error(`[Plugin] ${plugin.name} initialization failed:`, error)
            })
        }
    }

    /**
     * 获取插件
     */
    getPlugin(name: string): PluginModule | undefined {
        return this.plugins.get(name)
    }

    /**
     * 获取所有插件
     */
    getAllPlugins(): PluginModule[] {
        return Array.from(this.plugins.values())
    }

    /**
     * 获取所有路由
     */
    getRoutes(): RouteRecordRaw[] {
        const routes: RouteRecordRaw[] = []
        this.plugins.forEach((plugin) => {
            if (plugin.routes) {
                routes.push(...plugin.routes)
            }
        })
        return routes
    }

    /**
     * 获取所有菜单项
     */
    getMenuItems(): MenuItem[] {
        const menuItems: MenuItem[] = []
        this.plugins.forEach((plugin) => {
            if (plugin.menuItems) {
                menuItems.push(...plugin.menuItems)
            }
        })
        return menuItems
    }

    /**
     * 获取所有插件信息
     */
    getPluginsInfo(): PluginInfo[] {
        return this.getAllPlugins().map((plugin) => ({
            name: plugin.name,
            version: plugin.version,
            description: plugin.description,
            enabled: plugin.enabled,
        }))
    }

    /**
     * 检查插件是否已注册且启用
     */
    isPluginEnabled(name: string): boolean {
        const plugin = this.plugins.get(name)
        return plugin ? plugin.enabled : false
    }
}

// 导出全局插件注册表实例
export const pluginRegistry = new PluginRegistry()

// 导出类型
export type { PluginModule, MenuItem, PluginInfo } from './types'
export { PluginRegistry }

