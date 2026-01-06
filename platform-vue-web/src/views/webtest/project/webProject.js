import axios from '~/axios'

// 获取 Web 项目列表
export function getWebProjectList(query) {
    return axios.get('/webtest/project/list', { params: query })
}

// 获取 Web 项目详情
export function getWebProject(id) {
    return axios.get(`/webtest/project/${id}`)
}

// 新增 Web 项目
export function addWebProject(data) {
    return axios.post('/webtest/project', data)
}

// 更新 Web 项目
export function updateWebProject(id, data) {
    return axios.put(`/webtest/project/${id}`, data)
}

// 删除 Web 项目
export function deleteWebProject(id) {
    return axios.delete(`/webtest/project/${id}`)
}

// 批量删除 Web 项目
export function batchDeleteWebProject(ids) {
    return axios.delete('/webtest/project/batch', { data: { ids } })
}
