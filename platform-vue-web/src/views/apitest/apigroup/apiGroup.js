import axios from 'axios'

const API_BASE_URL = '/api/ApiGroup'

// 分页查询分组
export const queryGroupByPage = (data) => {
    return axios.post(`${API_BASE_URL}/queryByPage`, data)
}

// 根据ID查询分组
export const getGroupById = (id) => {
    return axios.get(`${API_BASE_URL}/queryById`, {
        params: { id }
    })
}

// 新增分组
export const createGroup = (data) => {
    return axios.post(`${API_BASE_URL}/add`, data)
}

// 更新分组
export const updateGroup = (id, data) => {
    return axios.post(`${API_BASE_URL}/update`, data)
}

// 删除分组
export const deleteGroup = (id) => {
    return axios.delete(`${API_BASE_URL}/delete`, {
        params: { id }
    })
}

// 获取项目下的分组树
export const getGroupTree = (projectId) => {
    return axios.get(`${API_BASE_URL}/tree`, {
        params: { project_id: projectId }
    })
}

