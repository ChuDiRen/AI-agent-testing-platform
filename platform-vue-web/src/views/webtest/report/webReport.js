import axios from '~/axios'

// 模块名 - 和后台对应
const module_name = "WebReport"

// ==================== Web测试报告相关接口 ====================

/**
 * 获取报告数据
 * @param {String} executionId - 执行ID
 * @returns {Promise}
 */
export function getReportData(executionId) {
  return axios.get(`/${module_name}/getReportData/${executionId}?_alias=web-report-data`)
}

/**
 * 获取Allure报告链接
 * @param {String} executionId - 执行ID
 * @returns {Promise}
 */
export function getAllureUrl(executionId) {
  return axios.get(`/${module_name}/allure/${executionId}?_alias=web-report-allure`)
}

/**
 * 下载报告
 * @param {String} executionId - 执行ID
 * @param {String} format - 下载格式，默认html
 * @returns {Promise}
 */
export function downloadReport(executionId, format = 'html') {
  return axios.get(`/${module_name}/download/${executionId}?_alias=web-report-download`, { 
    params: { format },
    responseType: 'blob'
  })
}

/**
 * 查看报告
 * @param {String} reportId - 报告ID
 * @returns {Promise}
 */
export function viewReport(reportId) {
  return axios.get(`/${module_name}/view/${reportId}?_alias=web-report-view`)
}

/**
 * 获取报告列表
 * @param {Object} params - 查询参数
 * @param {Number} params.page - 页码，默认1
 * @param {Number} params.pageSize - 每页数量，默认10
 * @param {Number} params.project_id - 项目ID
 * @param {String} params.execution_id - 执行ID
 * @param {String} params.status - 状态过滤
 * @param {String} params.format - 格式过滤
 * @param {String} params.start_date - 开始日期
 * @param {String} params.end_date - 结束日期
 * @returns {Promise}
 */
export function getReportList(params) {
  return axios.post(`/${module_name}/queryByPage?_alias=web-reports`, params)
}

/**
 * 获取报告详情
 * @param {String} reportId - 报告ID
 * @returns {Promise}
 */
export function getReportDetail(reportId) {
  return axios.get(`/${module_name}/queryById?_alias=web-report-detail`, { params: { id: reportId } })
}

/**
 * 生成报告
 * @param {Object} data - 生成参数
 * @param {String} data.execution_id - 执行ID
 * @param {String} data.format - 报告格式：html/pdf/json/allure
 * @param {Boolean} data.include_screenshots - 是否包含截图
 * @param {Boolean} data.include_steps - 是否包含步骤详情
 * @param {Boolean} data.include_charts - 是否包含图表
 * @returns {Promise}
 */
export function generateReport(data) {
  return axios.post(`/${module_name}/generate?_alias=web-report-generate`, data)
}

/**
 * 删除报告
 * @param {String} reportId - 报告ID
 * @returns {Promise}
 */
export function deleteReport(reportId) {
  return axios.delete(`/${module_name}/delete?_alias=web-report-delete`, { params: { id: reportId } })
}

/**
 * 批量删除报告
 * @param {Array} reportIds - 报告ID列表
 * @returns {Promise}
 */
export function batchDeleteReports(reportIds) {
  return axios.delete(`/${module_name}/batchDelete?_alias=web-reports-batch-delete`, { data: { ids: reportIds } })
}

/**
 * 获取报告统计
 * @param {Object} params - 查询参数
 * @param {Number} params.project_id - 项目ID
 * @param {Number} params.days - 统计天数，默认30
 * @returns {Promise}
 */
export function getReportStats(params) {
  return axios.get(`/${module_name}/getStatistics?_alias=web-reports-stats`, { params })
}

// ==================== 高级功能接口 ====================

/**
 * 获取报告模板列表
 * @param {Object} params - 查询参数
 * @param {Boolean} params.active_only - 是否只获取激活的模板
 * @returns {Promise}
 */
export function getReportTemplates(params = {}) {
  return axios.get(`/${module_name}/templates?_alias=web-report-templates`, { params })
}

