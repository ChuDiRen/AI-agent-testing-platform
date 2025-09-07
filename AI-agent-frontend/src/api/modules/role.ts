/**
 * 角色管理相关API接口
 */
import http from '@/api/http'
import type { 
  RoleInfo,
  RoleCreateRequest,
  RoleUpdateRequest,
  RoleMenuAssignRequest,
  RolePermissionResponse,
  RoleListResponse,
  PageQuery,
  ApiResponse 
} from '@/api/types'

/**
 * 角色管理API接口类
 */
export class RoleApi {
  /**
   * 获取角色列表（分页）
   * @param params 查询参数
   * @returns 角色列表
   */
  static async getRoleList(params?: PageQuery & {
    keyword?: string
  }): Promise<ApiResponse<PageData<RoleInfo>>> {
    const requestBody: any = {
      page: params?.page || 1,
      size: params?.size || 20
    }

    // 只添加有值且去除空格后不为空的参数
    if (params?.keyword && params.keyword.trim()) {
      requestBody.keyword = params.keyword.trim()
    }

    return http.post<PageData<RoleInfo>>('/roles/get-role-list', requestBody)
  }

  /**
   * 获取所有角色列表（不分页）
   * @returns 角色列表
   */
  static async getAllRoles(): Promise<ApiResponse<RoleInfo[]>> {
    const response = await http.post<PageData<RoleInfo>>('/roles/get-role-list', { page: 1, size: 100 })
    if (response.success && response.data) {
      return { ...response, data: response.data.data || [] }
    }
    return response as any
  }

  /**
   * 根据ID获取角色详情
   * @param roleId 角色ID
   * @returns 角色详情
   */
  static async getRoleById(roleId: number): Promise<ApiResponse<RoleInfo>> {
    return http.post<RoleInfo>('/roles/get-role-info', { role_id: roleId })
  }

  /**
   * 创建新角色
   * @param data 角色数据
   * @returns 创建结果
   */
  static async createRole(data: RoleCreateRequest): Promise<ApiResponse<RoleInfo>> {
    return http.post<RoleInfo>('/roles/create-role', data)
  }

  /**
   * 更新角色信息
   * @param roleId 角色ID
   * @param data 更新数据
   * @returns 更新结果
   */
  static async updateRole(roleId: number, data: RoleUpdateRequest): Promise<ApiResponse<RoleInfo>> {
    const requestBody = { role_id: roleId, ...data }
    return http.post<RoleInfo>('/roles/update-role', requestBody)
  }

  /**
   * 删除角色
   * @param roleId 角色ID
   * @returns 删除结果
   */
  static async deleteRole(roleId: number): Promise<ApiResponse<boolean>> {
    return http.post<boolean>('/roles/delete-role', { role_id: roleId })
  }

  /**
   * 批量删除角色
   * @param roleIds 角色ID数组
   * @returns 删除结果
   */
  static async batchDeleteRoles(roleIds: number[]): Promise<ApiResponse<boolean>> {
    return http.post<boolean>('/roles/batch-delete', { role_ids: roleIds })
  }

  /**
   * 获取角色权限列表
   * @param roleId 角色ID
   * @returns 权限列表
   */
  static async getRolePermissions(roleId: number): Promise<ApiResponse<RolePermissionResponse>> {
    return http.post<RolePermissionResponse>('/roles/get-role-permissions', { role_id: roleId })
  }

  /**
   * 分配角色菜单权限
   * @param roleId 角色ID
   * @param data 菜单分配数据
   * @returns 分配结果
   */
  static async assignRoleMenus(roleId: number, data: RoleMenuAssignRequest): Promise<ApiResponse<boolean>> {
    return http.post<boolean>('/roles/assign-role-menus', { role_id: roleId, ...data })
  }

  /**
   * 获取角色菜单权限
   * @param roleId 角色ID
   * @returns 菜单权限
   */
  static async getRoleMenus(roleId: number): Promise<ApiResponse<number[]>> {
    const response = await http.post<any>('/roles/get-role-permissions', { role_id: roleId })
    if (response.success && response.data) {
      return { ...response, data: response.data.menu_ids || [] }
    }
    return response as any
  }

  /**
   * 获取角色用户列表
   * @param roleId 角色ID
   * @returns 用户列表
   */
  static async getRoleUsers(roleId: number): Promise<ApiResponse<any[]>> {
    return http.get<any[]>(`/roles/${roleId}/users`)
  }

  /**
   * 检查角色名称是否可用
   * @param roleName 角色名称
   * @param excludeRoleId 排除的角色ID（编辑时使用）
   * @returns 检查结果
   */
  static async checkRoleName(roleName: string, excludeRoleId?: number): Promise<ApiResponse<boolean>> {
    const params = excludeRoleId ? { role_name: roleName, exclude_role_id: excludeRoleId } : { role_name: roleName }
    return http.get<boolean>('/roles/check-name', params)
  }

  /**
   * 获取角色统计信息
   * @returns 统计信息
   */
  static async getRoleStats(): Promise<ApiResponse<{
    total: number
    system_roles: number
    custom_roles: number
  }>> {
    return http.get('/roles/stats')
  }

  /**
   * 复制角色
   * @param roleId 源角色ID
   * @param newRoleName 新角色名称
   * @returns 复制结果
   */
  static async copyRole(roleId: number, newRoleName: string): Promise<ApiResponse<RoleInfo>> {
    return http.post<RoleInfo>(`/roles/${roleId}/copy`, { role_name: newRoleName })
  }
}

// 导出单个方法，保持兼容性
export const roleApi = {
  getRoleList: RoleApi.getRoleList,
  getAllRoles: RoleApi.getAllRoles,
  getRoleById: RoleApi.getRoleById,
  createRole: RoleApi.createRole,
  updateRole: RoleApi.updateRole,
  deleteRole: RoleApi.deleteRole,
  batchDeleteRoles: RoleApi.batchDeleteRoles,
  getRolePermissions: RoleApi.getRolePermissions,
  assignRoleMenus: RoleApi.assignRoleMenus,
  getRoleMenus: RoleApi.getRoleMenus,
  getRoleUsers: RoleApi.getRoleUsers,
  checkRoleName: RoleApi.checkRoleName,
  getRoleStats: RoleApi.getRoleStats,
  copyRole: RoleApi.copyRole
}