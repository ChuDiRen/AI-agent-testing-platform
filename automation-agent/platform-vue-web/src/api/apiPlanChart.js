import axios from "@/axios"

// 模块名 - 和后台对应
const module_name = "ApiTestPlanChart"

export function queryPlanCount(id) {
    return axios.get(`/api/v1/${module_name}/queryPlanCount?coll_id=${id}`)
}

export function queryCaseCount(id) {
    return axios.get(`/api/v1/${module_name}/queryCaseCount?coll_id=${id}`)
}

export function queryPassRate(id) {
    return axios.get(`/api/v1/${module_name}/queryPassRate?coll_id=${id}`)
}

export function queryPlanTrend(id) {
    return axios.get(`/api/v1/${module_name}/queryPlanTrend?coll_id=${id}`)
}

export function queryPlanTime(id) {
    return axios.get(`/api/v1/${module_name}/queryPlanTime?coll_id=${id}`)
}

export function queryFailTop5(id) {
    return axios.get(`/api/v1/${module_name}/queryFailTop5?coll_id=${id}`)
}
