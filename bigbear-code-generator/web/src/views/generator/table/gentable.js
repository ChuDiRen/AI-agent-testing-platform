import axios from "~/axios"

// 模块名 - 和后台对应
const module_name = "GenTable"

// 获取数据库表列表
export function getDbTables() {
    return axios.get(`/${module_name}/dbTables`)
}

// 批量导入表配置
export function importTables(tableNames) {
    return axios.post(`/${module_name}/importTables`, { table_names: tableNames })
}

// 上传 SQL 文件导入表配置
export function uploadSqlFile(file) {
    const formData = new FormData()
    formData.append('file', file)
    return axios.post(`/${module_name}/uploadSql`, formData, {
        headers: {
            'Content-Type': 'multipart/form-data'
        }
    })
}

// 分页查询表配置
export function queryByPage(data) {
    return axios.post(`/${module_name}/queryByPage?_alias=gentable-page`, data)
}

// 根据ID查询表配置
export function queryById(id) {
    return axios.get(`/${module_name}/queryById?id=${id}&_alias=gentable-detail`)
}

// 更新表配置
export function updateData(data) {
    return axios.put(`/${module_name}/update?_alias=gentable-update`, data)
}

// 删除表配置
export function deleteData(id) {
    return axios.delete(`/${module_name}/delete?id=${id}&_alias=gentable-delete`)
}
