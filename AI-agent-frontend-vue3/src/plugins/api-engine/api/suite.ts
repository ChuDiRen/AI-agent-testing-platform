/**
 * API引擎插件 - 测试套件API
 */
import request from '@/utils/request'

export interface Suite {
    suite_id?: number
    name: string
    description?: string
    created_by?: number
    create_time?: string
    modify_time?: string
}

export interface SuiteListParams {
    page?: number
    page_size?: number
    name?: string
}

export const suiteAPI = {
    /**
     * 获取套件列表
     */
    getSuites(params?: SuiteListParams) {
        return request.get('/api/v1/api-engine/suites', { params })
    },

    /**
     * 获取套件详情
     */
    getSuiteById(id: number) {
        return request.get(`/api/v1/api-engine/suites/${id}`)
    },

    /**
     * 创建套件
     */
    createSuite(data: Suite) {
        return request.post('/api/v1/api-engine/suites', data)
    },

    /**
     * 更新套件
     */
    updateSuite(id: number, data: Suite) {
        return request.put(`/api/v1/api-engine/suites/${id}`, data)
    },

    /**
     * 删除套件
     */
    deleteSuite(id: number) {
        return request.delete(`/api/v1/api-engine/suites/${id}`)
    }
}

