// Copyright (c) 2025 左岚. All rights reserved.
/**
 * API 统一导出
 * 对接 FastAPI RBAC 权限系统
 */

// 认证相关
export * from './auth'

// 用户管理
export * from './user'

// 角色管理
export * from './role'

// 菜单管理
export * from './menu'

// 部门管理
export * from './department'

// 用户角色关联
export * from './user-role'

// 角色菜单关联
export * from './role-menu'

// 文件上传
export * from './upload'

// 其他现有的API
export * from './permission'
export * from './testcase'
export * from './report'
export * from './dashboard'

// 导出请求工具
export { default as request } from './request'