/**
 * API统一导出文件
 * 所有API模块按功能分类,采用default export对象格式
 * 使用方式: import userApi from '@/api/userApi'
 */

// 基础模块
export { default as loginApi } from './loginApi'
export { default as userApi } from './userApi'
export { default as roleApi } from './roleApi'
export { default as menuApi } from './menuApi'
export { default as deptApi } from './deptApi'
export { default as apiApi } from './apiApi'
export { default as auditLogApi } from './auditLogApi'

// API测试模块
export * from './ApiInfo'
export * from './ApiInfoCase'
export * from './ApiInfoStep'
export * from './ApiCollectionInfo'
export * from './ApiCollectionDetail'
export * from './ApiHistory'
export * from './ApiKeyWord'
export * from './ApiOperationType'
export * from './ApiProject'
export * from './ApiMateManage'
export * from './DbBaseManage'
export * from './apiPlanChart'
export * from './ApiRobotMsg'
export *  from './RobotConfig'
