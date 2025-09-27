// 测试用例相关API
import { http } from '@/api/http'
import type { ApiResponse } from '@/api/types'

// 测试用例信息接口
export interface TestCaseInfo {
  id: number
  title: string
  description: string
  test_type: 'functional' | 'performance' | 'security' | 'integration' | 'unit' | 'api' | 'ui' | 'smoke'
  priority: 'low' | 'medium' | 'high' | 'critical'
  status: 'draft' | 'active' | 'deprecated' | 'archived'
  
  // 测试步骤
  steps: TestStep[]
  
  // 预期结果
  expected_result: string
  
  // 前置条件
  preconditions?: string[]
  
  // 测试数据
  test_data?: Record<string, any>
  
  // 标签
  tags: string[]
  
  // 自动化相关
  automation: {
    is_automated: boolean
    automation_script?: string
    automation_framework?: string
    automation_level: 'none' | 'partial' | 'full'
  }
  
  // 关联信息
  category_id?: number
  category_name?: string
  module_id?: number
  module_name?: string
  requirement_id?: string
  
  // 执行信息
  execution_count: number
  last_execution_time?: string
  last_execution_result?: 'passed' | 'failed' | 'skipped'
  
  // 创建信息
  created_at: string
  updated_at: string
  created_by_id: number
  creator_name?: string
  assigned_to_id?: number
  assigned_to_name?: string
}

// 测试步骤接口
export interface TestStep {
  step_number: number
  action: string
  expected_result: string
  test_data?: any
  notes?: string
}

// 测试用例生成请求接口
export interface TestCaseGenerateRequest {
  requirement_text: string
  test_type: string
  priority: string
  count: number
  agent_ids: number[]
  additional_config?: {
    include_negative_cases?: boolean
    include_boundary_cases?: boolean
    include_performance_cases?: boolean
    automation_target?: boolean
    coverage_requirements?: string[]
  }
}

// 测试用例生成任务接口
export interface TestCaseGenerationTask {
  task_id: string
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled'
  progress: number
  generated_count: number
  total_expected: number
  current_stage: string
  error_message?: string
  result?: {
    generated_cases: TestCaseInfo[]
    statistics: {
      total_generated: number
      by_priority: Record<string, number>
      by_type: Record<string, number>
      automation_percentage: number
    }
  }
  created_at: string
  updated_at: string
}

// 测试用例搜索参数接口
export interface TestCaseSearchParams {
  page?: number
  page_size?: number
  keyword?: string
  test_type?: string
  priority?: string
  status?: string
  category_id?: number
  module_id?: number
  assigned_to_id?: number
  created_by_id?: number
  tags?: string[]
  automation_level?: string
  order_by?: string
  order_desc?: boolean
}

// 测试用例搜索结果接口
export interface TestCaseSearchResult {
  test_cases: TestCaseInfo[]
  total: number
  page: number
  page_size: number
  statistics?: {
    total_count: number
    by_status: Record<string, number>
    by_priority: Record<string, number>
    automation_stats: {
      automated_count: number
      automation_percentage: number
    }
  }
}

// 测试用例创建请求接口
export interface TestCaseCreateRequest {
  title: string
  description: string
  test_type: string
  priority: string
  steps: Omit<TestStep, 'step_number'>[]
  expected_result: string
  preconditions?: string[]
  test_data?: Record<string, any>
  tags?: string[]
  category_id?: number
  module_id?: number
  requirement_id?: string
  automation?: {
    is_automated: boolean
    automation_script?: string
    automation_framework?: string
    automation_level: string
  }
}

// 测试用例更新请求接口
export interface TestCaseUpdateRequest {
  title?: string
  description?: string
  test_type?: string
  priority?: string
  status?: string
  steps?: Omit<TestStep, 'step_number'>[]
  expected_result?: string
  preconditions?: string[]
  test_data?: Record<string, any>
  tags?: string[]
  category_id?: number
  module_id?: number
  requirement_id?: string
  automation?: {
    is_automated?: boolean
    automation_script?: string
    automation_framework?: string
    automation_level?: string
  }
  assigned_to_id?: number
}

// 测试用例批量操作请求接口
export interface TestCaseBatchRequest {
  case_ids: number[]
  operation: 'delete' | 'archive' | 'activate' | 'assign' | 'tag' | 'export'
  params?: Record<string, any>
}

// 生成历史记录接口
export interface GenerationHistoryItem {
  id: number
  task_id: string
  requirement_text: string
  requirement_summary: string
  test_type: string
  priority: string
  count: number
  generated_count: number
  status: string
  agent_ids: number[]
  agent_names: string[]
  error_message?: string
  created_at: string
  updated_at: string
  created_by_id: number
  creator_name: string
}

