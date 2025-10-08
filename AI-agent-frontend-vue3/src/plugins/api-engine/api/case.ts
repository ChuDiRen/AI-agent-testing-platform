/**
 * API引擎插件 - 测试用例API
 */
import request from '@/utils/request'

export interface Case {
    case_id?: number
    suite_id: number
    name: string
    description?: string
    config_mode: 'form' | 'yaml'
    form_config?: any
    yaml_config?: string
    status?: string
    priority?: string
    created_by?: number
    create_time?: string
    modify_time?: string
}

export interface CaseListParams {
    page?: number
    page_size?: number
    suite_id?: number
    name?: string
    status?: string
    priority?: string
}

export const caseAPI = {
    /**
     * 获取用例列表
     */
    getCases(params?: CaseListParams) {
        return request.get('/api/v1/api-engine/cases', { params })
    },

    /**
     * 获取用例详情
     */
    getCaseById(id: number) {
        return request.get(`/api/v1/api-engine/cases/${id}`)
    },

    /**
     * 创建用例
     */
    createCase(data: Case) {
        return request.post('/api/v1/api-engine/cases', data)
    },

    /**
     * 更新用例
     */
    updateCase(id: number, data: Case) {
        return request.put(`/api/v1/api-engine/cases/${id}`, data)
    },

    /**
     * 删除用例
     */
    deleteCase(id: number) {
        return request.delete(`/api/v1/api-engine/cases/${id}`)
    },

    /**
     * 克隆用例
     */
    cloneCase(id: number) {
        return request.post(`/api/v1/api-engine/cases/${id}/clone`)
    },

    /**
     * 导入YAML用例
     */
    importYaml(data: { suite_id: number; yaml_content: string; name?: string }) {
        return request.post('/api/v1/api-engine/cases/import', data)
    }
}

