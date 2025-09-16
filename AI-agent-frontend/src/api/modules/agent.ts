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
    return http.post<AgentResponse>('/agents/', data)
  },

  /**
   * 获取代理详情
   */
  getAgent(id: number) {
    return http.get<AgentResponse>(`/agents/${id}`)
  },

  /**
   * 更新代理信息
   */
  updateAgent(id: number, data: AgentUpdateRequest) {
    return http.put<AgentResponse>(`/agents/${id}`, data)
  },

  /**
   * 删除代理
   */
  deleteAgent(id: number) {
    return http.delete(`/agents/${id}`)
  },

  /**
   * 搜索代理
   */
  searchAgents(params: AgentSearchRequest) {
    return http.post<AgentListResponse>('/agents/search', params)
  },

  /**
   * 获取代理列表
   */
  getAgentList(params: { page?: number; page_size?: number } = {}) {
    return http.get<AgentListResponse>('/agents/', { params })
  },

  /**
   * 获取代理统计信息
   */
  getStatistics() {
    return http.get<AgentStatisticsResponse>('/agents/statistics/overview')
  },

  /**
   * 启动代理
   */
  startAgent(id: number) {
    return http.post<AgentResponse>(`/agents/${id}/start`)
  },

  /**
   * 停止代理
   */
  stopAgent(id: number) {
    return http.post<AgentResponse>(`/agents/${id}/stop`)
  },

  /**
   * 更新代理状态
   */
  updateAgentStatus(id: number, status: string) {
    return http.post<AgentResponse>(`/agents/${id}/status`, { status })
  },

  /**
   * 批量操作代理
   */
  batchOperation(data: AgentBatchOperationRequest) {
    return http.post<AgentBatchOperationResponse>('/agents/batch', data)
  }
}