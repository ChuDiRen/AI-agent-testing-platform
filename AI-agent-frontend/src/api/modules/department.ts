/**
 * 部门管理相关API接口
 */
import http from '@/api/http'
import type { 
  DeptInfo,
  DeptTreeNode,
  DeptCreateRequest,
  DeptUpdateRequest,
  DeptStatusResponse,
  ApiResponse 
} from '@/api/types'

/**
 * 部门管理API接口类
 */
export class DepartmentApi {
  /**
   * 获取部门列表
   * @returns 部门列表
   */
  static async getDepartmentList(): Promise<ApiResponse<DeptInfo[]>> {
    return http.post<DeptInfo[]>('/departments/get-department-list', {})
  }

  /**
   * 获取部门树
   * @returns 部门树
   */
  static async getDepartmentTree(): Promise<ApiResponse<DeptTreeNode[]>> {
    return http.post<DeptTreeNode[]>('/departments/get-department-tree', {})
  }

  /**
   * 根据ID获取部门详情
   * @param deptId 部门ID
   * @returns 部门详情
   */
  static async getDepartmentById(deptId: number): Promise<ApiResponse<DeptInfo>> {
    return http.post<DeptInfo>('/departments/get-department-info', { dept_id: deptId })
  }

  /**
   * 创建新部门
   * @param data 部门数据
   * @returns 创建结果
   */
  static async createDepartment(data: DeptCreateRequest): Promise<ApiResponse<DeptInfo>> {
    return http.post<DeptInfo>('/departments/create-department', data)
  }

  /**
   * 更新部门信息
   * @param deptId 部门ID
   * @param data 更新数据
   * @returns 更新结果
   */
  static async updateDepartment(deptId: number, data: DeptUpdateRequest): Promise<ApiResponse<DeptInfo>> {
    const requestBody = { dept_id: deptId, ...data }
    return http.post<DeptInfo>('/departments/update-department', requestBody)
  }

  /**
   * 删除部门
   * @param deptId 部门ID
   * @returns 删除结果
   */
  static async deleteDepartment(deptId: number): Promise<ApiResponse<boolean>> {
    return http.post<boolean>('/departments/delete-department', { dept_id: deptId })
  }

  /**
   * 获取部门状态信息
   * @param deptId 部门ID
   * @returns 部门状态
   */
  static async getDepartmentStatus(deptId: number): Promise<ApiResponse<DeptStatusResponse>> {
    return http.get<DeptStatusResponse>(`/departments/${deptId}/status`)
  }

  /**
   * 获取部门用户列表
   * @param deptId 部门ID
   * @returns 用户列表
   */
  static async getDepartmentUsers(deptId: number): Promise<ApiResponse<any[]>> {
    return http.get<any[]>(`/departments/${deptId}/users`)
  }

  /**
   * 移动部门到新的父部门
   * @param deptId 部门ID
   * @param newParentId 新父部门ID
   * @returns 移动结果
   */
  static async moveDepartment(deptId: number, newParentId: number): Promise<ApiResponse<boolean>> {
    return http.put<boolean>(`/departments/${deptId}/move`, { parent_id: newParentId })
  }

  /**
   * 更新部门排序
   * @param deptId 部门ID
   * @param orderNum 排序号
   * @returns 更新结果
   */
  static async updateDepartmentOrder(deptId: number, orderNum: number): Promise<ApiResponse<boolean>> {
    return http.put<boolean>(`/departments/${deptId}/order`, { order_num: orderNum })
  }

  /**
   * 批量更新部门排序
   * @param orders 排序数据数组
   * @returns 更新结果
   */
  static async batchUpdateDepartmentOrder(orders: Array<{ dept_id: number; order_num: number }>): Promise<ApiResponse<boolean>> {
    return http.post<boolean>('/departments/batch-order', { orders })
  }

  /**
   * 检查部门名称是否可用
   * @param deptName 部门名称
   * @param parentId 父部门ID
   * @param excludeDeptId 排除的部门ID（编辑时使用）
   * @returns 检查结果
   */
  static async checkDepartmentName(deptName: string, parentId: number, excludeDeptId?: number): Promise<ApiResponse<boolean>> {
    const params = {
      dept_name: deptName,
      parent_id: parentId,
      ...(excludeDeptId && { exclude_dept_id: excludeDeptId })
    }
    return http.get<boolean>('/departments/check-name', params)
  }

  /**
   * 获取部门统计信息
   * @returns 统计信息
   */
  static async getDepartmentStats(): Promise<ApiResponse<{
    total: number
    max_level: number
    user_count: number
  }>> {
    return http.get('/departments/stats')
  }

  /**
   * 获取部门层级路径
   * @param deptId 部门ID
   * @returns 层级路径
   */
  static async getDepartmentPath(deptId: number): Promise<ApiResponse<DeptInfo[]>> {
    return http.get<DeptInfo[]>(`/departments/${deptId}/path`)
  }
}

// 导出单个方法，保持兼容性
export const departmentApi = {
  getDepartmentList: DepartmentApi.getDepartmentList,
  getDepartmentTree: DepartmentApi.getDepartmentTree,
  getDepartmentById: DepartmentApi.getDepartmentById,
  createDepartment: DepartmentApi.createDepartment,
  updateDepartment: DepartmentApi.updateDepartment,
  deleteDepartment: DepartmentApi.deleteDepartment,
  getDepartmentStatus: DepartmentApi.getDepartmentStatus,
  getDepartmentUsers: DepartmentApi.getDepartmentUsers,
  moveDepartment: DepartmentApi.moveDepartment,
  updateDepartmentOrder: DepartmentApi.updateDepartmentOrder,
  batchUpdateDepartmentOrder: DepartmentApi.batchUpdateDepartmentOrder,
  checkDepartmentName: DepartmentApi.checkDepartmentName,
  getDepartmentStats: DepartmentApi.getDepartmentStats,
  getDepartmentPath: DepartmentApi.getDepartmentPath
}