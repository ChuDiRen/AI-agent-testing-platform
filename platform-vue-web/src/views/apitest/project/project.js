import request from '@/axios' # HTTP请求工具

const module_name = 'ApiProject' # 模块名称

// 分页查询项目
export function queryByPage(data) {
    return request({
        url: `/${module_name}/queryByPage`,
        method: 'post',
        data
    })
}

// 查询所有项目
export function queryAll() {
    return request({
        url: `/${module_name}/queryAll`,
        method: 'get'
    })
}

// 根据ID查询项目
export function queryById(id) {
    return request({
        url: `/${module_name}/queryById`,
        method: 'get',
        params: { id }
    })
}

// 新增项目
export function insertData(data) {
    return request({
        url: `/${module_name}/insert`,
        method: 'post',
        data
    })
}

// 更新项目
export function updateData(data) {
    return request({
        url: `/${module_name}/update`,
        method: 'put',
        data
    })
}

// 删除项目
export function deleteData(id) {
    return request({
        url: `/${module_name}/delete`,
        method: 'delete',
        params: { id }
    })
}

