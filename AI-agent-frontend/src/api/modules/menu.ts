/**
 * 菜单管理相关API接口
 */
import http from '@/api/http'
import type {
  MenuInfo,
  MenuTreeNode,
  MenuCreateRequest,
  MenuUpdateRequest,
  ApiResponse,
  UserMenuTreeResponse
} from '@/api/types'

/**
 * 菜单管理API接口类
 */
export class MenuApi {
  /**
   * 获取菜单列表
   * @returns 菜单列表
   */
  static async getMenuList(): Promise<ApiResponse<MenuInfo[]>> {
    return http.post<MenuInfo[]>('/menus/get-menu-list')
  }

  /**
   * 获取菜单树
   * @param params 搜索参数
   * @returns 菜单树
   */
  static async getMenuTree(params?: { keyword?: string; is_active?: boolean }): Promise<ApiResponse<MenuTreeNode[]>> {
    return http.post<MenuTreeNode[]>('/menus/get-menu-tree', params || {})
  }

  /**
   * 根据ID获取菜单详情
   * @param menuId 菜单ID
   * @returns 菜单详情
   */
  static async getMenuById(menuId: number): Promise<ApiResponse<MenuInfo>> {
    return http.post<MenuInfo>('/menus/get-menu-info', { menu_id: menuId })
  }

  /**
   * 创建新菜单
   * @param data 菜单数据
   * @returns 创建结果
   */
  static async createMenu(data: MenuCreateRequest): Promise<ApiResponse<MenuInfo>> {
    return http.post<MenuInfo>('/menus/create-menu', data)
  }

  /**
   * 更新菜单信息
   * @param menuId 菜单ID
   * @param data 更新数据
   * @returns 更新结果
   */
  static async updateMenu(menuId: number, data: MenuUpdateRequest): Promise<ApiResponse<MenuInfo>> {
    return http.post<MenuInfo>('/menus/update-menu', { menu_id: menuId, ...data })
  }

  /**
   * 删除菜单
   * @param menuId 菜单ID
   * @returns 删除结果
   */
  static async deleteMenu(menuId: number): Promise<ApiResponse<boolean>> {
    return http.post<boolean>('/menus/delete-menu', { menu_id: menuId })
  }

  /**
   * 获取用户菜单树
   * @param userId 用户ID
   * @returns 用户菜单树
   */
  static async getUserMenuTree(userId: number): Promise<ApiResponse<MenuTreeNode[]>> {
    return http.post<MenuTreeNode[]>('/menus/get-user-menus', { user_id: userId })
  }

  /**
   * 获取角色菜单树
   * @param roleId 角色ID
   * @returns 角色菜单树
   */
  static async getRoleMenuTree(roleId: number): Promise<ApiResponse<MenuTreeNode[]>> {
    return http.get<MenuTreeNode[]>(`/menus/role/${roleId}`)
  }

  /**
   * 更新菜单排序
   * @param menuId 菜单ID
   * @param orderNum 排序号
   * @returns 更新结果
   */
  static async updateMenuOrder(menuId: number, orderNum: number): Promise<ApiResponse<boolean>> {
    return http.put<boolean>(`/menus/${menuId}/order`, { order_num: orderNum })
  }

  /**
   * 批量更新菜单排序
   * @param orders 排序数据数组
   * @returns 更新结果
   */
  static async batchUpdateMenuOrder(orders: Array<{ menu_id: number; order_num: number }>): Promise<ApiResponse<boolean>> {
    return http.post<boolean>('/menus/batch-order', { orders })
  }

  /**
   * 检查菜单名称是否可用
   * @param menuName 菜单名称
   * @param parentId 父菜单ID
   * @param excludeMenuId 排除的菜单ID（编辑时使用）
   * @returns 检查结果
   */
  static async checkMenuName(menuName: string, parentId: number, excludeMenuId?: number): Promise<ApiResponse<boolean>> {
    const params = {
      MENU_NAME: menuName,
      PARENT_ID: parentId,
      ...(excludeMenuId && { EXCLUDE_MENU_ID: excludeMenuId })
    }
    return http.get<boolean>('/menus/check-name', params)
  }

  /**
   * 检查权限标识是否可用
   * @param perms 权限标识
   * @param excludeMenuId 排除的菜单ID（编辑时使用）
   * @returns 检查结果
   */
  static async checkPerms(perms: string, excludeMenuId?: number): Promise<ApiResponse<boolean>> {
    const params = excludeMenuId ? { PERMS: perms, EXCLUDE_MENU_ID: excludeMenuId } : { PERMS: perms }
    return http.get<boolean>('/menus/check-perms', params)
  }

  /**
   * 获取菜单统计信息
   * @returns 统计信息
   */
  static async getMenuStats(): Promise<ApiResponse<{
    total: number
    menu_count: number
    button_count: number
    max_level: number
  }>> {
    return http.get('/menus/stats')
  }

  /**
   * 获取用户动态路由
   * @returns 用户路由树
   */
  static async getUserRoutes(): Promise<ApiResponse<UserMenuTreeResponse>> {
    return http.post<UserMenuTreeResponse>('/menus/get-user-routes')
  }
}

// 导出单个方法，保持兼容性
export const menuApi = {
  getMenuList: MenuApi.getMenuList,
  getMenuTree: MenuApi.getMenuTree,
  getMenuById: MenuApi.getMenuById,
  createMenu: MenuApi.createMenu,
  updateMenu: MenuApi.updateMenu,
  deleteMenu: MenuApi.deleteMenu,
  getUserMenuTree: MenuApi.getUserMenuTree,
  getRoleMenuTree: MenuApi.getRoleMenuTree,
  updateMenuOrder: MenuApi.updateMenuOrder,
  batchUpdateMenuOrder: MenuApi.batchUpdateMenuOrder,
  checkMenuName: MenuApi.checkMenuName,
  checkPerms: MenuApi.checkPerms,
  getMenuStats: MenuApi.getMenuStats,
  getUserRoutes: MenuApi.getUserRoutes
}