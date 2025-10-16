// AI模型管理API服务
import request from '@/axios'

// 分页查询AI模型
export function queryByPage(params) {
    return request({
        url: '/AiModel/queryByPage',
        method: 'get',
        params
    })
}

// 根据ID查询AI模型
export function queryById(id) {
    return request({
        url: `/AiModel/queryById/${id}`,
        method: 'get'
    })
}

// 新增AI模型
export function insertData(data) {
    return request({
        url: '/AiModel/insert',
        method: 'post',
        data
    })
}

// 更新AI模型
export function updateData(data) {
    return request({
        url: '/AiModel/update',
        method: 'put',
        data
    })
}

// 删除AI模型
export function deleteData(id) {
    return request({
        url: `/AiModel/delete/${id}`,
        method: 'delete'
    })
}

// 启用/禁用AI模型
export function toggleEnable(id, isEnabled) {
    return request({
        url: `/AiModel/toggle/${id}`,
        method: 'put',
        params: { is_enabled: isEnabled }
    })
}

// 测试AI模型连接
export function testConnection(id) {
    return request({
        url: `/AiModel/test/${id}`,
        method: 'post'
    })
}

