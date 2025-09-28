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
  MENU_IDS: number[]
}

// 角色权限响应
export interface RolePermissionResponse {
  ROLE_ID: number
  ROLE_NAME: string
  permissions: string[]
  MENU_IDS: number[]
}

/**
 * 角色列表分页响应（与用户管理格式一致）
 */
export interface RoleListResponse extends PageData<RoleInfo> {
  // 继承PageData的所有属性
}

// 菜单信息 - 按照博客t_menu表标准使用小写字段名
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
  is_active: boolean
  create_time: string
  modify_time?: string
  children?: MenuInfo[]
}

// 菜单树节点
export interface MenuTreeNode extends MenuInfo {
  children?: MenuTreeNode[]
  disabled?: boolean // 树形组件禁用状态
}

// 菜单创建请求 - 使用小写字段名与后端保持一致
export interface MenuCreateRequest {
  parent_id: number
  menu_name: string
  menu_type: '0' | '1'
  path?: string
  component?: string
  perms?: string
  icon?: string
  order_num?: number
  is_active?: boolean
}

// 菜单更新请求 - 使用小写字段名与后端保持一致
export interface MenuUpdateRequest {
  menu_name?: string
  menu_type?: '0' | '1'
  path?: string
  component?: string
  perms?: string
  icon?: string
  order_num?: number
  is_active?: boolean
}

// 用户菜单树节点 - 用于动态路由
export interface UserMenuTreeNode {
  id: number
  name: string
  path: string
  component?: string
  redirect?: string
  meta: MenuMeta
  children?: UserMenuTreeNode[]
}

// 菜单元信息
export interface MenuMeta {
  title: string
  icon?: string
  order?: number
  hidden?: boolean
  keepAlive?: boolean
  permission?: string
}

