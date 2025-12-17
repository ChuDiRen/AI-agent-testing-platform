import axios from '~/axios'

const module_name = "ApiStatistics"

// 获取系统总览统计
export function getOverview() {
    return axios.get(`/${module_name}/overview?_alias=statistics-overview`)
}

// 查询测试计划执行次数
export function getExecutionCount(planId = null) {
    let url = `/${module_name}/executionCount?_alias=statistics-execution-count`
    if (planId) url += `&plan_id=${planId}`
    return axios.get(url)
}

// 查询用例数量统计
export function getCaseCount(params = {}) {
    let url = `/${module_name}/caseCount?_alias=statistics-case-count`
    if (params.plan_id) url += `&plan_id=${params.plan_id}`
    if (params.project_id) url += `&project_id=${params.project_id}`
    return axios.get(url)
}

// 查询测试通过率
export function getPassRate(params = {}) {
    let url = `/${module_name}/passRate?_alias=statistics-pass-rate`
    if (params.plan_id) url += `&plan_id=${params.plan_id}`
    if (params.days) url += `&days=${params.days}`
    return axios.get(url)
}

// 查询执行趋势图数据
export function getExecutionTrend(params = {}) {
    let url = `/${module_name}/executionTrend?_alias=statistics-execution-trend`
    if (params.plan_id) url += `&plan_id=${params.plan_id}`
    if (params.limit) url += `&limit=${params.limit}`
    return axios.get(url)
}

// 查询耗时趋势图数据
export function getTimeTrend(params = {}) {
    let url = `/${module_name}/timeTrend?_alias=statistics-time-trend`
    if (params.plan_id) url += `&plan_id=${params.plan_id}`
    if (params.limit) url += `&limit=${params.limit}`
    return axios.get(url)
}

// 查询失败TOP5用例
export function getFailedTop5(params = {}) {
    let url = `/${module_name}/failedTop5?_alias=statistics-failed-top5`
    if (params.plan_id) url += `&plan_id=${params.plan_id}`
    if (params.days) url += `&days=${params.days}`
    return axios.get(url)
}

// 查询每日统计数据
export function getDailyStats(days = 7) {
    return axios.get(`/${module_name}/dailyStats?days=${days}&_alias=statistics-daily`)
}
