import axios from "~/axios"

// 模块名 - 和后台对应
const module_name = "Generator"

// 预览生成代码
export function previewCode(data) {
    return axios.post(`/${module_name}/preview?_alias=generator-preview`, data)
}

// 下载生成代码
export function downloadCode(data) {
    return axios.post(`/${module_name}/download?_alias=generator-download`, data, {
        responseType: 'blob'
    })
}

// 批量下载代码
export function batchDownload(data) {
    return axios.post(`/${module_name}/batchDownload?_alias=generator-batch-download`, data, {
        responseType: 'blob'
    })
}

// 获取生成历史
export function getHistory(data) {
    return axios.get(`/${module_name}/history?_alias=generator-history`, { params: data })
}

// 删除生成历史
export function deleteHistory(id) {
    return axios.delete(`/${module_name}/history?id=${id}&_alias=generator-history-delete`)
}