/**
 * 创建报告模板
 * @param {Object} data - 模板数据
 * @param {String} data.name - 模板名称
 * @param {String} data.description - 模板描述
 * @param {String} data.template_type - 模板类型：html/pdf/json
 * @param {String} data.template_content - 模板内容
 * @param {String} data.css_styles - CSS样式
 * @param {String} data.js_scripts - JavaScript脚本
 * @param {Boolean} data.is_default - 是否默认模板
 * @returns {Promise}
 */
export function createReportTemplate(data) {
  return axios.post(`/${module_name}/template/insert?_alias=web-report-template-create`, data)
}

/**
 * 更新报告模板
 * @param {Object} data - 模板数据
 * @param {Number} data.id - 模板ID
 * @returns {Promise}
 */
export function updateReportTemplate(data) {
  return axios.put(`/${module_name}/template/update?_alias=web-report-template-update`, data)
}

/**
 * 删除报告模板
 * @param {Number} templateId - 模板ID
 * @returns {Promise}
 */
export function deleteReportTemplate(templateId) {
  return axios.delete(`/${module_name}/template/delete?_alias=web-report-template-delete`, { params: { id: templateId } })
}

/**
 * 预览报告模板
 * @param {Object} data - 预览数据
 * @param {Number} data.template_id - 模板ID
 * @param {String} data.execution_id - 执行ID（用于数据预览）
 * @returns {Promise}
 */
export function previewReportTemplate(data) {
  return axios.post(`/${module_name}/template/preview?_alias=web-report-template-preview`, data)
}

/**
 * 获取报告配置
 * @param {Number} projectId - 项目ID
 * @returns {Promise}
 */
export function getReportConfig(projectId) {
  return axios.get(`/${module_name}/config?_alias=web-report-config`, {
    params: { project_id: projectId }
  })
}

/**
 * 更新报告配置
 * @param {Object} data - 配置数据
 * @param {Number} data.project_id - 项目ID
 * @param {Object} data.config_data - 配置内容
 * @returns {Promise}
 */
export function updateReportConfig(data) {
  return axios.post(`/${module_name}/config/update?_alias=web-report-config-update`, data)
}

/**
 * 分享报告
 * @param {Object} data - 分享数据
 * @param {String} data.report_id - 报告ID
 * @param {Number} data.expire_hours - 过期小时数，默认24
 * @param {Boolean} data.require_password - 是否需要密码
 * @param {String} data.password - 分享密码
 * @returns {Promise}
 */
export function shareReport(data) {
  return axios.post(`/${module_name}/share?_alias=web-report-share`, data)
}

/**
 * 获取分享报告
 * @param {String} shareToken - 分享令牌
 * @returns {Promise}
 */
export function getSharedReport(shareToken) {
  return axios.get(`/${module_name}/shared/${shareToken}?_alias=web-report-shared`)
}

/**
 * 获取报告评论
 * @param {String} reportId - 报告ID
 * @returns {Promise}
 */
export function getReportComments(reportId) {
  return axios.get(`/${module_name}/comments?_alias=web-report-comments`, {
    params: { report_id: reportId }
  })
}

/**
 * 添加报告评论
 * @param {Object} data - 评论数据
 * @param {String} data.report_id - 报告ID
 * @param {String} data.content - 评论内容
 * @param {String} data.comment_type - 评论类型
 * @returns {Promise}
 */
export function addReportComment(data) {
  return axios.post(`/${module_name}/comment/insert?_alias=web-report-comment-add`, data)
}

/**
 * 邮件发送报告
 * @param {Object} data - 发送数据
 * @param {String} data.report_id - 报告ID
 * @param {Array} data.recipients - 收件人列表
 * @param {String} data.subject - 邮件主题
 * @param {String} data.content - 邮件内容
 * @param {Boolean} data.include_attachment - 是否包含附件
 * @returns {Promise}
 */
export function emailReport(data) {
  return axios.post(`/${module_name}/email?_alias=web-report-email`, data)
}

/**
 * 获取报告访问日志
 * @param {String} reportId - 报告ID
 * @param {Object} params - 查询参数
 * @param {Number} params.page - 页码，默认1
 * @param {Number} params.pageSize - 每页数量，默认20
 * @returns {Promise}
 */
export function getReportAccessLogs(reportId, params = {}) {
  return axios.get(`/${module_name}/accessLogs?_alias=web-report-logs`, {
    params: { report_id: reportId, ...params }
  })
}