export const testCaseApi = {
  /**
   * 获取测试用例列表
   */
  getTestCaseList(params?: TestCaseSearchParams): Promise<ApiResponse<TestCaseSearchResult>> {
    return http.get('/test-cases', { params })
  },

  /**
   * 搜索测试用例
   */
  searchTestCases(params: TestCaseSearchParams): Promise<ApiResponse<TestCaseSearchResult>> {
    return http.get('/test-cases/search', { params })
  },

  /**
   * 获取测试用例详情
   */
  getTestCaseDetail(caseId: number): Promise<ApiResponse<TestCaseInfo>> {
    return http.get(`/test-cases/${caseId}`)
  },

  /**
   * 创建测试用例
   */
  createTestCase(data: TestCaseCreateRequest): Promise<ApiResponse<TestCaseInfo>> {
    return http.post('/test-cases', data)
  },

  /**
   * 更新测试用例
   */
  updateTestCase(caseId: number, data: TestCaseUpdateRequest): Promise<ApiResponse<TestCaseInfo>> {
    return http.put(`/test-cases/${caseId}`, data)
  },

  /**
   * 删除测试用例
   */
  deleteTestCase(caseId: number): Promise<ApiResponse<void>> {
    return http.delete(`/test-cases/${caseId}`)
  },

  /**
   * 生成测试用例
   */
  generateTestCases(data: TestCaseGenerateRequest): Promise<ApiResponse<{ task_id: string }>> {
    return http.post('/test-cases/generate', data)
  },

  /**
   * 检查生成任务状态
   */
  checkGenerationTask(taskId: string): Promise<ApiResponse<TestCaseGenerationTask>> {
    return http.get(`/test-cases/generation-tasks/${taskId}`)
  },

  /**
   * 取消生成任务
   */
  cancelGenerationTask(taskId: string): Promise<ApiResponse<void>> {
    return http.post(`/test-cases/generation-tasks/${taskId}/cancel`)
  },

  /**
   * 获取生成历史
   */
  getGenerationHistory(params?: {
    page?: number
    page_size?: number
    status?: string
    test_type?: string
  }): Promise<ApiResponse<{
    history: GenerationHistoryItem[]
    total: number
  }>> {
    return http.get('/test-cases/generation-history', { params })
  },

  /**
   * 批量操作测试用例
   */
  batchOperation(data: TestCaseBatchRequest): Promise<ApiResponse<{
    success_count: number
    failed_count: number
    failed_cases?: Array<{ id: number; title: string; error: string }>
  }>> {
    return http.post('/test-cases/batch-operation', data)
  },

  /**
   * 导出测试用例
   */
  exportTestCases(caseIds: number[], format: 'excel' | 'csv' | 'json' = 'excel'): Promise<Blob> {
    return http.post('/test-cases/export', {
      case_ids: caseIds,
      format
    }, {
      responseType: 'blob'
    })
  },

  /**
   * 导入测试用例
   */
  importTestCases(file: File, options?: {
    category_id?: number
    override_existing?: boolean
    auto_assign?: boolean
  }): Promise<ApiResponse<{
    imported_count: number
    failed_count: number
    failed_cases?: Array<{ row: number; title: string; error: string }>
  }>> {
    const formData = new FormData()
    formData.append('file', file)
    if (options) {
      Object.entries(options).forEach(([key, value]) => {
        if (value !== undefined) {
          formData.append(key, String(value))
        }
      })
    }
    
    return http.post('/test-cases/import', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },

  /**
   * 执行测试用例
   */
  executeTestCase(caseId: number, params?: {
    environment?: string
    browser?: string
    test_data?: Record<string, any>
  }): Promise<ApiResponse<{ execution_id: string }>> {
    return http.post(`/test-cases/${caseId}/execute`, params || {})
  },

  /**
   * 获取测试用例执行历史
   */
  getExecutionHistory(caseId: number, params?: {
      page?: number
      page_size?: number
    status?: string
  }): Promise<ApiResponse<{
    executions: Array<{
      id: string
      status: string
      start_time: string
      end_time?: string
      duration: number
      result: string
      error_message?: string
      screenshots?: string[]
      logs?: string[]
    }>
        total: number
  }>> {
    return http.get(`/test-cases/${caseId}/executions`, { params })
  },

  /**
   * 获取测试分类列表
   */
  getCategories(): Promise<ApiResponse<Array<{
    id: number
    name: string
    description?: string
    parent_id?: number
    children?: any[]
  }>>> {
    return http.get('/test-cases/categories')
  },

  /**
   * 创建测试分类
   */
  createCategory(data: {
    name: string
    description?: string
    parent_id?: number
  }): Promise<ApiResponse<{ id: number; name: string }>> {
    return http.post('/test-cases/categories', data)
  },

  /**
   * 获取测试模块列表
   */
  getModules(): Promise<ApiResponse<Array<{
    id: number
    name: string
    description?: string
    category_id: number
  }>>> {
    return http.get('/test-cases/modules')
  },

  /**
   * 创建测试模块
   */
  createModule(data: {
    name: string
    description?: string
    category_id: number
  }): Promise<ApiResponse<{ id: number; name: string }>> {
    return http.post('/test-cases/modules', data)
  },

  /**
   * 获取标签列表
   */
  getTags(): Promise<ApiResponse<Array<{
    name: string
    count: number
    color?: string
  }>>> {
    return http.get('/test-cases/tags')
  },

  /**
   * 获取测试用例模板
   */
  getTemplates(type?: string): Promise<ApiResponse<Array<{
          id: number
    name: string
    description: string
          test_type: string
    template_content: TestCaseCreateRequest
  }>>> {
    return http.get('/test-cases/templates', { params: { type } })
  },

  /**
   * 从模板创建测试用例
   */
  createFromTemplate(templateId: number, data?: Partial<TestCaseCreateRequest>): Promise<ApiResponse<TestCaseInfo>> {
    return http.post(`/test-cases/templates/${templateId}/create`, data || {})
  },

  /**
   * 克隆测试用例
   */
  cloneTestCase(caseId: number, data?: {
    title_suffix?: string
    copy_automation?: boolean
  }): Promise<ApiResponse<TestCaseInfo>> {
    return http.post(`/test-cases/${caseId}/clone`, data || {})
  },

  /**
   * 获取测试用例统计信息
   */
  getStatistics(params?: {
    category_id?: number
    date_range?: {
      start_date: string
      end_date: string
    }
  }): Promise<ApiResponse<{
    total_cases: number
    by_status: Record<string, number>
    by_priority: Record<string, number>
    by_type: Record<string, number>
    automation_stats: {
      automated_count: number
      automation_percentage: number
    }
    execution_stats: {
      total_executions: number
      success_rate: number
      avg_execution_time: number
    }
    recent_activity: Array<{
      date: string
      created_count: number
      executed_count: number
      success_rate: number
    }>
  }>> {
    return http.get('/test-cases/statistics/overview', { params })
  }
}

// 测试用例工具类
export const testCaseUtils = {
  /**
   * 格式化测试类型
   */
  formatTestType(type: string): { text: string; icon: string; color: string } {
    const typeMap = {
      functional: { text: '功能测试', icon: '🔧', color: '#409eff' },
      performance: { text: '性能测试', icon: '⚡', color: '#e6a23c' },
      security: { text: '安全测试', icon: '🔒', color: '#f56c6c' },
      integration: { text: '集成测试', icon: '🔗', color: '#67c23a' },
      unit: { text: '单元测试', icon: '📦', color: '#909399' },
      api: { text: 'API测试', icon: '🌐', color: '#9c27b0' },
      ui: { text: 'UI测试', icon: '🖥️', color: '#ff9800' },
      smoke: { text: '冒烟测试', icon: '💨', color: '#607d8b' }
    }
    return typeMap[type as keyof typeof typeMap] || typeMap.functional
  },

  /**
   * 格式化优先级
   */
  formatPriority(priority: string): { text: string; type: string; color: string } {
    const priorityMap = {
      low: { text: '低', type: 'info', color: '#909399' },
      medium: { text: '中', type: 'warning', color: '#e6a23c' },
      high: { text: '高', type: 'primary', color: '#409eff' },
      critical: { text: '紧急', type: 'danger', color: '#f56c6c' }
    }
    return priorityMap[priority as keyof typeof priorityMap] || priorityMap.medium
  },

  /**
   * 格式化状态
   */
  formatStatus(status: string): { text: string; type: string; color: string } {
    const statusMap = {
      draft: { text: '草稿', type: 'info', color: '#909399' },
      active: { text: '激活', type: 'success', color: '#67c23a' },
      deprecated: { text: '已废弃', type: 'warning', color: '#e6a23c' },
      archived: { text: '已归档', type: 'info', color: '#909399' }
    }
    return statusMap[status as keyof typeof statusMap] || statusMap.draft
  },

  /**
   * 格式化自动化等级
   */
  formatAutomationLevel(level: string): { text: string; icon: string; color: string } {
    const levelMap = {
      none: { text: '未自动化', icon: '❌', color: '#909399' },
      partial: { text: '部分自动化', icon: '⚠️', color: '#e6a23c' },
      full: { text: '完全自动化', icon: '✅', color: '#67c23a' }
    }
    return levelMap[level as keyof typeof levelMap] || levelMap.none
  },

  /**
   * 验证测试步骤
   */
  validateSteps(steps: TestStep[]): { valid: boolean; errors: string[] } {
    const errors: string[] = []
    
    if (!steps || steps.length === 0) {
      errors.push('至少需要一个测试步骤')
      return { valid: false, errors }
    }
    
    steps.forEach((step, index) => {
      if (!step.action || step.action.trim().length === 0) {
        errors.push(`第${index + 1}步：操作描述不能为空`)
      }
      
      if (!step.expected_result || step.expected_result.trim().length === 0) {
        errors.push(`第${index + 1}步：预期结果不能为空`)
      }
    })
    
    return { valid: errors.length === 0, errors }
  },

  /**
   * 生成测试用例编号
   */
  generateCaseNumber(prefix: string, categoryId?: number, sequence?: number): string {
    const categoryCode = categoryId ? String(categoryId).padStart(2, '0') : '00'
    const seqCode = sequence ? String(sequence).padStart(4, '0') : '0001'
    return `${prefix}-${categoryCode}-${seqCode}`
  },

  /**
   * 计算测试覆盖率
   */
  calculateCoverage(totalRequirements: number, coveredRequirements: number): number {
    if (totalRequirements === 0) return 0
    return Math.round((coveredRequirements / totalRequirements) * 100)
  },

  /**
   * 解析需求文本
   */
  parseRequirementText(text: string): {
    summary: string
    keywords: string[]
    testTypes: string[]
    complexity: 'low' | 'medium' | 'high'
  } {
    const keywords = this.extractKeywords(text)
    const testTypes = this.suggestTestTypes(text)
    const complexity = this.assessComplexity(text)
    const summary = this.generateSummary(text)
    
    return { summary, keywords, testTypes, complexity }
  },

  /**
   * 提取关键词
   */
  extractKeywords(text: string): string[] {
    // 简单的关键词提取逻辑
    const words = text.toLowerCase()
      .replace(/[^\w\s\u4e00-\u9fa5]/g, '')
      .split(/\s+/)
      .filter(word => word.length > 2)
    
    const stopWords = ['的', '了', '在', '是', '和', '有', '对', '为', '与', '及', '等', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for']
    
    return [...new Set(words.filter(word => !stopWords.includes(word)))].slice(0, 10)
  },

  /**
   * 建议测试类型
   */
  suggestTestTypes(text: string): string[] {
    const types: string[] = []
    const lowerText = text.toLowerCase()
    
    if (lowerText.includes('性能') || lowerText.includes('响应时间') || lowerText.includes('并发')) {
      types.push('performance')
    }
    
    if (lowerText.includes('安全') || lowerText.includes('权限') || lowerText.includes('认证')) {
      types.push('security')
    }
    
    if (lowerText.includes('接口') || lowerText.includes('api') || lowerText.includes('服务')) {
      types.push('api')
    }
    
    if (lowerText.includes('界面') || lowerText.includes('ui') || lowerText.includes('页面')) {
      types.push('ui')
    }
    
    if (lowerText.includes('集成') || lowerText.includes('系统间') || lowerText.includes('第三方')) {
      types.push('integration')
    }
    
    // 默认功能测试
    if (types.length === 0) {
      types.push('functional')
    }
    
    return types
  },

  /**
   * 评估复杂度
   */
  assessComplexity(text: string): 'low' | 'medium' | 'high' {
    const wordCount = text.split(/\s+/).length
    const complexKeywords = ['复杂', '多步骤', '集成', '第三方', '并发', '事务', '工作流', '状态机']
    const hasComplexKeywords = complexKeywords.some(keyword => text.includes(keyword))
    
    if (wordCount > 200 || hasComplexKeywords) {
      return 'high'
    } else if (wordCount > 100) {
      return 'medium'
    } else {
      return 'low'
    }
  },

  /**
   * 生成摘要
   */
  generateSummary(text: string, maxLength = 100): string {
    if (text.length <= maxLength) return text
    
    // 简单的摘要生成：取前几句话
    const sentences = text.split(/[。！？.!?]/).filter(s => s.trim().length > 0)
    let summary = ''
    
    for (const sentence of sentences) {
      if (summary.length + sentence.length <= maxLength) {
        summary += sentence + '。'
      } else {
        break
      }
    }
    
    return summary || text.substring(0, maxLength) + '...'
  }
}

export default testCaseApi