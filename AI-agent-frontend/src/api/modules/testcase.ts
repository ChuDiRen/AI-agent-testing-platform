// 测试用例生成管理API
import { http } from '@/api/http'
import type { 
  TestCaseInfo,
  TestCaseGenerateRequest, 
  TestCaseGenerateResponse,
  TestCaseListResponse
} from '../types'

export const testCaseApi = {
  /**
   * 生成AI测试用例
   */
  generateTestCases(data: TestCaseGenerateRequest) {
    return http.post<TestCaseGenerateResponse>('/test-cases/generate', data)
  },

  /**
   * 获取测试用例详情
   */
  getTestCase(id: number) {
    return http.get<{ success: boolean; message: string; data: TestCaseInfo }>(`/test-cases/${id}`)
  },

  /**
   * 更新测试用例
   */
  updateTestCase(id: number, data: Partial<TestCaseInfo>) {
    return http.put<{ success: boolean; message: string; data: TestCaseInfo }>(`/test-cases/${id}`, data)
  },

  /**
   * 删除测试用例
   */
  deleteTestCase(id: number) {
    return http.delete(`/test-cases/${id}`)
  },

  /**
   * 获取测试用例列表
   */
  getTestCaseList(params: {
    page?: number;
    page_size?: number;
    keyword?: string;
    priority?: string;
    test_type?: string;
    status?: string;
    project_id?: number;
    agent_id?: number;
  } = {}) {
    return http.get<TestCaseListResponse>('/test-cases/', { params })
  },

  /**
   * 搜索测试用例
   */
  searchTestCases(params: {
    page?: number;
    page_size?: number;
    keyword?: string;
    priority?: string;
    test_type?: string;
    status?: string;
    project_id?: number;
    agent_id?: number;
  }) {
    return http.post<TestCaseListResponse>('/test-cases/search', params)
  },

  /**
   * 批量删除测试用例
   */
  batchDeleteTestCases(ids: number[]) {
    return http.post('/test-cases/batch/delete', { test_case_ids: ids })
  },

  /**
   * 批量更新测试用例状态
   */
  batchUpdateStatus(ids: number[], status: 'draft' | 'active' | 'archived') {
    return http.post('/test-cases/batch/status', {
      test_case_ids: ids,
      status
    })
  },

  /**
   * 导出测试用例
   */
  exportTestCases(params: {
    test_case_ids?: number[];
    format?: 'excel' | 'json' | 'csv';
    project_id?: number;
  }) {
    return http.post('/test-cases/export', params, { responseType: 'blob' })
  },

  /**
   * 检查生成任务状态
   */
  checkGenerationTask(taskId: string) {
    return http.get<{
      success: boolean;
      message: string;
      data: {
        task_id: string;
        status: 'pending' | 'running' | 'completed' | 'failed';
        progress: number;
        generated_count: number;
        result?: TestCaseGenerateResponse['data'];
      }
    }>(`/test-cases/tasks/${taskId}`)
  },

  /**
   * 取消生成任务
   */
  cancelGenerationTask(taskId: string) {
    return http.post(`/test-cases/tasks/${taskId}/cancel`)
  },

  /**
   * 获取生成历史记录
   */
  getGenerationHistory(params: {
    page?: number;
    page_size?: number;
    user_id?: number;
  } = {}) {
    return http.get<{
      success: boolean;
      message: string;
      data: {
        total: number;
        page: number;
        page_size: number;
        history: Array<{
          id: number;
          task_id: string;
          requirement_text: string;
          test_type: string;
          priority: string;
          generated_count: number;
          status: 'pending' | 'running' | 'completed' | 'failed';
          created_at: string;
          updated_at: string;
        }>;
      };
    }>('/test-cases/history/generation', { params })
  }
}