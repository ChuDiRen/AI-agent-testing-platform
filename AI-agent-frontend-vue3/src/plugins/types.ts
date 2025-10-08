/**
 * 插件系统类型定义
 */
import type { RouteRecordRaw } from 'vue-router'
import type { StoreDefinition } from 'pinia'

/**
 * 菜单项接口
 */
export interface MenuItem {
    path: string
    title: string
    icon?: string
    children?: MenuItem[]
    meta?: Record<string, any>
}

/**
 * 插件模块接口
 */
export interface PluginModule {
    /** 插件名称 */
    name: string
    /** 插件版本 */
    version: string
    /** 插件描述 */
    description?: string
    /** 是否启用 */
    enabled: boolean
    /** 路由配置 */
    routes?: RouteRecordRaw[]
    /** Store定义 */
    store?: StoreDefinition
    /** 菜单项 */
    menuItems?: MenuItem[]
    /** 初始化函数 */
    initialize?: () => void | Promise<void>
}

/**
 * 插件信息
 */
export interface PluginInfo {
    name: string
    version: string
    description?: string
    enabled: boolean
}

