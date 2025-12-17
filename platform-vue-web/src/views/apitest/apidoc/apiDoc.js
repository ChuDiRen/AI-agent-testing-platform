/**
 * API文档相关接口
 */
import axios from '~/axios'

// 生成API文档
export function generateDoc(projectId, format = 'json') {
    return axios.get('/ApiDoc/generate', {
        params: { project_id: projectId, format }
    })
}

// 预览API文档
export function previewDoc(projectId) {
    return axios.get('/ApiDoc/preview', {
        params: { project_id: projectId },
        responseType: 'text'
    })
}

// 导出API文档
export function exportDoc(projectId, format = 'markdown') {
    return axios.get('/ApiDoc/export', {
        params: { project_id: projectId, format }
    })
}

// 获取接口详情文档
export function getApiDetail(apiId) {
    return axios.get('/ApiDoc/getApiDetail', {
        params: { api_id: apiId }
    })
}
