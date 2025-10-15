import { request } from '@/utils/request'

export default {
  // ==================== Base模块 ====================
  // 认证相关 - 完全按照vue-fastapi-admin标准
  login: (data) => request.post('/api/v1/base/access_token', data, { noNeedToken: true }),
  getUserInfo: () => request.get('/api/v1/base/userinfo'),
  getUserMenu: () => request.get('/api/v1/base/usermenu'),
  getUserApi: () => request.get('/api/v1/base/userapi'),
  updatePassword: (data = {}) => request.post('/api/v1/base/update_password', data),

  // ==================== User模块 ====================
  // 用户管理 - 完全按照vue-fastapi-admin标准
  getUserList: (params = {}) => request.get('/api/v1/user/list', { params }),
  getUserById: (params = {}) => request.get('/api/v1/user/get', { params }),
  createUser: (data = {}) => request.post('/api/v1/user/create', data),
  updateUser: (data = {}) => request.post('/api/v1/user/update', data),
  deleteUser: (id) => request.delete('/api/v1/user/delete', { params: { user_id: id } }),
  resetPassword: (data = {}) => request.post('/api/v1/user/reset_password', data),

  // ==================== Role模块 ====================
  // 角色管理 - 完全按照vue-fastapi-admin标准
  getRoleList: (params = {}) => request.get('/api/v1/role/list', { params }),
  createRole: (data = {}) => request.post('/api/v1/role/create', data),
  updateRole: (data = {}) => request.post('/api/v1/role/update', data),
  deleteRole: (id) => request.delete('/api/v1/role/delete', { params: { role_id: id } }),
  getRoleAuthorized: (params = {}) => request.get('/api/v1/role/authorized', { params }),
  updateRoleAuthorized: (data = {}) => request.post('/api/v1/role/authorized', data),

  // ==================== Menu模块 ====================
  // 菜单管理 - 完全按照vue-fastapi-admin标准
  getMenus: (params = {}) => request.get('/api/v1/menu/list', { params }),
  createMenu: (data = {}) => request.post('/api/v1/menu/create', data),
  updateMenu: (data = {}) => request.post('/api/v1/menu/update', data),
  deleteMenu: (id) => request.delete('/api/v1/menu/delete', { params: { id } }),

  // ==================== API模块 ====================
  // API管理 - 完全按照vue-fastapi-admin标准
  getApis: (params = {}) => request.get('/api/v1/api/list', { params }),
  getApiEndpointList: (params = {}) => request.get('/api/v1/api/list', { params }),
  createApi: (data = {}) => request.post('/api/v1/api/create', data),
  updateApi: (data = {}) => request.post('/api/v1/api/update', data),
  deleteApi: (id) => request.delete('/api/v1/api/delete', { params: { id } }),
  refreshApi: () => request.post('/api/v1/api/refresh'),

  // ==================== Dept模块 ====================
  // 部门管理 - 完全按照vue-fastapi-admin标准
  getDepts: (params = {}) => request.get('/api/v1/dept/list', { params }),
  createDept: (data = {}) => request.post('/api/v1/dept/create', data),
  updateDept: (data = {}) => request.post('/api/v1/dept/update', data),
  deleteDept: (id) => request.delete('/api/v1/dept/delete', { params: { dept_id: id } }),

  // ==================== AuditLog模块 ====================
  // 审计日志 - 完全按照vue-fastapi-admin标准
  getAuditLogList: (params = {}) => request.get('/api/v1/auditlog/list', { params }),

  // ==================== Agent模块 ====================
  // AI代理管理
  getAgentList: (params = {}) => request.get('/api/v1/agents/', { params }),
  getAgentById: (id) => request.get(`/api/v1/agents/${id}`),
  createAgent: (data = {}) => request.post('/api/v1/agents/', data),
  updateAgent: (id, data = {}) => request.put(`/api/v1/agents/${id}`, data),
  deleteAgent: (id) => request.delete(`/api/v1/agents/${id}`),
  startAgent: (id) => request.post(`/api/v1/agents/${id}/start`),
  stopAgent: (id) => request.post(`/api/v1/agents/${id}/stop`),
  searchAgents: (data = {}) => request.post('/api/v1/agents/search', data),
  getAgentStatistics: () => request.get('/api/v1/agents/statistics/overview'),
  batchOperateAgents: (data = {}) => request.post('/api/v1/agents/batch', data),
  updateAgentStatus: (id, data = {}) => request.post(`/api/v1/agents/${id}/status`, data),
  exportAgents: (params = {}) => request.get('/api/v1/agents/export', { params, responseType: 'blob' }),

  // ==================== TestCase模块 ====================
  // 测试用例管理
  getTestCaseList: (params = {}) => request.get('/api/v1/test-cases/', { params }),
  getTestCaseById: (id) => request.get(`/api/v1/test-cases/${id}`),
  createTestCase: (data = {}) => request.post('/api/v1/test-cases/', data),
  updateTestCase: (id, data = {}) => request.put(`/api/v1/test-cases/${id}`, data),
  deleteTestCase: (id) => request.delete(`/api/v1/test-cases/${id}`),
  searchTestCases: (data = {}) => request.post('/api/v1/test-cases/search', data),
  getTestCaseStatistics: () => request.get('/api/v1/test-cases/statistics/overview'),
  batchOperateTestCases: (data = {}) => request.post('/api/v1/test-cases/batch', data),
  executeTestCase: (id, data = {}) => request.post(`/api/v1/test-cases/${id}/execute`, data),
  completeTestCase: (id, data = {}) => request.post(`/api/v1/test-cases/${id}/complete`, data),
  generateTestCases: (data = {}) => request.post('/api/v1/test-cases/generate', data),
  getGenerationTask: (taskId) => request.get(`/api/v1/test-cases/generation-tasks/${taskId}`),
  cancelGenerationTask: (taskId) => request.post(`/api/v1/test-cases/generation-tasks/${taskId}/cancel`),
  getTestCaseGenerationHistory: (params = {}) => request.get('/api/v1/test-cases/history/generation', { params }),
  batchExecuteTestCases: (data = {}) => request.post('/api/v1/test-cases/batch/execute', data),
  batchDeleteTestCases: (data = {}) => request.post('/api/v1/test-cases/batch/delete', data),
  batchCreateTestCases: (data = {}) => request.post('/api/v1/test-cases/batch/create', data),
  exportTestCases: (params = {}) => request.get('/api/v1/test-cases/export', { params, responseType: 'blob' }),
  getGenerationHistory: (params = {}) => request.get('/api/v1/test-cases/generation/history', { params }),

  // ==================== AIModel模块 ====================
  // AI模型配置管理
  getModelList: (params = {}) => request.get('/api/v1/model-configs/', { params }),
  getAIModelList: (params = {}) => request.get('/api/v1/model-configs/', { params }),
  getModelById: (id) => request.get(`/api/v1/model-configs/${id}`),
  createModel: (data = {}) => request.post('/api/v1/model-configs/', data),
  updateModel: (id, data = {}) => request.put(`/api/v1/model-configs/${id}`, data),
  deleteModel: (id) => request.delete(`/api/v1/model-configs/${id}`),
  searchModels: (data = {}) => request.post('/api/v1/model-configs/search', data),
  getModelStatistics: () => request.get('/api/v1/model-configs/statistics'),
  batchOperateModels: (data = {}) => request.post('/api/v1/model-configs/batch', data),
  updateModelStatus: (id, data = {}) => request.post(`/api/v1/model-configs/${id}/status`, data),
  getModelProviders: () => request.get('/api/v1/model-configs/providers'),
  testModelConnection: (id) => request.post(`/api/v1/model-configs/${id}/test`),
  chatWithModel: (id, data = {}) => request.post(`/api/v1/model-configs/${id}/chat`, data),
  batchUpdateAIModels: (data = {}) => request.post('/api/v1/model-configs/batch/update', data),
  batchDeleteAIModels: (data = {}) => request.post('/api/v1/model-configs/batch/delete', data),
  exportAIModels: (params = {}) => request.get('/api/v1/model-configs/export', { params, responseType: 'blob' }),

  // ==================== TestReport模块 ====================
  // 测试报告管理
  getTestReportList: (params = {}) => request.get('/api/v1/test-reports/', { params }),
  getTestReportById: (id) => request.get(`/api/v1/test-reports/${id}`),
  createTestReport: (data = {}) => request.post('/api/v1/test-reports/', data),
  updateTestReport: (id, data = {}) => request.put(`/api/v1/test-reports/${id}`, data),
  deleteTestReport: (id) => request.delete(`/api/v1/test-reports/${id}`),
  searchTestReports: (data = {}) => request.post('/api/v1/test-reports/search', data),
  getTestReportStatistics: () => request.get('/api/v1/test-reports/statistics/overview'),
  exportTestReport: (id) => request.get(`/api/v1/test-reports/${id}/export`, { responseType: 'blob' }),

  // ==================== Dashboard模块 ====================
  // 仪表板数据
  getDashboardStatistics: (data = {}) => request.post('/api/v1/dashboard/get-statistics-data', data),
  getSystemInfo: (data = {}) => request.post('/api/v1/dashboard/get-system-info', data),
  getDashboardOverview: (data = {}) => request.post('/api/v1/dashboard/get-overview-data', data),

  // ==================== Log模块 ====================
  // 日志管理
  getLogList: (params = {}) => request.get('/api/v1/logs/', { params }),
  getLogById: (id) => request.get(`/api/v1/logs/${id}`),
  searchLogs: (data = {}) => request.post('/api/v1/logs/search', data),
  getLogStatistics: () => request.get('/api/v1/logs/statistics/overview'),
  exportLogs: (params = {}) => request.get('/api/v1/logs/export', { params, responseType: 'blob' }),
  clearLogs: () => request.delete('/api/v1/logs/clear'),

  // ==================== Chat模块 ====================
  // AI聊天
  sendChatMessage: (sessionId, data = {}) => request.post(`/api/v1/chat/sessions/${sessionId}/messages`, data),
  getChatMessages: (sessionId, params = {}) => request.get(`/api/v1/chat/sessions/${sessionId}/messages`, { params }),
  getChatSessionList: (params = {}) => request.get('/api/v1/chat/sessions', { params }),
  createChatSession: (data = {}) => request.post('/api/v1/chat/sessions', data),
  deleteChatSession: (sessionId) => request.delete(`/api/v1/chat/sessions/${sessionId}`),
  clearChatHistory: () => request.post('/api/v1/chat/clear'),

  // ==================== Knowledge模块 ====================
  // 知识库管理
  getKnowledgeList: (params = {}) => request.get('/api/v1/knowledge/', { params }),
  getKnowledgeById: (id) => request.get(`/api/v1/knowledge/${id}`),
  createKnowledge: (data = {}) => request.post('/api/v1/knowledge/', data),
  updateKnowledge: (id, data = {}) => request.put(`/api/v1/knowledge/${id}`, data),
  deleteKnowledge: (id) => request.delete(`/api/v1/knowledge/${id}`),
  searchKnowledge: (data = {}) => request.post('/api/v1/knowledge/search', data),
}
