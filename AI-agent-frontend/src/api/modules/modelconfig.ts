// AI模型配置管理API
import { http } from '@/api/http'
import type { 
  ModelConfigInfo,
  ModelConfigCreateRequest, 
  ModelConfigUpdateRequest,
  ModelConfigResponse,
  ModelConfigListResponse
} from '../types'

export const modelConfigApi = {
  /**
   * 创建AI模型配置
   */
  createModelConfig(data: ModelConfigCreateRequest) {
    return http.post<ModelConfigResponse>('/api/v1/model-configs/', data)
  },

  /**
   * 获取模型配置详情
   */
  getModelConfig(id: number) {
    return http.get<ModelConfigResponse>(`/api/v1/model-configs/${id}`)
  },

  /**
   * 更新模型配置
   */
  updateModelConfig(id: number, data: ModelConfigUpdateRequest) {
    return http.put<ModelConfigResponse>(`/api/v1/model-configs/${id}`, data)
  },

  /**
   * 删除模型配置
   */
  deleteModelConfig(id: number) {
    return http.delete(`/api/v1/model-configs/${id}`)
  },

  /**
   * 获取模型配置列表
   */
  getModelConfigList(params: { 
    page?: number; 
    page_size?: number; 
    keyword?: string;
    provider?: string;
    status?: string;
  } = {}) {
    return http.get<ModelConfigListResponse>('/api/v1/model-configs/', { params })
  },

  /**
   * 搜索模型配置
   */
  searchModelConfigs(params: { 
    page?: number; 
    page_size?: number; 
    keyword?: string;
    provider?: string;
    status?: string;
  }) {
    return http.post<ModelConfigListResponse>('/api/v1/model-configs/search', params)
  },

  /**
   * 测试模型配置连接
   */
  testModelConfig(id: number) {
    return http.post<{
      success: boolean;
      message: string;
      data: {
        status: 'success' | 'failed';
        response_time: number;
        error_message?: string;
        model_info?: {
          model_name: string;
          version?: string;
          capabilities: string[];
        }
      }
    }>(`/api/v1/model-configs/${id}/test`)
  },

  /**
   * 批量测试模型配置
   */
  batchTestModelConfigs(ids: number[]) {
    return http.post('/api/v1/model-configs/batch/test', { 
      model_config_ids: ids 
    })
  },

  /**
   * 激活/停用模型配置
   */
  toggleModelConfigStatus(id: number, status: 'active' | 'inactive') {
    return http.post<ModelConfigResponse>(`/api/v1/model-configs/${id}/status`, { status })
  },

  /**
   * 批量操作模型配置
   */
  batchOperation(data: {
    model_config_ids: number[];
    operation: 'activate' | 'deactivate' | 'delete' | 'test';
  }) {
    return http.post<{
      success: boolean;
      message: string;
      data: {
        total: number;
        success_count: number;
        failure_count: number;
        results: Array<{
          model_config_id: number;
          success: boolean;
          message?: string;
        }>;
      }
    }>('/api/v1/model-configs/batch', data)
  },

  /**
   * 获取模型配置统计信息
   */
  getStatistics() {
    return http.get<{
      success: boolean;
      message: string;
      data: {
        total_configs: number;
        active_configs: number;
        inactive_configs: number;
        error_configs: number;
        by_provider: Record<string, number>;
        usage_stats: {
          total_usage: number;
          total_errors: number;
          avg_response_time: number;
        }
      }
    }>('/api/v1/model-configs/statistics')
  },

  /**
   * 获取支持的模型提供商列表
   */
  getSupportedProviders() {
    return http.get<{
      success: boolean;
      message: string;
      data: Array<{
        provider: string;
        name: string;
        description: string;
        models: Array<{
          model_name: string;
          display_name: string;
          max_tokens: number;
          capabilities: string[];
        }>;
        required_fields: Array<{
          field: string;
          label: string;
          type: string;
          required: boolean;
          default_value?: any;
          description?: string;
        }>;
      }>
    }>('/api/v1/model-configs/providers')
  },

  /**
   * 获取模型使用情况报告
   */
  getUsageReport(params: {
    start_date?: string;
    end_date?: string;
    provider?: string;
    model_config_id?: number;
  } = {}) {
    return http.get<{
      success: boolean;
      message: string;
      data: {
        summary: {
          total_requests: number;
          successful_requests: number;
          failed_requests: number;
          avg_response_time: number;
          total_tokens_used: number;
        };
        daily_stats: Array<{
          date: string;
          requests: number;
          success_rate: number;
          avg_response_time: number;
          tokens_used: number;
        }>;
        by_model: Array<{
          model_config_id: number;
          model_name: string;
          requests: number;
          success_rate: number;
          avg_response_time: number;
        }>;
      }
    }>('/api/v1/model-configs/usage-report', { params })
  }
}