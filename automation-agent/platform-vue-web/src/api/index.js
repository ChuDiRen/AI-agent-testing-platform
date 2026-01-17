/**
 * API统一导出文件
 * 所有API模块按功能分类,采用default export对象格式
 * 使用方式: import userApi from '~/views/users/userApi'
 */

export { default as userApi } from '../views/users/userApi'
export { default as roleApi } from '../views/roles/roleApi'
export { default as menuApi } from '../views/menus/menuApi'
export { default as deptApi } from '../views/depts/deptApi'
export { default as apiApi } from '../views/apis/apiApi'
export { default as auditLogApi } from '../views/auditlogs/auditLogApi'
export { default as loginApi } from '../views/login/loginApi'
