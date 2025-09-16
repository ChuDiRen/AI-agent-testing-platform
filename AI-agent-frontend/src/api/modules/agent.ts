// AI代理管理API
import { http } from '@/api/http'
import type { 
  AgentCreateRequest, 
  AgentUpdateRequest, 
  AgentSearchRequest,
  AgentResponse,
  AgentListResponse,
  AgentStatisticsResponse,
  AgentBatchOperationRequest,
  AgentBatchOperationResponse
} from '../types'

export const agentApi = {
  /**
   * 创建AI代理
   */
  createAgent(data: AgentCreateRequest) {
    return http.post<AgentResponse>('/api/v1/agents/', data)
  },

  /**
   * 获取代理详情
   */
  getAgent(id: number) {
    return http.get<AgentResponse>(`/api/v1/agents/${id}`)
  },

  /**
   * 更新代理信息
   */
  updateAgent(id: number, data: AgentUpdateRequest) {
    return http.put<AgentResponse>(`/api/v1/agents/${id}`, data)
  },

  /**
   * 删除代理
   */
  deleteAgent(id: number) {
    return http.delete(`/api/v1/agents/${id}`)
  },

  /**
   * 搜索代理
   */
  searchAgents(params: AgentSearchRequest) {
    return http.post<AgentListResponse>('/api/v1/agents/search', params)
  },

  /**
   * 获取代理列表
   */
  getAgentList(params: { page?: number; page_size?: number } = {}) {
    return http.get<AgentListResponse>('/api/v1/agents/', { params })
  },

  /**
   * 获取代理统计信息
   */
  getStatistics() {
    return http.get<AgentStatisticsResponse>('/api/v1/agents/statistics/overview')
  },

  /**
   * 启动代理
   */
  startAgent(id: number) {
    return http.post<AgentResponse>(`/api/v1/agents/${id}/start`)
  },

  /**
   * 停止代理
   */
  stopAgent(id: number) {
    return http.post<AgentResponse>(`/api/v1/agents/${id}/stop`)
  },

  /**
   * 更新代理状态
   */
  updateAgentStatus(id: number, status: string) {
    return http.post<AgentResponse>(`/api/v1/agents/${id}/status`, { status })
  },

  /**
   * 批量操作代理
   */
  batchOperation(data: AgentBatchOperationRequest) {
    return http.post<AgentBatchOperationResponse>('/api/v1/agents/batch', data)
  }
}