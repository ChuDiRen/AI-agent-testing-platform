import axios from '~/axios'  // 修复：使用配置好的axios实例

const API_BASE_URL = '/ApiTest'  // 修复：移除/api前缀，因为axios已经配置了baseURL

// 执行接口测试
export const executeApiTest = (data) => {
    return axios.post(`${API_BASE_URL}/execute`, data)
}

// 查询测试状态
export const getTestStatus = (testId) => {
    return axios.get(`${API_BASE_URL}/status`, {
        params: { test_id: testId }
    })
}

// 分页查询测试历史
export const queryTestHistoryByPage = (data) => {
    return axios.post(`${API_BASE_URL}/queryByPage`, data)
}

// 根据ID查询测试历史
export const getTestHistoryById = (id) => {
    return axios.get(`${API_BASE_URL}/queryById`, {
        params: { id }
    })
}

// 删除测试历史
export const deleteTestHistory = (id) => {
    return axios.delete(`${API_BASE_URL}/delete`, {
        params: { id }
    })
}

