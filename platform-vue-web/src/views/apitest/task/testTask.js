import axios from "~/axios"

// 分页查询测试任务
export function queryByPage(data) {
    return axios.post("/TestTask/queryByPage?_alias=test-task-list", data)
}

// 根据ID查询测试任务
export function queryById(id) {
    return axios.get(`/TestTask/queryById?id=${id}&_alias=test-task-detail`)
}

// 新增测试任务
export function insertData(data) {
    return axios.post("/TestTask/insert?_alias=test-task-add", data)
}

// 更新测试任务
export function updateData(data) {
    return axios.put("/TestTask/update?_alias=test-task-update", data)
}

// 删除测试任务
export function deleteData(id) {
    return axios.delete(`/TestTask/delete?id=${id}&_alias=test-task-delete`)
}

// 执行测试任务
export function executeTask(data) {
    return axios.post("/TestTask/execute?_alias=test-task-execute", data)
}

// 更新任务状态
export function updateStatus(id, status) {
    return axios.put(`/TestTask/updateStatus?id=${id}&status=${status}&_alias=test-task-status`)
}

// 查询任务执行记录
export function queryExecutions(data) {
    return axios.post("/TestTask/queryExecutions?_alias=test-task-executions", data)
}

// 获取执行记录详情
export function getExecutionDetail(id) {
    return axios.get(`/TestTask/getExecutionDetail?id=${id}&_alias=test-task-execution-detail`)
}
