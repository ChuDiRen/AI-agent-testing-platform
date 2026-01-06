import axios from '~/axios'

// 模块名 - 和后台对应
const module_name = "WebKeyword"

// ==================== Web关键字管理相关接口 ====================

/**
 * 获取关键字列表
 * @param {Object} params - 查询参数
 * @param {Number} params.page - 页码，默认1
 * @param {Number} params.pageSize - 每页数量，默认10
 * @param {String} params.name - 关键字名称（模糊查询）
 * @param {String} params.category - 分类过滤
 * @param {Boolean} params.is_builtin - 是否内置关键字
 * @param {Boolean} params.is_active - 是否启用
 * @param {String} params.author - 作者过滤
 * @returns {Promise}
 */
export function getKeywordList(params) {
  return axios.post(`/${module_name}/queryByPage?_alias=web-keywords`, params)
}

/**
 * 获取关键字详情
 * @param {Number} id - 关键字ID
 * @returns {Promise}
 */
export function getKeywordById(id) {
  return axios.get(`/${module_name}/queryById?_alias=web-keyword-detail`, { params: { id } })
}

/**
 * 保存关键字（新增/更新）
 * @param {Object} data - 关键字数据
 * @param {Number} data.id - 关键字ID（更新时必需）
 * @param {String} data.name - 关键字名称
 * @param {String} data.description - 关键字描述
 * @param {String} data.category - 分类
 * @param {String} data.keyword_type - 关键字类型：action/assertion/utility
 * @param {String} data.python_code - Python代码
 * @param {String} data.parameters - 参数定义
 * @param {String} data.return_type - 返回类型
 * @param {String} data.example_usage - 使用示例
 * @param {String} data.documentation - 文档说明
 * @param {String} data.tags - 标签
 * @param {Boolean} data.is_builtin - 是否内置关键字
 * @param {Boolean} data.is_active - 是否启用
 * @returns {Promise}
 */
export function saveKeyword(data) {
  if (data.id) {
    return axios.put(`/${module_name}/update?_alias=web-keyword-update`, data)
  }
  return axios.post(`/${module_name}/insert?_alias=web-keyword-create`, data)
}

/**
 * 删除关键字
 * @param {Number} id - 关键字ID
 * @returns {Promise}
 */
export function deleteKeyword(id) {
  return axios.delete(`/${module_name}/delete?_alias=web-keyword-delete`, { params: { id } })
}

/**
 * 批量删除关键字
 * @param {Array} ids - 关键字ID列表
 * @returns {Promise}
 */
export function batchDeleteKeyword(ids) {
  return axios.delete(`/${module_name}/batchDelete?_alias=web-keywords-batch-delete`, { data: { ids } })
}

/**
 * 生成关键字文件
 * @param {Object} data - 生成参数
 * @param {Array} data.keyword_ids - 关键字ID列表
 * @param {String} data.file_type - 文件类型：py/js/ts
 * @param {String} data.output_path - 输出路径
 * @param {Boolean} data.include_docs - 是否包含文档
 * @returns {Promise}
 */
export function generateKeywordFile(data) {
  return axios.post(`/${module_name}/generateFile?_alias=web-keywords-generate`, data)
}

/**
 * 导入关键字
 * @param {FormData} formData - 表单数据，包含关键字文件
 * @returns {Promise}
 */
export function importKeywords(formData) {
  return axios.post(`/${module_name}/import?_alias=web-keywords-import`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

/**
 * 导出关键字
 * @param {Array} ids - 关键字ID列表
 * @param {String} format - 导出格式：json/yaml/py
 * @returns {Promise}
 */
export function exportKeywords(ids, format = 'json') {
  return axios.post(`/${module_name}/export?_alias=web-keywords-export`, {
    ids,
    format
  })
}

// ==================== 高级功能接口 ====================

/**
 * 验证关键字代码
 * @param {Object} data - 验证数据
 * @param {String} data.python_code - Python代码
 * @param {String} data.keyword_type - 关键字类型
 * @param {String} data.parameters - 参数定义
 * @returns {Promise}
 */
export function validateKeywordCode(data) {
  return axios.post(`/${module_name}/validate?_alias=web-keyword-validate`, data)
}

/**
 * 测试关键字执行
 * @param {Object} data - 测试数据
 * @param {Number} data.keyword_id - 关键字ID
 * @param {Object} data.test_params - 测试参数
 * @param {String} data.browser_type - 浏览器类型
 * @returns {Promise}
 */
export function testKeywordExecution(data) {
  return axios.post(`/${module_name}/test?_alias=web-keyword-test`, data)
}

/**
 * 获取关键字统计
 * @param {Object} params - 查询参数
 * @param {String} params.category - 分类过滤
 * @param {Boolean} params.is_builtin - 是否内置关键字
 * @param {Number} params.days - 统计天数，默认7
 * @returns {Promise}
 */
export function getKeywordStatistics(params) {
  return axios.get(`/${module_name}/statistics?_alias=web-keywords-stats`, { params })
}

/**
 * 搜索关键字
 * @param {Object} params - 搜索参数
 * @param {String} params.keyword - 搜索关键词
 * @param {String} params.category - 分类过滤
 * @param {String} params.keyword_type - 关键字类型过滤
 * @param {Boolean} params.is_builtin - 是否内置关键字
 * @returns {Promise}
 */
export function searchKeywords(params) {
  return axios.post(`/${module_name}/search?_alias=web-keywords-search`, params)
}

/**
 * 获取关键字使用统计
 * @param {Number} keywordId - 关键字ID
 * @returns {Promise}
 */
export function getKeywordUsageStats(keywordId) {
  return axios.get(`/${module_name}/usageStats?_alias=web-keyword-usage`, {
    params: { keyword_id: keywordId }
  })
}

/**
 * 批量更新关键字状态
 * @param {Object} data - 更新数据
 * @param {Array} data.keyword_ids - 关键字ID列表
 * @param {Boolean} data.is_active - 是否启用
 * @returns {Promise}
 */
export function batchUpdateKeywordStatus(data) {
  return axios.post(`/${module_name}/batchUpdateStatus?_alias=web-keywords-status-update`, data)
}

/**
 * 获取关键字分类列表
 * @returns {Promise}
 */
export function getKeywordCategories() {
  return axios.get(`/${module_name}/categories?_alias=web-keywords-categories`)
}

/**
 * 克隆关键字
 * @param {Number} keywordId - 源关键字ID
 * @param {Object} options - 克隆选项
 * @param {String} options.new_name - 新关键字名称
 * @param {Boolean} options.copy_code - 是否复制代码
 * @returns {Promise}
 */
export function cloneKeyword(keywordId, options = {}) {
  return axios.post(`/${module_name}/clone?_alias=web-keyword-clone`, {
    keyword_id: keywordId,
    new_name: options.new_name,
    copy_code: options.copy_code !== false
  })
}
