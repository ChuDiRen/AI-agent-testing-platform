// 测试报告管理API
import { http } from '@/api/http'
import type { 
  TestReportInfo,
  TestReportCreateRequest,
  TestReportResponse,
  TestReportListResponse,
  TestReportStatisticsResponse
} from '../types'

export const testReportApi = {
  /**
   * 创建测试报告
   */
  createTestReport(data: TestReportCreateRequest) {
    return http.post<TestReportResponse>('/test-reports/', data)
  },

  /**
   * 获取测试报告详情
   */
  getTestReport(id: number) {
    return http.get<TestReportResponse>(`/test-reports/${id}`)
  },

  /**
   * 更新测试报告
   */
  updateTestReport(id: number, data: Partial<TestReportInfo>) {
    return http.put<TestReportResponse>(`/test-reports/${id}`, data)
  },

  /**
   * 删除测试报告
   */
  deleteTestReport(id: number) {
    return http.delete(`/test-reports/${id}`)
  },

  /**
   * 获取测试报告列表
   */
  getTestReportList(params: {
    page?: number;
    page_size?: number;
    keyword?: string;
    test_type?: string;
    status?: string;
    agent_id?: number;
    project_id?: number;
    start_date?: string;
    end_date?: string;
  } = {}) {
    return http.get<TestReportListResponse>('/test-reports/', { params })
  },

  /**
   * 搜索测试报告
   */
  searchTestReports(params: {
    page?: number;
    page_size?: number;
    keyword?: string;
    test_type?: string;
    status?: string;
    agent_id?: number;
    project_id?: number;
    start_date?: string;
    end_date?: string;
  }) {
    return http.post<TestReportListResponse>('/test-reports/search', params)
  },

  /**
   * 获取测试报告统计信息
   */
  getStatistics(params: {
    start_date?: string;
    end_date?: string;
    project_id?: number;
  } = {}) {
    return http.get<TestReportStatisticsResponse>('/test-reports/statistics', { params })
  },

  /**
   * 生成测试报告
   */
  generateReport(data: {
    title: string;
    test_case_ids: number[];
    test_type: 'functional' | 'performance' | 'security' | 'integration' | 'unit';
    agent_id?: number;
    project_id?: number;
    config?: {
      parallel_execution?: boolean;
      timeout?: number;
      retry_count?: number;
    }
  }) {
    return http.post<{
      success: boolean;
      message: string;
      data: {
        task_id: string;
        report_id?: number;
        estimated_time: number;
      }
    }>('/test-reports/generate', data)
  },

  /**
   * 获取报告生成任务状态
   */
  getGenerationTask(taskId: string) {
    return http.get<{
      success: boolean;
      message: string;
      data: {
        task_id: string;
        status: 'pending' | 'running' | 'completed' | 'failed';
        progress: number;
        report_id?: number;
        current_step?: string;
        executed_cases: number;
        total_cases: number;
        start_time: string;
        estimated_completion?: string;
      }
    }>(`/test-reports/tasks/${taskId}`)
  },

  /**
   * 取消报告生成任务
   */
  cancelGenerationTask(taskId: string) {
    return http.post(`/test-reports/tasks/${taskId}/cancel`)
  },

  /**
   * 导出测试报告
   */
  exportTestReport(reportId: number, format: 'pdf' | 'excel' | 'html' | 'json' = 'pdf') {
    return http.get(`/test-reports/${reportId}/export`, {
      params: { format },
      responseType: 'blob'
    })
  },

  /**
   * 批量导出测试报告
   */
  batchExportReports(data: {
    report_ids: number[];
    format: 'pdf' | 'excel' | 'html' | 'json';
    merge?: boolean;
  }) {
    return http.post('/test-reports/batch/export', data, {
      responseType: 'blob'
    })
  },

  /**
   * 重新执行测试报告
   */
  rerunTestReport(reportId: number, options?: {
    only_failed?: boolean;
    parallel?: boolean;
    timeout?: number;
  }) {
    return http.post<{
      success: boolean;
      message: string;
      data: {
        task_id: string;
        new_report_id: number;
      }
    }>(`/test-reports/${reportId}/rerun`, options || {})
  },

  /**
   * 比较测试报告
   */
  compareReports(reportId1: number, reportId2: number) {
    return http.post<{
      success: boolean;
      message: string;
      data: {
        comparison_id: string;
        report1: TestReportInfo;
        report2: TestReportInfo;
        differences: {
          success_rate_diff: number;
          execution_time_diff: number;
          case_differences: Array<{
            test_case_id: number;
            test_case_title: string;
            report1_status: string;
            report2_status: string;
            status_changed: boolean;
          }>;
        };
        summary: {
          improved_cases: number;
          regressed_cases: number;
          new_failures: number;
          fixed_failures: number;
        };
      }
    }>(`/test-reports/compare`, {
      report_id_1: reportId1,
      report_id_2: reportId2
    })
  },

  /**
   * 获取报告趋势数据
   */
  getTrendData(params: {
    project_id?: number;
    agent_id?: number;
    test_type?: string;
    days?: number;
  } = {}) {
    return http.get<{
      success: boolean;
      message: string;
      data: {
        trend_points: Array<{
          date: string;
          total_reports: number;
          success_rate: number;
          avg_execution_time: number;
          total_cases: number;
          passed_cases: number;
          failed_cases: number;
        }>;
        summary: {
          total_reports: number;
          avg_success_rate: number;
          trend_direction: 'improving' | 'declining' | 'stable';
        };
      }
    }>('/test-reports/trends', { params })
  },

  /**
   * 获取报告详细信息（包含测试用例详情）
   */
  getReportDetails(reportId: number) {
    return http.get<{
      success: boolean;
      message: string;
      data: TestReportInfo & {
        test_cases: Array<{
          test_case_id: number;
          test_case_title: string;
          status: 'passed' | 'failed' | 'skipped' | 'error';
          execution_time: number;
          error_message?: string;
          steps_executed: number;
          total_steps: number;
          screenshots: string[];
          logs: string[];
        }>;
        environment_info: {
          browser?: string;
          os?: string;
          test_environment: string;
          agent_version?: string;
        };
      }
    }>(`/test-reports/${reportId}/details`)
  }
}