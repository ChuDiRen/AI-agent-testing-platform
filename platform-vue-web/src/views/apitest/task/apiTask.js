import axios from "~/axios"

// 获取可用执行器列表（插件）
export function listExecutors() {
    return axios.get("/Task/executors?_alias=task-executors")
}

// 预留：直接通过任务调度接口执行测试任务（当前用例执行已通过 /ApiInfoCase/executeCase 封装）
export function executeTask(data) {
    return axios.post("/Task/execute?_alias=task-execute", data)
}
