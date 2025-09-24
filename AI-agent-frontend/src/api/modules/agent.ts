// AI代理管理相关API
import { http } from '@/api/http'
import type { ApiResponse } from '@/api/types'

// 代理信息接口
export interface AgentInfo {
  id: number
  name: string
  type: 'chat' | 'task' | 'analysis' | 'testing' | 'custom'
  status: 'inactive' | 'active' | 'running' | 'stopped' | 'error' | 'maintenance'
  version: string
  description?: string
  config?: Record<string, any>
  run_count: number
  success_rate: number
  created_at: string
  updated_at: string
  created_by_id: number
  creator_name?: string
}

// 代理统计信息接口
export interface AgentStatistics {
  total_agents: number
  active_agents: number
  running_agents: number
  stopped_agents: number
  error_agents: number
  overall_success_rate: number
  total_runs: number
  success_runs: number
}

// 代理搜索参数接口
export interface AgentSearchParams {
  page?: number
  page_size?: number
  keyword?: string
  type?: string
  status?: string
  created_by_id?: number
  order_by?: string
  order_desc?: boolean
}

// 代理搜索结果接口
export interface AgentSearchResult {
  agents: AgentInfo[]
  total: number
  page: number
  page_size: number
}

// 代理创建请求接口
export interface AgentCreateRequest {
  name: string
  type: string
  version: string
  description?: string
  config?: Record<string, any>
}

// 代理更新请求接口
export interface AgentUpdateRequest {
  name?: string
  type?: string
  version?: string
  description?: string
  config?: Record<string, any>
  status?: string
}

// 批量操作请求接口
export interface AgentBatchOperationRequest {
  agent_ids: number[]
  operation: 'activate' | 'deactivate' | 'delete' | 'start' | 'stop'
}

// 批量操作结果接口
export interface AgentBatchOperationResult {
  total: number
  success_count: number
  failed_count: number
  failed_agents?: Array<{ id: number; name: string; error: string }>
}

// 代理运行日志接口
export interface AgentRunLog {
  id: number
  agent_id: number
  start_time: string
  end_time?: string
  status: 'running' | 'completed' | 'failed' | 'stopped'
  input_data?: Record<string, any>
  output_data?: Record<string, any>
  error_message?: string
  execution_time?: number
  tokens_used?: number
  cost?: number
}

// 代理配置详情接口
export interface AgentConfigDetail {
  id: number
  agent_id: number
  config_name: string
  config_version: string
  config_data: Record<string, any>
  is_active: boolean
  created_at: string
  updated_at: string
}

