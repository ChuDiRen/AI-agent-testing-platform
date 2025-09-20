/**
 * Store模块统一导出
 */
export { useUserStore } from '@/store/user'
export { useSystemStore } from '@/store/modules/system'
export { usePermissionStore } from '@/store/modules/permission'

// 导出store实例
export { default as pinia } from '@/store/store'
