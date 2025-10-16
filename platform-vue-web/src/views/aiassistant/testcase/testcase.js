// 测试用例管理API服务
import request from '@/axios'

// 分页查询测试用例
export function queryByPage(params) {
    return request({
        url: '/TestCase/queryByPage',
        method: 'get',
        params
    })
}

// 根据ID查询测试用例
export function queryById(id) {
    return request({
        url: `/TestCase/queryById/${id}`,
        method: 'get'
    })
}

// 新增测试用例
export function insertData(data) {
    return request({
        url: '/TestCase/insert',
        method: 'post',
        data
    })
}

// 更新测试用例
export function updateData(data) {
    return request({
        url: '/TestCase/update',
        method: 'put',
        data
    })
}

// 删除测试用例
export function deleteData(id) {
    return request({
        url: `/TestCase/delete/${id}`,
        method: 'delete'
    })
}

// 批量保存测试用例
export function batchInsert(data) {
    return request({
        url: '/TestCase/batch-insert',
        method: 'post',
        data
    })
}

// 导出单个测试用例为YAML
export function exportYaml(id) {
    return request({
        url: `/TestCase/export-yaml/${id}`,
        method: 'get',
        responseType: 'blob'
    })
}

// 批量导出测试用例为YAML
export function exportBatchYaml(data) {
    return request({
        url: '/TestCase/export-batch-yaml',
        method: 'post',
        data,
        responseType: 'blob'
    })
}