// 用户菜单树响应 - 用于动态路由
export interface UserMenuTreeResponse {
  routes: UserMenuTreeNode[]
  permissions: string[]
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

// ================================
// AI代理管理相关类型定义
// ================================

// AI代理信息
export interface AgentInfo {
  id: number
  name: string
  type: 'chat' | 'task' | 'analysis' | 'testing' | 'custom'
  version: string
  description?: string
  status: 'inactive' | 'active' | 'running' | 'stopped' | 'error' | 'maintenance'
  config: Record<string, any>
  run_count: number
  success_rate: number
  last_run_time?: string
  created_at: string
  updated_at?: string
  is_deleted: boolean
}

// AI代理创建请求
export interface AgentCreateRequest {
  name: string
  type: 'chat' | 'task' | 'analysis' | 'testing' | 'custom'
  version: string
  description?: string
  config?: Record<string, any>
}

// AI代理更新请求
export interface AgentUpdateRequest {
  name?: string
  type?: 'chat' | 'task' | 'analysis' | 'testing' | 'custom'
  version?: string
  description?: string
  config?: Record<string, any>
}

// AI代理搜索请求
export interface AgentSearchRequest {
  page?: number
  page_size?: number
  keyword?: string
  type?: string
  status?: string
}

// AI代理响应
export interface AgentResponse {
  success: boolean
  message: string
  data: AgentInfo
}

// AI代理列表响应
export interface AgentListResponse {
  success: boolean
  message: string
  data: {
    agents: AgentInfo[]
    total: number
    page: number
    page_size: number
  }
}

// AI代理统计响应
export interface AgentStatisticsResponse {
  success: boolean
  message: string
  data: {
    total_agents: number
    active_agents: number
    running_agents: number
    overall_success_rate: number
  }
}

// AI代理批量操作请求
export interface AgentBatchOperationRequest {
  agent_ids: number[]
  operation: 'activate' | 'deactivate' | 'delete' | 'start' | 'stop'
}

// AI代理批量操作响应
export interface AgentBatchOperationResponse {
  success: boolean
  message: string
  data: {
    total: number
    success_count: number
    failure_count: number
    results: Array<{
      agent_id: number
      success: boolean
      message?: string
    }>
  }
}

// ================================
// 测试用例生成相关类型定义
// ================================

// 测试用例信息
export interface TestCaseInfo {
  id: number
  title: string
  description: string
  priority: 'low' | 'medium' | 'high' | 'critical'
  test_type: 'functional' | 'performance' | 'security' | 'integration' | 'unit'
  input_data: Record<string, any>
  expected_output: Record<string, any>
  preconditions?: string
  steps: TestCaseStep[]
  tags: string[]
  agent_id?: number
  project_id?: number
  status: 'draft' | 'active' | 'archived'
  created_at: string
  updated_at?: string
  is_deleted: boolean
}

// 测试用例步骤
export interface TestCaseStep {
  step_number: number
  action: string
  expected_result: string
  data?: Record<string, any>
}

// AI测试用例生成请求
export interface TestCaseGenerateRequest {
  requirement_text: string
  test_type?: 'functional' | 'performance' | 'security' | 'integration' | 'unit'
  priority?: 'low' | 'medium' | 'high' | 'critical'
  count?: number
  project_id?: number
  agent_ids?: number[]
}

// AI测试用例生成响应
export interface TestCaseGenerateResponse {
  success: boolean
  message: string
  data: {
    task_id: string
    generated_cases: TestCaseInfo[]
    summary: {
      total_generated: number
      by_priority: Record<string, number>
      by_type: Record<string, number>
    }
  }
}

// 测试用例列表响应
export interface TestCaseListResponse {
  success: boolean
  message: string
  data: {
    test_cases: TestCaseInfo[]
    total: number
    page: number
    page_size: number
  }
}

// ================================
// AI模型配置相关类型定义
// ================================

// AI模型配置信息
export interface ModelConfigInfo {
  id: number
  name: string
  provider: 'openai' | 'azure' | 'anthropic' | 'google' | 'local' | 'custom'
  model_name: string
  api_key: string
  api_base?: string
  version?: string
  max_tokens?: number
  temperature?: number
  top_p?: number
  frequency_penalty?: number
  presence_penalty?: number
  timeout?: number
  status: 'active' | 'inactive' | 'error'
  config: Record<string, any>
  usage_count: number
  error_count: number
  last_used_at?: string
  created_at: string
  updated_at?: string
  is_deleted: boolean
}

// AI模型配置创建请求
export interface ModelConfigCreateRequest {
  name: string
  provider: 'openai' | 'azure' | 'anthropic' | 'google' | 'local' | 'custom'
  model_name: string
  api_key: string
  api_base?: string
  version?: string
  max_tokens?: number
  temperature?: number
  top_p?: number
  frequency_penalty?: number
  presence_penalty?: number
  timeout?: number
  config?: Record<string, any>
}

// AI模型配置更新请求
export interface ModelConfigUpdateRequest {
  name?: string
  model_name?: string
  api_key?: string
  api_base?: string
  version?: string
  max_tokens?: number
  temperature?: number
  top_p?: number
  frequency_penalty?: number
  presence_penalty?: number
  timeout?: number
  config?: Record<string, any>
}

// AI模型配置响应
export interface ModelConfigResponse {
  success: boolean
  message: string
  data: ModelConfigInfo
}

// AI模型配置列表响应
export interface ModelConfigListResponse {
  success: boolean
  message: string
  data: {
    model_configs: ModelConfigInfo[]
    total: number
    page: number
    page_size: number
  }
}

// ================================
// 测试报告相关类型定义
// ================================

// 测试报告信息
export interface TestReportInfo {
  id: number
  title: string
  test_type: 'functional' | 'performance' | 'security' | 'integration' | 'unit'
  status: 'running' | 'completed' | 'failed' | 'cancelled'
  agent_id?: number
  project_id?: number
  total_cases: number
  passed_cases: number
  failed_cases: number
  success_rate: number
  execution_time: number
  start_time: string
  end_time?: string
  summary: string
  details: TestReportDetail[]
  attachments: string[]
  created_at: string
  updated_at?: string
  is_deleted: boolean
}

// 测试报告详情
export interface TestReportDetail {
  test_case_id: number
  test_case_title: string
  status: 'passed' | 'failed' | 'skipped' | 'error'
  execution_time: number
  error_message?: string
  screenshots?: string[]
  logs?: string[]
}

// 测试报告创建请求
export interface TestReportCreateRequest {
  title: string
  test_type: 'functional' | 'performance' | 'security' | 'integration' | 'unit'
  agent_id?: number
  project_id?: number
  test_case_ids: number[]
}

// 测试报告响应
export interface TestReportResponse {
  success: boolean
  message: string
  data: TestReportInfo
}

// 测试报告列表响应
export interface TestReportListResponse {
  success: boolean
  message: string
  data: {
    test_reports: TestReportInfo[]
    total: number
    page: number
    page_size: number
  }
}

// 测试报告统计响应
export interface TestReportStatisticsResponse {
  success: boolean
  message: string
  data: {
    total_reports: number
    completed_reports: number
    running_reports: number
    overall_success_rate: number
    avg_execution_time: number
    trend_data: Array<{
      date: string
      total: number
      passed: number
      failed: number
    }>
  }
}
