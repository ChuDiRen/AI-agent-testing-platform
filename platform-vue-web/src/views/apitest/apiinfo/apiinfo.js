import axios from '~/axios'

const module_name = "ApiInfo" // 模块名称

// 分页查询接口信息
export function queryByPage(data) {
    return axios.post(`/${module_name}/queryByPage?_alias=apiinfo-page`, data)
}

// 根据ID查询接口信息
export function queryById(id) {
    return axios.get(`/${module_name}/queryById?id=${id}&_alias=apiinfo-detail`)
}

// 新增接口信息
export function insertData(data) {
    return axios.post(`/${module_name}/insert?_alias=apiinfo-insert`, data)
}

// 更新接口信息
export function updateData(data) {
    return axios.put(`/${module_name}/update?_alias=apiinfo-update`, data)
}

// 删除接口信息
export function deleteData(id) {
    return axios.delete(`/${module_name}/delete?id=${id}&_alias=apiinfo-delete`)
}

// 批量删除接口信息
export function batchDeleteData(ids) {
    return axios.post(`/${module_name}/batchDelete?_alias=apiinfo-batch-delete`, { ids })
}

// 根据项目ID获取接口列表
export function getByProject(projectId) {
    return axios.get(`/${module_name}/getByProject?project_id=${projectId}&_alias=apiinfo-by-project`)
}

// 获取所有请求方法
export function getMethods() {
    return axios.get(`/${module_name}/getMethods?_alias=apiinfo-methods`)
}

// 查询所有接口信息
export function queryAll() {
    return axios.get(`/${module_name}/queryAll?_alias=apiinfo-all`)
}

// 导入Swagger
export function importSwagger(data) {
    return axios.post(`/${module_name}/importSwagger?_alias=apiinfo-import`, data)
}

// 接口调试
export function debugApi(data) {
    return axios.post(`/${module_name}/debug?_alias=apiinfo-debug`, data)
}

// 发送请求并下载
export function debugAndDownload(data) {
    return axios.post(`/${module_name}/debugAndDownload?_alias=apiinfo-download`, data)
}
