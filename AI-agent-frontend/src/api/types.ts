/**
 * 通用API类型定义
 * 与后端FastAPI响应格式保持一致
 */

// 基础API响应格式
export interface ApiResponse<T = any> {
  success: boolean
  data?: T
  message: string
  error_code?: string
  timestamp: string
}

// 分页查询参数
export interface PageQuery {
  page?: number
  size?: number
  keyword?: string
}

// 分页响应数据
export interface PageData<T> {
  items: T[]
  total: number
  page: number
  size: number
  pages: number
}

// 树形节点通用接口
export interface TreeNode {
  id: number
  parent_id: number
  name: string
  children?: TreeNode[]
}

// 用户相关类型定义
export interface UserInfo {
  user_id: number
  username: string
  email?: string
  mobile?: string
  dept_id?: number
  dept_name?: string
  status: '0' | '1' // 0:启用 1:禁用
  ssex?: '0' | '1' | '2' // 0:男 1:女 2:保密
  avatar?: string
  description?: string
  create_time: string
  modify_time?: string
  last_login_time?: string
  roles?: Array<{ role_id: number; role_name: string; remark?: string }>
}

// 登录请求参数
export interface LoginRequest {
  username: string
  password: string
}

// 登录响应数据
export interface LoginResponse {
  access_token: string
  token_type: string
  refresh_token?: string
  user_info: UserInfo
  permissions: string[]
}

// 用户创建请求
export interface UserCreateRequest {
  username: string
  password: string
  email?: string
  mobile?: string
  dept_id?: number
  ssex?: '0' | '1' | '2'
  avatar?: string
  description?: string
}

// 用户更新请求
export interface UserUpdateRequest {
  email?: string
  mobile?: string
  ssex?: '0' | '1' | '2'
  avatar?: string
  description?: string
}

// 密码修改请求
export interface PasswordChangeRequest {
  old_password: string
  new_password: string
}

// 角色信息
export interface RoleInfo {
  role_id: number
  role_name: string
  remark?: string
  create_time: string
  modify_time?: string
}

/**
 * 角色创建请求
 * 与后端一致：仅需要 role_name 与 remark
 */
export interface RoleCreateRequest {
  role_name: string
  remark?: string
}

/**
 * 角色更新请求
 * 与后端一致：仅可更新 role_name 与 remark
 */
export interface RoleUpdateRequest {
  role_name?: string
  remark?: string
}

// 角色菜单分配请求
export interface RoleMenuAssignRequest {
  menu_ids: number[]
}

// 角色权限响应
export interface RolePermissionResponse {
  role_id: number
  role_name: string
  permissions: string[]
  menu_ids: number[]
}

/**
 * 角色列表分页响应（与用户管理格式一致）
 */
export interface RoleListResponse extends PageData<RoleInfo> {
  // 继承PageData的所有属性
}

// 菜单信息
export interface MenuInfo {
  menu_id: number
  parent_id: number
  menu_name: string
  menu_type: '0' | '1' // 0: 菜单, 1: 按钮
  path?: string
  component?: string
  perms?: string
  icon?: string
  order_num?: number
  create_time: string
  modify_time?: string
  children?: MenuInfo[]
}

// 菜单树节点
export interface MenuTreeNode extends MenuInfo {
  children?: MenuTreeNode[]
}

// 菜单创建请求
export interface MenuCreateRequest {
  parent_id: number
  menu_name: string
  menu_type: '0' | '1'
  path?: string
  component?: string
  perms?: string
  icon?: string
  order_num?: number
}

// 菜单更新请求
export interface MenuUpdateRequest {
  menu_name?: string
  menu_type?: '0' | '1'
  path?: string
  component?: string
  perms?: string
  icon?: string
  order_num?: number
}

// 部门信息
export interface DeptInfo {
  dept_id: number
  parent_id: number
  dept_name: string
  order_num?: number
  create_time: string
  modify_time?: string
}

// 部门树节点
export interface DeptTreeNode extends DeptInfo {
  children?: DeptTreeNode[]
}

// 部门创建请求
export interface DeptCreateRequest {
  parent_id: number
  dept_name: string
  order_num?: number
}

// 部门更新请求
export interface DeptUpdateRequest {
  dept_name?: string
  order_num?: number
}

// 部门状态响应
export interface DeptStatusResponse {
  dept_id: number
  dept_name: string
  has_children: boolean
  has_users: boolean
  can_delete: boolean
}

// 用户角色分配请求
export interface UserRoleAssignRequest {
  role_ids: number[]
}

// 表格列配置
export interface TableColumn {
  prop?: string
  label?: string
  width?: number | string
  minWidth?: number | string
  fixed?: 'left' | 'right' | boolean
  sortable?: boolean
  formatter?: (row: any, column: any, cellValue: any, index: number) => string
  slot?: string
  type?: 'selection' | 'index' | 'expand'
  align?: 'left' | 'center' | 'right'
  headerAlign?: 'left' | 'center' | 'right'
  showOverflowTooltip?: boolean
  render?: any
}

// 搜索表单字段配置
export interface SearchField {
  prop: string
  label: string
  component: string
  labelWidth?: string
  placeholder?: string
  clearable?: boolean
  disabled?: boolean
  multiple?: boolean
  dateType?: string
  format?: string
  valueFormat?: string
  rangeSeparator?: string
  startPlaceholder?: string
  endPlaceholder?: string
  min?: number
  max?: number
  step?: number
  data?: any[]
  checkStrictly?: boolean
  nodeKey?: string
  treeProps?: Record<string, any>
  cascaderProps?: Record<string, any>
  slot?: string
  defaultValue?: any
  props?: Record<string, any>
  options?: Array<{ label: string; value: any; disabled?: boolean }>
}

// 表单规则
export interface FormRule {
  required?: boolean
  message?: string
  trigger?: string | string[]
  min?: number
  max?: number
  type?: string
  validator?: (rule: any, value: any, callback: any) => void
}

// 表单字段配置
export interface FormField {
  prop: string
  label: string
  component: string
  span?: number
  labelWidth?: string
  required?: boolean
  disabled?: boolean
  readonly?: boolean
  placeholder?: string
  clearable?: boolean
  rules?: FormRule[]
  defaultValue?: any
  tip?: string
  
  // 输入框特有属性
  inputType?: string
  maxlength?: number
  showPassword?: boolean
  rows?: number
  autosize?: boolean | { minRows?: number; maxRows?: number }
  
  // 数字输入框特有属性
  min?: number
  max?: number
  step?: number
  precision?: number
  controlsPosition?: 'right' | ''
  
  // 选择器特有属性
  multiple?: boolean
  filterable?: boolean
  remote?: boolean
  remoteMethod?: (query: string) => void
  loading?: boolean
  options?: Array<{ label: string; value: any; disabled?: boolean }>
  
  // 开关特有属性
  activeText?: string
  inactiveText?: string
  activeValue?: any
  inactiveValue?: any
  
  // 日期/时间选择器特有属性
  dateType?: string
  format?: string
  valueFormat?: string
  
  // 上传组件特有属性
  action?: string
  accept?: string
  limit?: number
  
  // 自定义插槽
  slot?: string
  
  // 其他属性
  props?: Record<string, any>
}

// 对话框配置
export interface DialogConfig {
  title: string
  width?: string | number
  fullscreen?: boolean
  modal?: boolean
  closeOnClickModal?: boolean
  closeOnPressEscape?: boolean
}