export const agentApi = {
  /**
   * 获取代理统计信息
   */
  getStatistics(): Promise<ApiResponse<AgentStatistics>> {
    return http.get('/agents/statistics')
  },

  /**
   * 搜索代理列表
   */
  searchAgents(params: AgentSearchParams): Promise<ApiResponse<AgentSearchResult>> {
    return http.get('/agents/search', { params })
  },

  /**
   * 获取代理详情
   */
  getAgentDetail(agentId: number): Promise<ApiResponse<AgentInfo>> {
    return http.get(`/agents/${agentId}`)
  },

  /**
   * 创建代理
   */
  createAgent(data: AgentCreateRequest): Promise<ApiResponse<AgentInfo>> {
    return http.post('/agents', data)
  },

  /**
   * 更新代理
   */
  updateAgent(agentId: number, data: AgentUpdateRequest): Promise<ApiResponse<AgentInfo>> {
    return http.put(`/agents/${agentId}`, data)
  },

  /**
   * 删除代理
   */
  deleteAgent(agentId: number): Promise<ApiResponse<void>> {
    return http.delete(`/agents/${agentId}`)
  },

  /**
   * 启动代理
   */
  startAgent(agentId: number, params?: Record<string, any>): Promise<ApiResponse<{ run_id: number }>> {
    return http.post(`/agents/${agentId}/start`, params || {})
  },

  /**
   * 停止代理
   */
  stopAgent(agentId: number): Promise<ApiResponse<void>> {
    return http.post(`/agents/${agentId}/stop`)
  },

  /**
   * 重启代理
   */
  restartAgent(agentId: number): Promise<ApiResponse<{ run_id: number }>> {
    return http.post(`/agents/${agentId}/restart`)
  },

  /**
   * 激活代理
   */
  activateAgent(agentId: number): Promise<ApiResponse<void>> {
    return http.post(`/agents/${agentId}/activate`)
  },

  /**
   * 停用代理
   */
  deactivateAgent(agentId: number): Promise<ApiResponse<void>> {
    return http.post(`/agents/${agentId}/deactivate`)
  },

  /**
   * 批量操作代理
   */
  batchOperation(data: AgentBatchOperationRequest): Promise<ApiResponse<AgentBatchOperationResult>> {
    return http.post('/agents/batch-operation', data)
  },

  /**
   * 获取代理运行日志
   */
  getAgentRunLogs(agentId: number, params?: {
    page?: number
    page_size?: number
    status?: string
    start_time?: string
    end_time?: string
  }): Promise<ApiResponse<{ logs: AgentRunLog[]; total: number }>> {
    return http.get(`/agents/${agentId}/logs`, { params })
  },

  /**
   * 获取代理运行详情
   */
  getAgentRunDetail(agentId: number, runId: number): Promise<ApiResponse<AgentRunLog>> {
    return http.get(`/agents/${agentId}/runs/${runId}`)
  },

  /**
   * 获取代理配置列表
   */
  getAgentConfigs(agentId: number): Promise<ApiResponse<AgentConfigDetail[]>> {
    return http.get(`/agents/${agentId}/configs`)
  },

  /**
   * 创建代理配置
   */
  createAgentConfig(agentId: number, data: {
    config_name: string
    config_version: string
    config_data: Record<string, any>
  }): Promise<ApiResponse<AgentConfigDetail>> {
    return http.post(`/agents/${agentId}/configs`, data)
  },

  /**
   * 更新代理配置
   */
  updateAgentConfig(agentId: number, configId: number, data: {
    config_name?: string
    config_version?: string
    config_data?: Record<string, any>
    is_active?: boolean
  }): Promise<ApiResponse<AgentConfigDetail>> {
    return http.put(`/agents/${agentId}/configs/${configId}`, data)
  },

  /**
   * 删除代理配置
   */
  deleteAgentConfig(agentId: number, configId: number): Promise<ApiResponse<void>> {
    return http.delete(`/agents/${agentId}/configs/${configId}`)
  },

  /**
   * 应用代理配置
   */
  applyAgentConfig(agentId: number, configId: number): Promise<ApiResponse<void>> {
    return http.post(`/agents/${agentId}/configs/${configId}/apply`)
  },

  /**
   * 测试代理连接
   */
  testAgentConnection(agentId: number, testData?: Record<string, any>): Promise<ApiResponse<{
    success: boolean
    response_time: number
    test_result: any
    error_message?: string
  }>> {
    return http.post(`/agents/${agentId}/test`, testData || {})
  },

  /**
   * 获取代理性能指标
   */
  getAgentMetrics(agentId: number, timeRange?: {
    start_time: string
    end_time: string
  }): Promise<ApiResponse<{
    avg_response_time: number
    success_rate: number
    total_runs: number
    error_count: number
    cost_stats: {
      total_cost: number
      avg_cost: number
      total_tokens: number
    }
    time_series: Array<{
      timestamp: string
      response_time: number
      success_count: number
      error_count: number
      cost: number
    }>
  }>> {
    return http.get(`/agents/${agentId}/metrics`, { params: timeRange })
  },

  /**
   * 导出代理配置
   */
  exportAgentConfig(agentId: number): Promise<Blob> {
    return http.get(`/agents/${agentId}/export`, { responseType: 'blob' })
  },

  /**
   * 导入代理配置
   */
  importAgentConfig(file: File): Promise<ApiResponse<AgentInfo>> {
    const formData = new FormData()
    formData.append('config_file', file)
    return http.post('/agents/import', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },

  /**
   * 克隆代理
   */
  cloneAgent(agentId: number, data: {
    name: string
    description?: string
  }): Promise<ApiResponse<AgentInfo>> {
    return http.post(`/agents/${agentId}/clone`, data)
  }
}

// 代理工具类
export const agentUtils = {
  /**
   * 格式化代理状态
   */
  formatStatus(status: string): { text: string; type: string; color: string } {
    const statusMap = {
      inactive: { text: '未激活', type: 'info', color: '#909399' },
      active: { text: '激活', type: 'success', color: '#67c23a' },
      running: { text: '运行中', type: 'primary', color: '#409eff' },
      stopped: { text: '已停止', type: 'warning', color: '#e6a23c' },
      error: { text: '错误', type: 'danger', color: '#f56c6c' },
      maintenance: { text: '维护中', type: 'warning', color: '#e6a23c' }
    }
    return statusMap[status as keyof typeof statusMap] || statusMap.inactive
  },

  /**
   * 格式化代理类型
   */
  formatType(type: string): { text: string; icon: string; color: string } {
    const typeMap = {
      chat: { text: '聊天代理', icon: 'ChatDotRound', color: '#409eff' },
      task: { text: '任务代理', icon: 'Operation', color: '#67c23a' },
      analysis: { text: '分析代理', icon: 'TrendCharts', color: '#e6a23c' },
      testing: { text: '测试代理', icon: 'TestTube', color: '#f56c6c' },
      custom: { text: '自定义', icon: 'Setting', color: '#909399' }
    }
    return typeMap[type as keyof typeof typeMap] || typeMap.custom
  },

  /**
   * 计算运行时长
   */
  calculateRuntime(startTime: string, endTime?: string): string {
    const start = new Date(startTime)
    const end = endTime ? new Date(endTime) : new Date()
    const diff = end.getTime() - start.getTime()
    
    if (diff < 1000) {
      return `${diff}ms`
    } else if (diff < 60000) {
      return `${Math.floor(diff / 1000)}s`
    } else if (diff < 3600000) {
      return `${Math.floor(diff / 60000)}m ${Math.floor((diff % 60000) / 1000)}s`
    } else {
      const hours = Math.floor(diff / 3600000)
      const minutes = Math.floor((diff % 3600000) / 60000)
      return `${hours}h ${minutes}m`
    }
  },

  /**
   * 格式化成本
   */
  formatCost(cost: number): string {
    if (cost < 0.01) {
      return `¥${(cost * 100).toFixed(4)}分`
    } else if (cost < 1) {
      return `¥${(cost * 100).toFixed(2)}分`
    } else {
      return `¥${cost.toFixed(2)}`
    }
  },

  /**
   * 生成代理头像URL
   */
  getAgentAvatar(type: string, id: number): string {
    const colors = ['#409eff', '#67c23a', '#e6a23c', '#f56c6c', '#909399']
    const color = colors[id % colors.length]
    const typeMap = {
      chat: '💬',
      task: '⚙️',
      analysis: '📊',
      testing: '🧪',
      custom: '🔧'
    }
    const emoji = typeMap[type as keyof typeof typeMap] || '🤖'
    
    // 可以返回一个基于emoji和颜色的头像URL，或者使用默认头像
    return `data:image/svg+xml;base64,${btoa(`
      <svg width="32" height="32" viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg">
        <circle cx="16" cy="16" r="16" fill="${color}"/>
        <text x="16" y="20" text-anchor="middle" font-size="14" fill="white">${emoji}</text>
      </svg>
    `)}`
  },

  /**
   * 验证代理配置
   */
  validateConfig(config: Record<string, any>, type: string): { valid: boolean; errors: string[] } {
    const errors: string[] = []
    
    // 基础验证
    if (!config || typeof config !== 'object') {
      errors.push('配置必须是有效的JSON对象')
      return { valid: false, errors }
    }
    
    // 根据类型进行特定验证
    switch (type) {
      case 'chat':
        if (!config.large_model_id) {
          errors.push('聊天代理必须指定large_model_id')
        }
        if (config.temperature && (config.temperature < 0 || config.temperature > 2)) {
          errors.push('temperature参数必须在0-2之间')
        }
        break
      case 'task':
        if (!config.task_type) {
          errors.push('任务代理必须指定task_type')
        }
        break
      case 'analysis':
        if (!config.analysis_type) {
          errors.push('分析代理必须指定analysis_type')
        }
        break
      case 'testing':
        if (!config.test_framework) {
          errors.push('测试代理必须指定test_framework')
        }
        break
    }
    
    return { valid: errors.length === 0, errors }
  }
}

export default agentApi