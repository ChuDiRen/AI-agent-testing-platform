import axios from "~/axios"

// 模块名 - 和后台对应
const module_name = "ApiKeyWord"

// 标准 - 增删改查接口调用
export function queryByPage(data) {
    return axios.post(`/${module_name}/queryByPage?_alias=keyword-page`, data)
}

export function queryById(id) {
    return axios.get(`/${module_name}/queryById?id=${id}&_alias=keyword-detail`)
}

export function insertData(data) {
    return axios.post(`/${module_name}/insert?_alias=keyword-insert`, data)
}

export function updateData(data) {
    return axios.put(`/${module_name}/update?_alias=keyword-update`, data)
}

export function deleteData(id) {
    return axios.delete(`/${module_name}/delete?id=${id}&_alias=keyword-delete`)
}

// 拓展其他方法
export function queryAll() {
    return axios.get(`/${module_name}/queryAll?_alias=keyword-all`)
}

//  扩展：生成关键字文件接口
export function keywordFile(data) {
    return axios.post(`/${module_name}/keywordFile?_alias=keyword-file`, data)
}

// 从执行引擎同步关键字
export function syncFromPlugin(pluginId) {
    return axios.post(`/${module_name}/syncFromPlugin?plugin_id=${pluginId}&_alias=keyword-sync`)
}

// 根据插件查询关键字
export function queryByPlugin(pluginId, pluginCode) {
    const params = new URLSearchParams()
    if (pluginId) params.append('plugin_id', pluginId)
    if (pluginCode) params.append('plugin_code', pluginCode)
    return axios.get(`/${module_name}/queryByPlugin?${params.toString()}&_alias=keyword-by-plugin`)
}

// 批量删除关键字
export function batchDelete(ids) {
    return axios.delete(`/${module_name}/batchDelete?ids=${ids}&_alias=keyword-batch-delete`)
}

// 批量导入关键字
export function batchImport(fileContent) {
    return axios.post(`/${module_name}/batchImport?file=${encodeURIComponent(fileContent)}&_alias=keyword-batch-import`)
}

// 批量导出关键字
export function batchExport(ids = null, format = 'json') {
    let url = `/${module_name}/batchExport?format=${format}&_alias=keyword-batch-export`
    if (ids) {
        url += `&ids=${ids}`
    }
    return axios.get(url)
}