import axios from '~/axios'

const module_name = "ApiStatistics"

// 获取系统总览统计
export function getOverview() {
    return axios.get(`/${module_name}/overview?_alias=statistics-overview`)
}
