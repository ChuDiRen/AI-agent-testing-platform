import axios from '~/axios'

// 模块名 - 和后台对应
const module_name = "WebHistory"

// ==================== Web测试历史相关接口 ====================

/**
 * 获取执行历史
 * @param {Object} params - 查询参数
 * @param {Number} params.page - 页码，默认1
 * @param {Number} params.pageSize - 每页数量，默认10
 * @param {Number} params.project_id - 项目ID
 * @param {String} params.execution_name - 执行名称（模糊查询）
 * @param {String} params.status - 状态过滤
 * @param {String} params.env - 环境过滤
 * @param {String} params.executor - 执行人过滤
 * @param {String} params.start_date - 开始日期
 * @param {String} params.end_date - 结束日期
 * @returns {Promise}
 */
export function getExecutionHistory(params) {
  return axios.post(`/${module_name}/queryByPage?_alias=web-history`, params)
}

/**
 * 获取执行详情
 * @param {String} id - 执行ID
 * @returns {Promise}
 */
export function getExecutionDetail(id) {
  return axios.get(`/${module_name}/queryById?_alias=web-history-detail`, { params: { id } })
}

/**
 * 获取执行用例详情
 * @param {String} executionId - 执行ID
 * @returns {Promise}
 */
export function getExecutionCases(executionId) {
  return axios.get(`/${module_name}/queryCases?_alias=web-history-cases`, { params: { execution_id: executionId } })
}

/**
 * 获取执行统计
 * @param {Object} params - 查询参数
 * @param {Number} params.project_id - 项目ID
 * @param {Number} params.days - 统计天数，默认7
 * @param {String} params.env - 环境过滤
 * @returns {Promise}
 */
export function getExecutionStats(params) {
  return axios.get(`/${module_name}/getStatistics?_alias=web-history-stats`, { params })
}

/**
 * 删除执行历史
 * @param {String} id - 执行ID
 * @returns {Promise}
 */
export function deleteExecutionHistory(id) {
  return axios.delete(`/${module_name}/delete?_alias=web-history-delete`, { params: { id } })
}

/**
 * 批量删除执行历史
 * @param {Array} ids - 执行ID列表
 * @returns {Promise}
 */
export function batchDeleteExecutionHistory(ids) {
  return axios.delete(`/${module_name}/batchDelete?_alias=web-history-batch-delete`, { data: { ids } })
}

// ==================== 高级功能接口 ====================

/**
 * 获取执行趋势统计
 * @param {Object} params - 查询参数
 * @param {Number} params.project_id - 项目ID
 * @param {Number} params.days - 统计天数，默认30
 * @param {String} params.group_by - 分组方式：day/week/month
 * @returns {Promise}
 */
export function getExecutionTrends(params) {
  return axios.get(`/${module_name}/trends?_alias=web-history-trends`, { params })
}

/**
 * 获取执行失败分析
 * @param {Object} params - 查询参数
 * @param {Number} params.project_id - 项目ID
 * @param {Number} params.days - 统计天数，默认7
 * @returns {Promise}
 */
export function getFailureAnalysis(params) {
  return axios.get(`/${module_name}/failureAnalysis?_alias=web-history-failure`, { params })
}

/**
 * 获取执行性能统计
 * @param {Object} params - 查询参数
 * @param {Number} params.project_id - 项目ID
 * @param {Number} params.days - 统计天数，默认7
 * @returns {Promise}
 */
export function getPerformanceStats(params) {
  return axios.get(`/${module_name}/performance?_alias=web-history-performance`, { params })
}

/**
 * 导出执行历史
 * @param {Object} params - 导出参数
 * @param {Array} params.execution_ids - 执行ID列表
 * @param {String} params.format - 导出格式：json/xlsx/csv
 * @param {Boolean} params.include_cases - 是否包含用例详情
 * @returns {Promise}
 */
export function exportExecutionHistory(params) {
  return axios.post(`/${module_name}/export?_alias=web-history-export`, params)
}

/**
 * 重新执行历史记录
 * @param {String} executionId - 执行ID
 * @param {Object} options - 执行选项
 * @param {Boolean} options.only_failed - 是否只重跑失败的用例
 * @param {Boolean} options.generate_report - 是否生成报告
 * @returns {Promise}
 */
export function reExecuteHistory(executionId, options = {}) {
  return axios.post(`/${module_name}/reExecute?_alias=web-history-reexecute`, {
    execution_id: executionId,
    only_failed: options.only_failed || false,
    generate_report: options.generate_report !== false
  })
}

/**
 * 获取执行对比
 * @param {Object} params - 对比参数
 * @param {Array} params.execution_ids - 执行ID列表（最多2个）
 * @returns {Promise}
 */
export function compareExecutions(params) {
  return axios.post(`/${module_name}/compare?_alias=web-history-compare`, params)
}

/**
 * 获取执行日志
 * @param {String} executionId - 执行ID
 * @param {Object} options - 查询选项
 * @param {String} options.level - 日志级别：debug/info/warn/error
 * @param {Number} options.limit - 日志条数限制
 * @returns {Promise}
 */
export function getExecutionLogs(executionId, options = {}) {
  const params = { execution_id: executionId }
  if (options.level) {
    params.level = options.level
  }
  if (options.limit) {
    params.limit = options.limit
  }
  return axios.get(`/${module_name}/logs?_alias=web-history-logs`, { params })
}

/**
 * 获取执行截图
 * @param {String} executionId - 执行ID
 * @param {String} caseId - 用例ID（可选）
 * @returns {Promise}
 */
export function getExecutionScreenshots(executionId, caseId = null) {
  const params = { execution_id: executionId }
  if (caseId) {
    params.case_id = caseId
  }
  return axios.get(`/${module_name}/screenshots?_alias=web-history-screenshots`, { params })
}

/**
 * 清理历史记录
 * @param {Object} params - 清理参数
 * @param {Number} params.project_id - 项目ID
 * @param {Number} params.days - 保留天数
 * @param {Boolean} params.only_failed - 是否只清理失败的记录
 * @returns {Promise}
 */
export function cleanupHistory(params) {
  return axios.post(`/${module_name}/cleanup?_alias=web-history-cleanup`, params)
}

// 创建执行记录（内部使用）
export function createExecutionHistory(data) {
  return axios.post('/WebHistory/insert', data)
}

// 更新执行记录（内部使用）
export function updateExecutionHistory(data) {
  return axios.put('/WebHistory/update', data)
}
