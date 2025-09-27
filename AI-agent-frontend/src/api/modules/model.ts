// AI模型配置相关API
import { http } from '@/api/http'
import type { ApiResponse } from '@/api/types'

// 模型信息接口
export interface ModelInfo {
  id: number
  name: string
  display_name?: string
  provider: 'openai' | 'anthropic' | 'azure' | 'google' | 'baidu' | 'alibaba' | 'tencent' | 'local' | 'custom'
  model_type: 'chat' | 'completion' | 'embedding' | 'image' | 'audio' | 'multimodal'
  status: 'active' | 'inactive' | 'maintenance' | 'deprecated'
  version?: string
  description?: string
  api_endpoint?: string
  api_key?: string
  max_tokens: number
  temperature: number
  pricing?: {
    input_price: number  // 每1000 tokens的输入价格
    output_price: number // 每1000 tokens的输出价格
    currency: string     // 货币单位
  }
  config?: Record<string, any>
  usage_count: number
  total_tokens: number
  total_cost: number
  created_at: string
  updated_at: string
  created_by_id: number
  creator_name?: string
}

// 模型统计信息接口
export interface ModelStatistics {
  total_models: number
  active_models: number
  inactive_models: number
  total_usage_count: number
  total_tokens_used: number
  total_cost: number
  provider_stats: Array<{
    provider: string
    count: number
    usage_count: number
    total_cost: number
  }>
}

// 模型搜索参数接口
export interface ModelSearchParams {
  page?: number
  page_size?: number
  keyword?: string
  provider?: string
  model_type?: string
  status?: string
  order_by?: string
  order_desc?: boolean
}

// 模型搜索结果接口
export interface ModelSearchResult {
  models: ModelInfo[]
  total: number
  page: number
  page_size: number
}

// 模型创建请求接口
export interface ModelCreateRequest {
  name: string
  display_name?: string
  provider: string
  model_type: string
  version?: string
  description?: string
  api_endpoint?: string
  api_key?: string
  max_tokens?: number
  temperature?: number
  pricing?: {
    input_price: number
    output_price: number
    currency: string
  }
  config?: Record<string, any>
}

// 模型更新请求接口
export interface ModelUpdateRequest {
  name?: string
  display_name?: string
  provider?: string
  model_type?: string
  version?: string
  description?: string
  api_endpoint?: string
  api_key?: string
  max_tokens?: number
  temperature?: number
  pricing?: {
    input_price: number
    output_price: number
    currency: string
  }
  config?: Record<string, any>
  status?: string
}

// 模型测试请求接口
export interface ModelTestRequest {
  prompt: string
  max_tokens?: number
  temperature?: number
  test_type?: 'simple' | 'comprehensive'
}

// 模型测试结果接口
export interface ModelTestResult {
  success: boolean
  response_time: number
  response_content?: string
  tokens_used?: number
  cost?: number
  error_message?: string
  performance_metrics?: {
    latency: number
    throughput: number
    error_rate: number
  }
}

// 模型使用记录接口
export interface ModelUsageRecord {
  id: number
  model_id: number
  user_id: number
  request_time: string
  response_time: number
  tokens_input: number
  tokens_output: number
  cost: number
  status: 'success' | 'failed' | 'timeout'
  error_message?: string
  request_data?: Record<string, any>
  response_data?: Record<string, any>
}

