import axios from '~/axios'

// 模块名 - 和后台对应
const module_name = "WebCase"

// ==================== Web用例管理相关接口 ====================

/**
 * 获取Web用例列表
 * @param {Object} params - 查询参数
 * @param {Number} params.page - 页码，默认1
 * @param {Number} params.pageSize - 每页数量，默认10
 * @param {Number} params.project_id - 项目ID
 * @param {String} params.folder_id - 目录ID
 * @param {String} params.name - 用例名称（模糊查询）
 * @param {String} params.status - 状态过滤
 * @param {String} params.priority - 优先级过滤
 * @returns {Promise}
 */
export function getWebCaseList(params) {
  return axios.post(`/${module_name}/queryByPage?_alias=web-cases`, params)
}

/**
 * 获取Web用例目录树
 * @param {Number} projectId - 项目ID
 * @returns {Promise}
 */
export function getWebCaseTree(projectId) {
  return axios.post(`/${module_name}/queryTree?_alias=web-tree`, { project_id: projectId })
}

/**
 * 获取Web用例详情
 * @param {Number} id - 用例ID
 * @returns {Promise}
 */
export function getWebCaseById(id) {
  return axios.get(`/${module_name}/queryById?_alias=web-case-detail`, { params: { id } })
}

/**
 * 保存Web用例（新增或更新）
 * @param {Object} data - 用例数据
 * @param {Number} data.id - 用例ID（更新时必需）
 * @param {String} data.name - 用例名称
 * @param {String} data.description - 用例描述
 * @param {Number} data.project_id - 项目ID
 * @param {Number} data.folder_id - 目录ID
 * @param {String} data.content - YAML内容
 * @param {String} data.file_type - 文件类型，默认yaml
 * @param {String} data.priority - 优先级
 * @param {String} data.status - 状态
 * @param {String} data.tags - 标签
 * @param {String} data.pre_condition - 前置条件
 * @param {String} data.post_condition - 后置条件
 * @param {String} data.expected_result - 预期结果
 * @returns {Promise}
 */
export function saveWebCase(data) {
  if (data.id) {
    return axios.put(`/${module_name}/update?_alias=web-case-update`, data)
  }
  return axios.post(`/${module_name}/insert?_alias=web-case-create`, data)
}

/**
 * 删除Web用例
 * @param {Number} id - 用例ID
 * @returns {Promise}
 */
export function deleteWebCase(id) {
  return axios.delete(`/${module_name}/delete?_alias=web-case-delete`, { params: { id } })
}

/**
 * 批量删除Web用例
 * @param {Array} ids - 用例ID列表
 * @returns {Promise}
 */
export function batchDeleteWebCase(ids) {
  return axios.delete(`/${module_name}/batchDelete?_alias=web-cases-batch-delete`, { data: { ids } })
}

/**
 * 复制Web用例
 * @param {Number} id - 源用例ID
 * @param {String} newName - 新用例名称（可选）
 * @returns {Promise}
 */
export function copyCase(id, newName) {
  return axios.post(`/${module_name}/copy?_alias=web-case-copy`, {}, { 
    params: { id, new_name: newName } 
  })
}

/**
 * 导入XMind用例
 * @param {FormData} formData - 表单数据，包含XMind文件
 * @param {Number} formData.project_id - 项目ID
 * @param {Number} formData.folder_id - 目录ID
 * @returns {Promise}
 */
export function importXMindCase(formData) {
  return axios.post(`/${module_name}/importXMind?_alias=web-xmind-import`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

/**
 * 添加用例到测试计划
 * @param {Object} data - 计划数据
 * @param {Array} data.case_ids - 用例ID列表
 * @param {Number} data.plan_id - 计划ID
 * @returns {Promise}
 */
export function addCasesToPlan(data) {
  return axios.post(`/${module_name}/addToPlan?_alias=web-add-to-plan`, data)
}

// ==================== 目录管理相关接口 ====================

/**
 * 创建目录
 * @param {Object} data - 目录数据
 * @param {String} data.name - 目录名称
 * @param {Number} data.project_id - 项目ID
 * @param {Number} data.parent_id - 父目录ID
 * @returns {Promise}
 */
export function createFolder(data) {
  return axios.post(`/${module_name}/folder/insert?_alias=web-folder-create`, data)
}

/**
 * 删除目录
 * @param {Number} id - 目录ID
 * @returns {Promise}
 */
export function deleteFolder(id) {
  return axios.delete(`/${module_name}/folder/delete?_alias=web-folder-delete`, { params: { id } })
}

/**
 * 移动目录
 * @param {Number} id - 目录ID
 * @param {Number} newParentId - 新父目录ID
 * @returns {Promise}
 */
export function moveFolder(id, newParentId) {
  return axios.post(`/${module_name}/folder/move?_alias=web-folder-move`, {
    id,
    new_parent_id: newParentId
  })
}

/**
 * 批量排序目录
 * @param {Array} folderList - 目录排序列表
 * @returns {Promise}
 */
export function batchSortFolders(folderList) {
  return axios.post(`/${module_name}/folder/batchSort?_alias=web-folders-sort`, {
    folder_list: folderList
  })
}

// ==================== 高级功能接口 ====================

/**
 * 批量执行用例
 * @param {Array} caseIds - 用例ID列表
 * @param {Object} options - 执行选项
 * @param {String} options.browser_type - 浏览器类型
 * @param {String} options.environment - 执行环境
 * @param {Boolean} options.generate_report - 是否生成报告
 * @returns {Promise}
 */
export function batchExecuteCases(caseIds, options = {}) {
  return axios.post(`/${module_name}/batchExecute?_alias=web-batch-execute`, {
    case_ids: caseIds,
    browser_type: options.browser_type || 'chrome',
    environment: options.environment || 'test',
    generate_report: options.generate_report !== false
  })
}

/**
 * 验证用例语法
 * @param {String} content - YAML内容
 * @returns {Promise}
 */
export function validateCaseSyntax(content) {
  return axios.post(`/${module_name}/validate?_alias=web-validate`, {
    content
  })
}

/**
 * 预览用例执行
 * @param {Number} caseId - 用例ID
 * @param {Object} options - 预览选项
 * @param {Boolean} options.dry_run - 是否只验证不执行
 * @returns {Promise}
 */
export function previewCaseExecution(caseId, options = {}) {
  return axios.post(`/${module_name}/preview?_alias=web-preview`, {
    case_id: caseId,
    dry_run: options.dry_run !== false
  })
}

/**
 * 获取用例执行统计
 * @param {Object} params - 查询参数
 * @param {Number} params.project_id - 项目ID
 * @param {Number} params.days - 统计天数，默认7
 * @returns {Promise}
 */
export function getCaseStatistics(params) {
  return axios.get(`/${module_name}/statistics?_alias=web-stats`, { params })
}

/**
 * 导出用例
 * @param {Array} caseIds - 用例ID列表
 * @param {String} format - 导出格式：yaml/json/xlsx
 * @returns {Promise}
 */
export function exportCases(caseIds, format = 'yaml') {
  return axios.post(`/${module_name}/export?_alias=web-export`, {
    case_ids: caseIds,
    format
  })
}

/**
 * 检查用例依赖
 * @param {Number} caseId - 用例ID
 * @returns {Promise}
 */
export function checkCaseDependencies(caseId) {
  return axios.get(`/${module_name}/dependencies?_alias=web-dependencies`, {
    params: { case_id: caseId }
  })
}
