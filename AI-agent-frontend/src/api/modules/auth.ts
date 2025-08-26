/**
 * 用户认证相关API接口
 */
import http from '@/api/http'
import type { 
  LoginRequest, 
  LoginResponse, 
  UserInfo,
  ApiResponse 
} from '@/api/types'

/**
 * 认证API接口类
 */
export class AuthApi {
  /**
   * 用户登录
   * @param data 登录参数
   * @returns 登录响应数据
   */
  static async login(data: LoginRequest): Promise<ApiResponse<LoginResponse>> {
    return http.post<LoginResponse>('/users/login', data)
  }

  /**
   * 获取当前用户信息
   * @returns 用户信息
   */
  static async getCurrentUser(userId: number): Promise<ApiResponse<UserInfo>> {
    return http.post<UserInfo>('/users/get-user-info', { user_id: userId })
  }

  /**
   * 获取用户权限列表
   * @param userId 用户ID
   * @returns 权限列表
   */
  static async getUserPermissions(userId: number): Promise<ApiResponse<string[]>> {
    const res = await http.get<{ menus: any[]; permissions: string[] }>(`/menus/user/${userId}`)
    if ((res as any)?.success) {
      const data = (res as any).data
      return { ...(res as any), data: data?.permissions || [] }
    }
    return res as any
  }

  /**
   * 获取用户菜单列表
   * @param userId 用户ID
   * @returns 菜单列表
   */
  static async getUserMenus(userId: number): Promise<ApiResponse<any[]>> {
    const res = await http.get<{ menus: any[]; permissions: string[] }>(`/menus/user/${userId}`)
    if ((res as any)?.success) {
      const data = (res as any).data
      return { ...(res as any), data: data?.menus || [] }
    }
    return res as any
  }

  /**
   * 刷新token
   * @returns 新的token信息
   */
  static async refreshToken(): Promise<ApiResponse<{ access_token: string; token_type: string }>> {
    return http.post('/users/refresh-token')
  }

  /**
   * 用户退出登录
   * @returns 操作结果
   */
  static async logout(): Promise<ApiResponse<boolean>> {
    return http.post<boolean>('/users/logout')
  }
}

// 导出单个方法，保持兼容性
export const authApi = {
  login: AuthApi.login,
  getCurrentUser: AuthApi.getCurrentUser,
  getUserPermissions: AuthApi.getUserPermissions,
  getUserMenus: AuthApi.getUserMenus,
  refreshToken: AuthApi.refreshToken,
  logout: AuthApi.logout,
}