export const modelApi = {
  /**
   * 获取模型统计信息
   */
  getStatistics(): Promise<ApiResponse<ModelStatistics>> {
    return http.get('/models/statistics')
  },

  /**
   * 获取模型配置列表（标准分页接口）
   */
  getModelList(params: {
    page?: number
    page_size?: number
    keyword?: string
    provider?: string
    model_type?: string
    is_active?: boolean
  } = {}): Promise<ApiResponse<ModelSearchResult>> {
    const { page = 1, page_size = 20, ...filters } = params
    const queryParams = { page, page_size, ...filters }
    return http.get('/model-configs', { params: queryParams })
  },

  /**
   * 获取模型详情
   */
  getModelDetail(modelId: number): Promise<ApiResponse<ModelInfo>> {
    return http.get(`/model-configs/${modelId}`)
  },

  /**
   * 创建模型
   */
  createModel(data: ModelCreateRequest): Promise<ApiResponse<ModelInfo>> {
    return http.post('/model-configs', data)
  },

  /**
   * 更新模型
   */
  updateModel(modelId: number, data: ModelUpdateRequest): Promise<ApiResponse<ModelInfo>> {
    return http.put(`/model-configs/${modelId}`, data)
  },

  /**
   * 删除模型
   */
  deleteModel(modelId: number): Promise<ApiResponse<void>> {
    return http.delete(`/model-configs/${modelId}`)
  },

  /**
   * 测试模型连接
   */
  testModel(modelId: number, data: ModelTestRequest): Promise<ApiResponse<ModelTestResult>> {
    return http.post(`/model-configs/${modelId}/test`, data)
  },

  /**
   * 激活模型
   */
  activateModel(modelId: number): Promise<ApiResponse<void>> {
    return http.post(`/model-configs/${modelId}/activate`)
  },

  /**
   * 停用模型
   */
  deactivateModel(modelId: number): Promise<ApiResponse<void>> {
    return http.post(`/model-configs/${modelId}/deactivate`)
  },

  /**
   * 获取模型使用记录
   */
  getModelUsage(modelId: number, params?: {
    page?: number
    page_size?: number
    start_time?: string
    end_time?: string
    status?: string
  }): Promise<ApiResponse<{ records: ModelUsageRecord[]; total: number }>> {
    return http.get(`/model-configs/${modelId}/usage`, { params })
  },

  /**
   * 获取模型性能指标
   */
  getModelMetrics(modelId: number, timeRange?: {
    start_time: string
    end_time: string
  }): Promise<ApiResponse<{
    avg_response_time: number
    success_rate: number
    total_requests: number
    total_tokens: number
    total_cost: number
    error_rate: number
    time_series: Array<{
      timestamp: string
      request_count: number
      avg_response_time: number
      success_rate: number
      tokens_used: number
      cost: number
    }>
  }>> {
    return http.get(`/model-configs/${modelId}/metrics`, { params: timeRange })
  },

  /**
   * 批量导入模型配置
   */
  importModels(file: File): Promise<ApiResponse<{
    success_count: number
    failed_count: number
    failed_models?: Array<{ name: string; error: string }>
  }>> {
    const formData = new FormData()
    formData.append('config_file', file)
    return http.post('/models/import', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },

  /**
   * 导出模型配置
   */
  exportModels(modelIds?: number[]): Promise<Blob> {
    const params = modelIds ? { model_ids: modelIds.join(',') } : {}
    return http.get('/models/export', { 
      params,
      responseType: 'blob' 
    })
  },

  /**
   * 获取可用的模型提供商
   */
  getProviders(): Promise<ApiResponse<Array<{
    name: string
    display_name: string
    supported_types: string[]
    required_config: string[]
    description: string
  }>>> {
    return http.get('/models/providers')
  },

  /**
   * 获取模型配置模板
   */
  getConfigTemplates(provider?: string): Promise<ApiResponse<Array<{
    name: string
    provider: string
    model_type: string
    config: Record<string, any>
    description: string
  }>>> {
    return http.get('/models/templates', { params: { provider } })
  },

  /**
   * 验证模型配置
   */
  validateConfig(data: {
    provider: string
    model_type: string
    config: Record<string, any>
  }): Promise<ApiResponse<{
    valid: boolean
    errors?: string[]
    warnings?: string[]
  }>> {
    return http.post('/models/validate-config', data)
  },

  /**
   * 获取模型定价信息
   */
  getModelPricing(modelId: number): Promise<ApiResponse<{
    input_price: number
    output_price: number
    currency: string
    pricing_model: 'per_token' | 'per_request' | 'subscription'
    free_tier?: {
      daily_limit: number
      monthly_limit: number
    }
  }>> {
    return http.get(`/models/${modelId}/pricing`)
  }
}

// 模型工具类
export const modelUtils = {
  /**
   * 格式化模型状态
   */
  formatStatus(status: string): { text: string; type: string; color: string } {
    const statusMap = {
      active: { text: '激活', type: 'success', color: '#67c23a' },
      inactive: { text: '未激活', type: 'info', color: '#909399' },
      maintenance: { text: '维护中', type: 'warning', color: '#e6a23c' },
      deprecated: { text: '已废弃', type: 'danger', color: '#f56c6c' }
    }
    return statusMap[status as keyof typeof statusMap] || statusMap.inactive
  },

  /**
   * 格式化模型提供商
   */
  formatProvider(provider: string): { text: string; icon: string; color: string } {
    const providerMap = {
      openai: { text: 'OpenAI', icon: '🤖', color: '#00a67e' },
      anthropic: { text: 'Anthropic', icon: '🧠', color: '#d4a574' },
      azure: { text: 'Azure OpenAI', icon: '☁️', color: '#0078d4' },
      google: { text: 'Google', icon: '🔍', color: '#4285f4' },
      baidu: { text: '百度', icon: '🐻', color: '#2932e1' },
      alibaba: { text: '阿里云', icon: '☁️', color: '#ff6a00' },
      tencent: { text: '腾讯云', icon: '☁️', color: '#006eff' },
      local: { text: '本地模型', icon: '💻', color: '#909399' },
      custom: { text: '自定义', icon: '⚙️', color: '#606266' }
    }
    return providerMap[provider as keyof typeof providerMap] || providerMap.custom
  },

  /**
   * 格式化模型类型
   */
  formatType(type: string): { text: string; icon: string; color: string } {
    const typeMap = {
      chat: { text: '对话模型', icon: '💬', color: '#409eff' },
      completion: { text: '文本生成', icon: '📝', color: '#67c23a' },
      embedding: { text: '向量模型', icon: '🔗', color: '#e6a23c' },
      image: { text: '图像模型', icon: '🖼️', color: '#f56c6c' },
      audio: { text: '音频模型', icon: '🎵', color: '#909399' },
      multimodal: { text: '多模态', icon: '🎭', color: '#9c27b0' }
    }
    return typeMap[type as keyof typeof typeMap] || typeMap.chat
  },

  /**
   * 计算Token成本
   */
  calculateCost(inputTokens: number, outputTokens: number, pricing: {
    input_price: number
    output_price: number
  }): number {
    const inputCost = (inputTokens / 1000) * pricing.input_price
    const outputCost = (outputTokens / 1000) * pricing.output_price
    return inputCost + outputCost
  },

  /**
   * 格式化成本
   */
  formatCost(cost: number, currency = '¥'): string {
    if (cost < 0.01) {
      return `${currency}${(cost * 100).toFixed(4)}分`
    } else if (cost < 1) {
      return `${currency}${(cost * 100).toFixed(2)}分`
    } else {
      return `${currency}${cost.toFixed(2)}`
    }
  },

  /**
   * 格式化Token数量
   */
  formatTokens(tokens: number): string {
    if (tokens < 1000) {
      return `${tokens}`
    } else if (tokens < 1000000) {
      return `${(tokens / 1000).toFixed(1)}K`
    } else {
      return `${(tokens / 1000000).toFixed(1)}M`
    }
  },

  /**
   * 验证API密钥格式
   */
  validateApiKey(key: string, provider: string): { valid: boolean; message?: string } {
    if (!key || key.trim().length === 0) {
      return { valid: false, message: 'API密钥不能为空' }
    }

    switch (provider) {
      case 'openai':
        if (!key.startsWith('sk-')) {
          return { valid: false, message: 'OpenAI API密钥应以"sk-"开头' }
        }
        if (key.length < 20) {
          return { valid: false, message: 'OpenAI API密钥长度不正确' }
        }
        break
      case 'anthropic':
        if (!key.startsWith('sk-ant-')) {
          return { valid: false, message: 'Anthropic API密钥应以"sk-ant-"开头' }
        }
        break
      case 'azure':
        if (key.length !== 32) {
          return { valid: false, message: 'Azure API密钥长度应为32位' }
        }
        break
    }

    return { valid: true }
  },

  /**
   * 获取模型推荐配置
   */
  getRecommendedConfig(modelType: string, useCase: string): Record<string, any> {
    const configs = {
      chat: {
        general: { temperature: 0.7, max_tokens: 2000 },
        creative: { temperature: 0.9, max_tokens: 3000 },
        factual: { temperature: 0.3, max_tokens: 1500 },
        coding: { temperature: 0.2, max_tokens: 4000 }
      },
      completion: {
        general: { temperature: 0.7, max_tokens: 1000 },
        creative: { temperature: 0.8, max_tokens: 2000 },
        technical: { temperature: 0.4, max_tokens: 1500 }
      }
    }

    return configs[modelType as keyof typeof configs]?.[useCase] || { temperature: 0.7, max_tokens: 2000 }
  },

  /**
   * 生成模型测试提示词
   */
  generateTestPrompts(modelType: string): Array<{ name: string; prompt: string; description: string }> {
    const prompts = {
      chat: [
        {
          name: '基础对话',
          prompt: '你好，请介绍一下你自己。',
          description: '测试基本对话能力'
        },
        {
          name: '逻辑推理',
          prompt: '如果一个房间里有3只猫，每只猫抓了2只老鼠，总共抓了多少只老鼠？',
          description: '测试逻辑推理能力'
        },
        {
          name: '创意写作',
          prompt: '请写一个关于人工智能的简短故事。',
          description: '测试创意表达能力'
        }
      ],
      completion: [
        {
          name: '文本续写',
          prompt: '人工智能的发展正在改变我们的生活方式，',
          description: '测试文本续写能力'
        },
        {
          name: '格式化输出',
          prompt: '请用JSON格式列出5种常见的编程语言：',
          description: '测试结构化输出能力'
        }
      ],
      embedding: [
        {
          name: '文本嵌入',
          prompt: '这是一个用于测试向量化的文本样本。',
          description: '测试文本向量化能力'
        }
      ]
    }

    return prompts[modelType as keyof typeof prompts] || prompts.chat
  }
}

export default modelApi
