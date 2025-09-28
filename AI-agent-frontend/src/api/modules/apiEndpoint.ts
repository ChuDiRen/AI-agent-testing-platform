/**
 * API端点管理接口
 */

import http from '@/api/http'

// API端点相关接口类型定义
export interface ApiEndpoint {
  id: number
  path: string
  method: string
  name: string
  description?: string
  status: string
  module?: string
  permission?: string
  version: string
  request_example?: Record<string, any>
  response_example?: Record<string, any>
  total_calls: number
  success_calls: number
  error_calls: number
  success_rate: number
  avg_response_time: number
  max_response_time: number
  min_response_time: number
  last_called_at?: string
  created_at?: string
  updated_at?: string
  created_by_id: number
}

export interface ApiEndpointCreateRequest {
  path: string
  method: string
  name: string
  description?: string
  module?: string
  permission?: string
  version?: string
  request_example?: Record<string, any>
  response_example?: Record<string, any>
}

export interface ApiEndpointUpdateRequest {
  name?: string
  description?: string
  status?: string
  module?: string
  permission?: string
  version?: string
  request_example?: Record<string, any>
  response_example?: Record<string, any>
}

export interface ApiEndpointQueryParams {
  page?: number
  size?: number
  keyword?: string
  method?: string
  status?: string
  module?: string
  permission?: string
}

export interface ApiEndpointListResponse {
  items: ApiEndpoint[]
  total: number
  page: number
  size: number
  pages: number
}

export interface ApiStatistics {
  total_apis: number
  active_apis: number
  deprecated_apis: number
  maintenance_apis: number
  total_calls_today: number
  success_calls_today: number
  error_calls_today: number
  avg_response_time: number
  top_apis: Array<{
    name: string
    path: string
    calls: number
  }>
  error_apis: Array<{
    name: string
    path: string
    error_rate: number
  }>
}

export interface ApiCallLog {
  id: number
  api_id: number
  api_path: string
  method: string
  status_code: number
  response_time: number
  user_id?: number
  ip_address: string
  user_agent?: string
  request_data?: Record<string, any>
  response_data?: Record<string, any>
  error_message?: string
  created_at: string
}

/**
 * API端点管理API类
 */
export class ApiEndpointApi {
  /**
   * 创建API端点
   */
  static async createApiEndpoint(data: ApiEndpointCreateRequest) {
    return http.post<ApiEndpoint>('/api/v1/api-endpoints/', data)
  }

  /**
   * 更新API端点
   */
  static async updateApiEndpoint(id: number, data: ApiEndpointUpdateRequest) {
    return http.put<ApiEndpoint>(`/api/v1/api-endpoints/${id}`, data)
  }

  /**
   * 删除API端点
   */
  static async deleteApiEndpoint(id: number) {
    return http.delete<boolean>(`/api/v1/api-endpoints/${id}`)
  }

  /**
   * 获取API端点详情
   */
  static async getApiEndpoint(id: number) {
    return http.get<ApiEndpoint>(`/api/v1/api-endpoints/${id}`)
  }

  /**
   * 获取API端点列表
   */
  static async getApiEndpoints(params?: ApiEndpointQueryParams) {
    return http.get<ApiEndpointListResponse>('/api/v1/api-endpoints/', { params })
  }

  /**
   * 获取API统计数据
   */
  static async getApiStatistics() {
    return http.get<ApiStatistics>('/api/v1/api-endpoints/statistics/overview')
  }

  /**
   * 获取所有模块列表
   */
  static async getModules() {
    return http.get<string[]>('/api/v1/api-endpoints/metadata/modules')
  }

  /**
   * 获取所有权限列表
   */
  static async getPermissions() {
    return http.get<string[]>('/api/v1/api-endpoints/metadata/permissions')
  }

  /**
   * 获取所有HTTP方法列表
   */
  static async getMethods() {
    return http.get<string[]>('/api/v1/api-endpoints/metadata/methods')
  }

  /**
   * 批量更新API状态
   */
  static async batchUpdateStatus(apiIds: number[], status: string) {
    return http.post<number>('/api/v1/api-endpoints/batch/status', {
      api_ids: apiIds,
      status
    })
  }

  /**
   * 从路由同步API端点
   */
  static async syncApiEndpoints() {
    return http.post<{
      total_scanned: number
      new_created: number
      updated: number
      skipped: number
    }>('/api/v1/api-endpoints/sync')
  }

  /**
   * 获取API调用日志
   */
  static async getApiCallLogs(params?: {
    page?: number
    size?: number
    api_id?: number
    start_date?: string
    end_date?: string
  }) {
    return http.get<{
      items: ApiCallLog[]
      total: number
      page: number
      size: number
      pages: number
    }>('/api/v1/api-endpoints/logs', { params })
  }
}

// 导出单个方法，保持兼容性
export const apiEndpointApi = {
  createApiEndpoint: ApiEndpointApi.createApiEndpoint,
  updateApiEndpoint: ApiEndpointApi.updateApiEndpoint,
  deleteApiEndpoint: ApiEndpointApi.deleteApiEndpoint,
  getApiEndpoint: ApiEndpointApi.getApiEndpoint,
  getApiEndpoints: ApiEndpointApi.getApiEndpoints,
  getApiStatistics: ApiEndpointApi.getApiStatistics,
  getModules: ApiEndpointApi.getModules,
  getPermissions: ApiEndpointApi.getPermissions,
  getMethods: ApiEndpointApi.getMethods,
  batchUpdateStatus: ApiEndpointApi.batchUpdateStatus,
  syncApiEndpoints: ApiEndpointApi.syncApiEndpoints,
  getApiCallLogs: ApiEndpointApi.getApiCallLogs
}

// 默认导出
export default ApiEndpointApi

// API状态常量
export const API_STATUS = {
  ACTIVE: 'active',
  INACTIVE: 'inactive',
  DEPRECATED: 'deprecated',
  MAINTENANCE: 'maintenance'
} as const

// API状态标签映射
export const API_STATUS_LABELS = {
  [API_STATUS.ACTIVE]: '激活',
  [API_STATUS.INACTIVE]: '未激活',
  [API_STATUS.DEPRECATED]: '已废弃',
  [API_STATUS.MAINTENANCE]: '维护中'
} as const

// HTTP方法常量
export const HTTP_METHODS = {
  GET: 'GET',
  POST: 'POST',
  PUT: 'PUT',
  DELETE: 'DELETE',
  PATCH: 'PATCH',
  HEAD: 'HEAD',
  OPTIONS: 'OPTIONS'
} as const

// HTTP方法颜色映射
export const HTTP_METHOD_COLORS = {
  [HTTP_METHODS.GET]: 'success',
  [HTTP_METHODS.POST]: 'primary',
  [HTTP_METHODS.PUT]: 'warning',
  [HTTP_METHODS.DELETE]: 'danger',
  [HTTP_METHODS.PATCH]: 'info',
  [HTTP_METHODS.HEAD]: 'secondary',
  [HTTP_METHODS.OPTIONS]: 'secondary'
} as const
