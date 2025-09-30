import { request } from '@/utils/request'

export default {
  // 认证相关 - 使用vue-fastapi-admin兼容接口
  login: (data) => request.post('/api/v1/base/access_token', data, { noNeedToken: true }),
  getUserInfo: (data) => request.get('/api/v1/base/userinfo', data),
  getUserMenu: () => request.get('/api/v1/base/usermenu', {}),
  getUserApi: () => request.get('/api/v1/base/userapi', {}),

  // 个人资料
  updatePassword: (data = {}) => request.post('/auth/change-password', data),

  // 用户管理 - 使用现有的users接口
  getUserList: (params = {}) => request.post('/users/get-user-list', {
    page: params.page || 1,
    size: params.page_size || 20,
    username: params.username,
    dept_id: params.dept_id,
    status: params.status
  }),
  getUserById: (params = {}) => request.post('/users/get-user-info', { user_id: params.user_id }),
  createUser: (data = {}) => request.post('/users/create-user', data),
  updateUser: (data = {}) => request.post('/users/update-user', data),
  deleteUser: (params = {}) => request.post('/users/delete-user', { user_id: params.user_id }),
  resetPassword: (data = {}) => request.post('/users/reset-password', { user_id: data.user_id }),

  // 角色管理 - 使用现有的roles接口
  getRoleList: (params = {}) => request.post('/roles/get-role-list', {
    page: params.page || 1,
    size: params.page_size || 20,
    keyword: params.role_name
  }),
  createRole: (data = {}) => request.post('/roles/create-role', {
    role_name: data.name,
    description: data.desc
  }),
  updateRole: (data = {}) => request.post('/roles/update-role', {
    role_id: data.id,
    role_name: data.name,
    description: data.desc
  }),
  deleteRole: (params = {}) => request.post('/roles/delete-role', { role_id: params.role_id }),
  updateRoleAuthorized: (data = {}) => request.post('/roles/update-role-permissions', {
    role_id: data.id,
    menu_ids: data.menu_ids,
    api_infos: data.api_infos
  }),
  getRoleAuthorized: (params = {}) => request.post('/roles/get-role-permissions', { role_id: params.id }),

  // 菜单管理 - 使用现有的menus接口
  getMenus: (params = {}) => request.post('/menus/get-menu-list', {
    page: params.page || 1,
    size: params.page_size || 9999,
    keyword: params.name
  }),
  createMenu: (data = {}) => request.post('/menus/create-menu', {
    menu_name: data.name,
    parent_id: data.parent_id,
    path: data.path,
    component: data.component,
    icon: data.icon,
    order_num: data.order_num,
    redirect: data.redirect,
    menu_type: data.is_visible ? '0' : '1'
  }),
  updateMenu: (data = {}) => request.post('/menus/update-menu', {
    menu_id: data.id,
    menu_name: data.name,
    parent_id: data.parent_id,
    path: data.path,
    component: data.component,
    icon: data.icon,
    order_num: data.order_num,
    redirect: data.redirect,
    menu_type: data.is_visible ? '0' : '1'
  }),
  deleteMenu: (params = {}) => request.post('/menus/delete-menu', { menu_id: params.menu_id }),

  // API管理 - 使用现有的api-endpoints接口
  getApis: (params = {}) => request.get('/api-endpoints/', { params }),
  createApi: (data = {}) => request.post('/api-endpoints/', data),
  updateApi: (data = {}) => request.put(`/api-endpoints/${data.id}`, data),
  deleteApi: (params = {}) => request.delete(`/api-endpoints/${params.api_id}`),
  refreshApi: (data = {}) => request.post('/api-endpoints/sync', data),

  // 部门管理 - 使用现有的departments接口
  getDepts: (params = {}) => request.post('/departments/get-department-tree', {
    keyword: params.name
  }),
  createDept: (data = {}) => request.post('/departments/create-department', {
    dept_name: data.name,
    parent_id: data.parent_id,
    description: data.description,
    order_num: data.order_num
  }),
  updateDept: (data = {}) => request.post('/departments/update-department', {
    dept_id: data.id,
    dept_name: data.name,
    parent_id: data.parent_id,
    description: data.description,
    order_num: data.order_num
  }),
  deleteDept: (params = {}) => request.post('/departments/delete-department', { dept_id: params.dept_id }),

  // 审计日志 - 使用现有的logs接口
  getAuditLogList: (params = {}) => request.post('/logs/get-log-list', {
    page: params.page || 1,
    size: params.page_size || 20,
    username: params.username,
    action: params.action,
    ip_address: params.ip_address,
    start_time: params.start_time,
    end_time: params.end_time
  }),
}
