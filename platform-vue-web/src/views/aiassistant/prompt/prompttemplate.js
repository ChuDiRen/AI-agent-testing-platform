// 提示词模板管理API服务
import request from '@/axios'

// 分页查询提示词模板
export function queryByPage(params) {
    return request({
        url: '/PromptTemplate/queryByPage',
        method: 'get',
        params
    })
}

// 根据ID查询提示词模板
export function queryById(id) {
    return request({
        url: `/PromptTemplate/queryById/${id}`,
        method: 'get'
    })
}

// 新增提示词模板
export function insertData(data) {
    return request({
        url: '/PromptTemplate/insert',
        method: 'post',
        data
    })
}

// 更新提示词模板
export function updateData(data) {
    return request({
        url: '/PromptTemplate/update',
        method: 'put',
        data
    })
}

// 删除提示词模板
export function deleteData(id) {
    return request({
        url: `/PromptTemplate/delete/${id}`,
        method: 'delete'
    })
}

// 激活/停用提示词模板
export function toggleActive(id, isActive) {
    return request({
        url: `/PromptTemplate/toggle/${id}`,
        method: 'put',
        params: { is_active: isActive }
    })
}

// 按类型查询模板
export function queryByTestType(testType) {
    return request({
        url: '/PromptTemplate/by-test-type',
        method: 'get',
        params: { test_type: testType }
    })
}

