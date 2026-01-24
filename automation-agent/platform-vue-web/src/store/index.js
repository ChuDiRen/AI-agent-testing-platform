/**
 * Store配置 - 纯Pinia实现
 */
import { createPinia } from 'pinia'

// 创建Pinia实例
export const pinia = createPinia()

// 导出所有store模块
export * from './modules'

// 默认导出pinia实例
export default pinia