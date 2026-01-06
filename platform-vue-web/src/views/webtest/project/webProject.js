import axios from '~/axios'

// 模块名 - 和后台对应
const module_name = "WebProject"

// ==================== Web项目管理相关接口 ====================

/**
 * 获取Web项目列表
 * @param {Object} params - 查询参数
 * @param {Number} params.page - 页码，默认1
 * @param {Number} params.pageSize - 每页数量，默认10
 * @param {String} params.name - 项目名称（模糊查询）
 * @param {String} params.status - 状态过滤
 * @returns {Promise}
 */
export function getWebProjectList(params) {
    return axios.post(`/${module_name}/queryByPage?_alias=web-projects`, params)
}

/**
 * 获取所有Web项目
 * @returns {Promise}
 */
export function getWebProjects() {
    return axios.get(`/${module_name}/queryAll?_alias=web-projects-all`)
}

/**
 * 获取Web项目详情
 * @param {Number} id - 项目ID
 * @returns {Promise}
 */
export function getWebProject(id) {
    return axios.get(`/${module_name}/queryById?_alias=web-project-detail`, { params: { id } })
}

/**
 * 新增Web项目
 * @param {Object} data - 项目数据
 * @param {String} data.project_name - 项目名称
 * @param {String} data.description - 项目描述
 * @param {String} data.base_url - 基础URL
 * @param {String} data.environment - 环境配置
 * @param {String} data.browser_config - 浏览器配置
 * @param {String} data.timeout_config - 超时配置
 * @param {String} data.proxy_config - 代理配置
 * @returns {Promise}
 */
export function addWebProject(data) {
    return axios.post(`/${module_name}/insert?_alias=web-project-create`, data)
}

/**
 * 更新Web项目
 * @param {Object} data - 项目数据
 * @param {Number} data.id - 项目ID
 * @returns {Promise}
 */
export function updateWebProject(data) {
    return axios.put(`/${module_name}/update?_alias=web-project-update`, data)
}

/**
 * 删除Web项目
 * @param {Number} id - 项目ID
 * @returns {Promise}
 */
export function deleteWebProject(id) {
    return axios.delete(`/${module_name}/delete?_alias=web-project-delete`, { params: { id } })
}

/**
 * 批量删除Web项目
 * @param {Array} ids - 项目ID列表
 * @returns {Promise}
 */
export function batchDeleteWebProject(ids) {
    return axios.delete(`/${module_name}/batchDelete?_alias=web-projects-batch-delete`, { data: { ids } })
}

// ==================== 项目配置相关接口 ====================

/**
 * 获取项目配置
 * @param {Number} projectId - 项目ID
 * @returns {Promise}
 */
export function getProjectConfig(projectId) {
    return axios.get(`/${module_name}/config?_alias=web-project-config`, {
        params: { project_id: projectId }
    })
}

/**
 * 更新项目配置
 * @param {Object} data - 配置数据
 * @param {Number} data.project_id - 项目ID
 * @param {String} data.config_type - 配置类型
 * @param {Object} data.config_data - 配置内容
 * @returns {Promise}
 */
export function updateProjectConfig(data) {
    return axios.post(`/${module_name}/config/update?_alias=web-project-config-update`, data)
}

/**
 * 测试项目连接
 * @param {Number} projectId - 项目ID
 * @returns {Promise}
 */
export function testProjectConnection(projectId) {
    return axios.post(`/${module_name}/testConnection?_alias=web-project-test`, {
        project_id: projectId
    })
}

/**
 * 获取项目统计
 * @param {Number} projectId - 项目ID
 * @returns {Promise}
 */
export function getProjectStatistics(projectId) {
    return axios.get(`/${module_name}/statistics?_alias=web-project-stats`, {
        params: { project_id: projectId }
    })
}

/**
 * 克隆项目
 * @param {Number} projectId - 源项目ID
 * @param {Object} options - 克隆选项
 * @param {String} options.new_name - 新项目名称
 * @param {Boolean} options.clone_cases - 是否克隆用例
 * @param {Boolean} options.clone_elements - 是否克隆元素
 * @param {Boolean} options.clone_keywords - 是否克隆关键字
 * @returns {Promise}
 */
export function cloneProject(projectId, options = {}) {
    return axios.post(`/${module_name}/clone?_alias=web-project-clone`, {
        project_id: projectId,
        new_name: options.new_name,
        clone_cases: options.clone_cases !== false,
        clone_elements: options.clone_elements !== false,
        clone_keywords: options.clone_keywords !== false
    })
}

/**
 * 导出项目
 * @param {Number} projectId - 项目ID
 * @param {String} format - 导出格式：json/yaml/xlsx
 * @returns {Promise}
 */
export function exportProject(projectId, format = 'json') {
    return axios.post(`/${module_name}/export?_alias=web-project-export`, {
        project_id: projectId,
        format
    })
}

/**
 * 导入项目
 * @param {FormData} formData - 表单数据，包含项目文件
 * @returns {Promise}
 */
export function importProject(formData) {
    return axios.post(`/${module_name}/import?_alias=web-project-import`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
    })
}
