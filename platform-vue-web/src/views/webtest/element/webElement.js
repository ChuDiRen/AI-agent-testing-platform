import axios from '~/axios'

// 模块名 - 和后台对应
const module_name = "WebElement"

// ==================== Web元素管理相关接口 ====================

/**
 * 获取元素列表
 * @param {Object} params - 查询参数
 * @param {Number} params.page - 页码，默认1
 * @param {Number} params.pageSize - 每页数量，默认10
 * @param {Number} params.project_id - 项目ID
 * @param {String} params.module - 所属模块
 * @param {String} params.name - 元素名称（模糊查询）
 * @param {String} params.locator_type - 定位器类型
 * @param {String} params.status - 状态过滤
 * @returns {Promise}
 */
export function getElementList(params) {
  return axios.post(`/${module_name}/queryByPage?_alias=web-elements`, params)
}

/**
 * 获取元素详情
 * @param {Number} id - 元素ID
 * @returns {Promise}
 */
export function getElementById(id) {
  return axios.get(`/${module_name}/queryById?_alias=web-element-detail`, { params: { id } })
}

/**
 * 保存元素（新增/更新）
 * @param {Object} data - 元素数据
 * @param {Number} data.id - 元素ID（更新时必需）
 * @param {String} data.name - 元素名称
 * @param {String} data.description - 元素描述
 * @param {Number} data.project_id - 项目ID
 * @param {String} data.module - 所属模块
 * @param {String} data.page_name - 页面名称
 * @param {String} data.element_type - 元素类型
 * @param {String} data.locator_type - 定位器类型
 * @param {String} data.locator_value - 定位器值
 * @param {String} data.locator_strategy - 定位策略
 * @param {String} data.timeout - 超时时间（秒）
 * @param {String} data.priority - 优先级
 * @param {String} data.status - 状态
 * @param {String} data.tags - 标签
 * @returns {Promise}
 */
export function saveElement(data) {
  if (data.id) {
    return axios.put(`/${module_name}/update?_alias=web-element-update`, data)
  }
  return axios.post(`/${module_name}/insert?_alias=web-element-create`, data)
}

/**
 * 删除元素
 * @param {Number} id - 元素ID
 * @returns {Promise}
 */
export function deleteElement(id) {
  return axios.delete(`/${module_name}/delete?_alias=web-element-delete`, { params: { id } })
}

/**
 * 批量删除元素
 * @param {Array} ids - 元素ID列表
 * @returns {Promise}
 */
export function batchDeleteElement(ids) {
  return axios.delete(`/${module_name}/batchDelete?_alias=web-elements-batch-delete`, { data: { ids } })
}

/**
 * 导入元素
 * @param {FormData} formData - 表单数据，包含元素文件
 * @param {Number} formData.project_id - 项目ID
 * @returns {Promise}
 */
export function importElements(formData) {
  return axios.post(`/${module_name}/import?_alias=web-elements-import`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

/**
 * 导出元素
 * @param {Array} ids - 元素ID列表
 * @param {String} format - 导出格式：json/yaml/xlsx
 * @returns {Promise}
 */
export function exportElements(ids, format = 'json') {
  return axios.post(`/${module_name}/export?_alias=web-elements-export`, { 
    ids, 
    format 
  })
}

/**
 * 按模块获取元素
 * @param {String} module - 模块名称
 * @param {Number} projectId - 项目ID（可选）
 * @returns {Promise}
 */
export function getElementsByModule(module, projectId = null) {
  const params = { module }
  if (projectId) {
    params.project_id = projectId
  }
  return axios.get(`/${module_name}/queryByModule?_alias=web-elements-by-module`, { params })
}

// ==================== 高级功能接口 ====================

/**
 * 验证元素定位器
 * @param {Object} data - 验证数据
 * @param {String} data.locator_type - 定位器类型
 * @param {String} data.locator_value - 定位器值
 * @param {String} data.page_url - 页面URL
 * @param {String} data.browser_type - 浏览器类型
 * @returns {Promise}
 */
export function validateElementLocator(data) {
  return axios.post(`/${module_name}/validateLocator?_alias=web-element-validate`, data)
}

/**
 * 批量验证元素定位器
 * @param {Array} elements - 元素列表
 * @returns {Promise}
 */
export function batchValidateElementLocators(elements) {
  return axios.post(`/${module_name}/batchValidate?_alias=web-elements-batch-validate`, {
    elements
  })
}

/**
 * 获取元素使用统计
 * @param {Object} params - 查询参数
 * @param {Number} params.project_id - 项目ID
 * @param {String} params.module - 模块过滤
 * @param {Number} params.days - 统计天数，默认7
 * @returns {Promise}
 */
export function getElementStatistics(params) {
  return axios.get(`/${module_name}/statistics?_alias=web-elements-stats`, { params })
}

/**
 * 同步元素到页面
 * @param {Object} data - 同步数据
 * @param {Array} data.element_ids - 元素ID列表
 * @param {String} data.page_url - 页面URL
 * @returns {Promise}
 */
export function syncElementsToPage(data) {
  return axios.post(`/${module_name}/syncToPage?_alias=web-elements-sync`, data)
}

/**
 * 获取元素依赖关系
 * @param {Number} elementId - 元素ID
 * @returns {Promise}
 */
export function getElementDependencies(elementId) {
  return axios.get(`/${module_name}/dependencies?_alias=web-element-dependencies`, {
    params: { element_id: elementId }
  })
}

/**
 * 搜索元素
 * @param {Object} params - 搜索参数
 * @param {String} params.keyword - 搜索关键词
 * @param {Number} params.project_id - 项目ID
 * @param {String} params.module - 模块过滤
 * @param {String} params.element_type - 元素类型过滤
 * @returns {Promise}
 */
export function searchElements(params) {
  return axios.post(`/${module_name}/search?_alias=web-elements-search`, params)
}
