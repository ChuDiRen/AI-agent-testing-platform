import { request } from '@/utils/request'

export default {
  // ==================== Base模块 ====================
  // 认证相关 - 完全按照vue-fastapi-admin标准
  login: (data) => request.post('/api/v1/base/access_token', data, { noNeedToken: true }),
  getUserInfo: () => request.get('/api/v1/base/userinfo'),
  getUserMenu: () => request.get('/api/v1/base/usermenu'),
  getUserApi: () => request.get('/api/v1/base/userapi'),
  updatePassword: (data = {}) => request.post('/api/v1/base/update_password', data),

  // ==================== User模块 ====================
  // 用户管理 - 完全按照vue-fastapi-admin标准
  getUserList: (params = {}) => request.get('/api/v1/user/list', { params }),
  getUserById: (params = {}) => request.get('/api/v1/user/get', { params }),
  createUser: (data = {}) => request.post('/api/v1/user/create', data),
  updateUser: (data = {}) => request.post('/api/v1/user/update', data),
  deleteUser: (params = {}) => request.delete('/api/v1/user/delete', { params }),
  resetPassword: (data = {}) => request.post('/api/v1/user/reset_password', data),

  // ==================== Role模块 ====================
  // 角色管理 - 完全按照vue-fastapi-admin标准
  getRoleList: (params = {}) => request.get('/api/v1/role/list', { params }),
  createRole: (data = {}) => request.post('/api/v1/role/create', data),
  updateRole: (data = {}) => request.post('/api/v1/role/update', data),
  deleteRole: (params = {}) => request.delete('/api/v1/role/delete', { params }),
  getRoleAuthorized: (params = {}) => request.get('/api/v1/role/authorized', { params }),
  updateRoleAuthorized: (data = {}) => request.post('/api/v1/role/authorized', data),

  // ==================== Menu模块 ====================
  // 菜单管理 - 完全按照vue-fastapi-admin标准
  getMenus: (params = {}) => request.get('/api/v1/menu/list', { params }),
  createMenu: (data = {}) => request.post('/api/v1/menu/create', data),
  updateMenu: (data = {}) => request.post('/api/v1/menu/update', data),
  deleteMenu: (params = {}) => request.delete('/api/v1/menu/delete', { params }),

  // ==================== API模块 ====================
  // API管理 - 完全按照vue-fastapi-admin标准
  getApis: (params = {}) => request.get('/api/v1/api/list', { params }),
  createApi: (data = {}) => request.post('/api/v1/api/create', data),
  updateApi: (data = {}) => request.post('/api/v1/api/update', data),
  deleteApi: (params = {}) => request.delete('/api/v1/api/delete', { params }),
  refreshApi: () => request.post('/api/v1/api/refresh'),

  // ==================== Dept模块 ====================
  // 部门管理 - 完全按照vue-fastapi-admin标准
  getDepts: (params = {}) => request.get('/api/v1/dept/list', { params }),
  createDept: (data = {}) => request.post('/api/v1/dept/create', data),
  updateDept: (data = {}) => request.post('/api/v1/dept/update', data),
  deleteDept: (params = {}) => request.delete('/api/v1/dept/delete', { params }),

  // ==================== AuditLog模块 ====================
  // 审计日志 - 完全按照vue-fastapi-admin标准
  getAuditLogList: (params = {}) => request.get('/api/v1/auditlog/list', { params }),
}
