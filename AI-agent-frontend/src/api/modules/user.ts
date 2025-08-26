/**
 * 用户管理相关API接口
 */
import http from '@/api/http'
import type { 
  UserInfo,
  UserCreateRequest,
  UserUpdateRequest,
  PasswordChangeRequest,
  UserRoleAssignRequest,
  PageQuery,
  PageData,
  ApiResponse 
} from '@/api/types'

/**
 * 用户管理API接口类
 */
export class UserApi {
  /**
   * 获取用户列表（分页）
   * @param params 查询参数
   * @returns 用户列表
   */
  static async getUserList(params?: PageQuery & {
    dept_id?: number
    status?: '0' | '1'
    keyword?: string
  }): Promise<ApiResponse<PageData<UserInfo>>> {
    const requestBody = {
      page: params?.page || 1,
      size: params?.size || 20,
      dept_id: params?.dept_id,
      status: params?.status,
      username: params?.keyword
    }
    return http.post<PageData<UserInfo>>('/users/get-user-list', requestBody)
  }

  /**
   * 获取所有用户列表（不分页）
   * @returns 用户列表
   */
  static async getAllUsers(): Promise<ApiResponse<UserInfo[]>> {
    return http.get<UserInfo[]>('/users/all')
  }

  /**
   * 根据ID获取用户详情
   * @param userId 用户ID
   * @returns 用户详情
   */
  static async getUserById(userId: number): Promise<ApiResponse<UserInfo>> {
    return http.post<UserInfo>('/users/get-user-info', { user_id: userId })
  }

  /**
   * 创建新用户
   * @param data 用户数据
   * @returns 创建结果
   */
  static async createUser(data: UserCreateRequest): Promise<ApiResponse<UserInfo>> {
    return http.post<UserInfo>('/users/create-user', data)
  }

  /**
   * 更新用户信息
   * @param userId 用户ID
   * @param data 更新数据
   * @returns 更新结果
   */
  static async updateUser(userId: number, data: UserUpdateRequest): Promise<ApiResponse<UserInfo>> {
    const requestBody = { user_id: userId, ...data }
    return http.post<UserInfo>('/users/update-user', requestBody)
  }

  /**
   * 删除用户
   * @param userId 用户ID
   * @returns 删除结果
   */
  static async deleteUser(userId: number): Promise<ApiResponse<boolean>> {
    return http.post<boolean>('/users/delete', { user_id: userId })
  }

  /**
   * 批量删除用户
   * @param userIds 用户ID数组
   * @returns 删除结果
   */
  static async batchDeleteUsers(userIds: number[]): Promise<ApiResponse<boolean>> {
    return http.post<boolean>('/users/batch-delete', { user_ids: userIds })
  }

  /**
   * 修改用户密码
   * @param userId 用户ID
   * @param data 密码数据
   * @returns 修改结果
   */
  static async changePassword(userId: number, data: PasswordChangeRequest): Promise<ApiResponse<boolean>> {
    return http.put<boolean>(`/users/${userId}/password`, data)
  }

  /**
   * 重置用户密码
   * @param userId 用户ID
   * @param newPassword 新密码
   * @returns 重置结果
   */
  static async resetPassword(userId: number, newPassword: string): Promise<ApiResponse<boolean>> {
    return http.post<boolean>(`/users/${userId}/reset-password`, { new_password: newPassword })
  }

  /**
   * 启用/禁用用户
   * @param userId 用户ID
   * @param status 状态 '0':启用 '1':禁用
   * @returns 操作结果
   */
  static async toggleUserStatus(userId: number, status: '0' | '1'): Promise<ApiResponse<boolean>> {
    return http.put<boolean>(`/users/${userId}/status`, { status })
  }

  /**
   * 获取用户角色列表
   * @param userId 用户ID
   * @returns 角色列表
   */
  static async getUserRoles(userId: number): Promise<ApiResponse<any[]>> {
    return http.get<any[]>(`/users/${userId}/roles`)
  }

  /**
   * 分配用户角色
   * @param userId 用户ID
   * @param data 角色分配数据
   * @returns 分配结果
   */
  static async assignUserRoles(userId: number, data: UserRoleAssignRequest): Promise<ApiResponse<boolean>> {
    return http.post<boolean>(`/users/${userId}/roles`, data)
  }

  /**
   * 获取用户权限列表
   * @param userId 用户ID
   * @returns 权限列表
   */
  static async getUserPermissions(userId: number): Promise<ApiResponse<string[]>> {
    return http.get<string[]>(`/users/${userId}/permissions`)
  }

  /**
   * 获取用户菜单树
   * @param userId 用户ID
   * @returns 菜单树
   */
  static async getUserMenus(userId: number): Promise<ApiResponse<any[]>> {
    return http.get<any[]>(`/users/${userId}/menus`)
  }

  /**
   * 导出用户数据
   * @param params 查询参数
   * @returns 文件下载
   */
  static async exportUsers(params?: any): Promise<void> {
    const response = await http.get('/users/export', params)
    // 处理文件下载
    // 实际实现中需要根据响应处理文件下载
  }

  /**
   * 导入用户数据
   * @param file 上传的文件
   * @returns 导入结果
   */
  static async importUsers(file: File): Promise<ApiResponse<any>> {
    const formData = new FormData()
    formData.append('file', file)
    return http.upload<any>('/users/import', formData)
  }

  /**
   * 检查用户名是否可用
   * @param username 用户名
   * @param excludeUserId 排除的用户ID（编辑时使用）
   * @returns 检查结果
   */
  static async checkUsername(username: string, excludeUserId?: number): Promise<ApiResponse<boolean>> {
    const params = excludeUserId ? { username, exclude_user_id: excludeUserId } : { username }
    return http.get<boolean>('/users/check-username', params)
  }

  /**
   * 检查邮箱是否可用
   * @param email 邮箱
   * @param excludeUserId 排除的用户ID（编辑时使用）
   * @returns 检查结果
   */
  static async checkEmail(email: string, excludeUserId?: number): Promise<ApiResponse<boolean>> {
    const params = excludeUserId ? { email, exclude_user_id: excludeUserId } : { email }
    return http.get<boolean>('/users/check-email', params)
  }

  /**
   * 获取用户统计信息
   * @returns 统计信息
   */
  static async getUserStats(): Promise<ApiResponse<{
    total: number
    active: number
    inactive: number
    today_register: number
  }>> {
    return http.get('/users/stats')
  }
}

// 导出单个方法，保持兼容性
export const userApi = {
  getUserList: UserApi.getUserList,
  getAllUsers: UserApi.getAllUsers,
  getUserById: UserApi.getUserById,
  createUser: UserApi.createUser,
  updateUser: UserApi.updateUser,
  deleteUser: UserApi.deleteUser,
  batchDeleteUsers: UserApi.batchDeleteUsers,
  changePassword: UserApi.changePassword,
  resetPassword: UserApi.resetPassword,
  toggleUserStatus: UserApi.toggleUserStatus,
  getUserRoles: UserApi.getUserRoles,
  assignUserRoles: UserApi.assignUserRoles,
  getUserPermissions: UserApi.getUserPermissions,
  getUserMenus: UserApi.getUserMenus,
  exportUsers: UserApi.exportUsers,
  importUsers: UserApi.importUsers,
  checkUsername: UserApi.checkUsername,
  checkEmail: UserApi.checkEmail,
  getUserStats: UserApi.getUserStats
}