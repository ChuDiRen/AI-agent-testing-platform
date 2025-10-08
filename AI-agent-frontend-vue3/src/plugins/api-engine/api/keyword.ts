/**
 * API引擎插件 - 关键字管理API
 */
import request from '@/utils/request'

export interface KeywordParameter {
    name: string
    type: string
    required: boolean
    description?: string
    default?: any
}

export interface Keyword {
    keyword_id?: number
    name: string
    description?: string
    code: string
    parameters?: KeywordParameter[]
    created_by?: number
    create_time?: string
    modify_time?: string
}

export interface KeywordListParams {
    page?: number
    page_size?: number
    name?: string
}

export const keywordAPI = {
    /**
     * 获取所有关键字(内置+自定义)
     */
    getKeywords(params?: KeywordListParams) {
        return request.get('/api/v1/plugin/api-engine/keywords', { params })
    },

    /**
     * 获取内置关键字列表
     */
    getBuiltinKeywords() {
        return request.get('/api/v1/plugin/api-engine/keywords/builtin')
    },

    /**
     * 获取关键字详情
     */
    getKeywordById(id: number) {
        return request.get(`/api/v1/plugin/api-engine/keywords/${id}`)
    },

    /**
     * 创建自定义关键字
     */
    createKeyword(data: Keyword) {
        return request.post('/api/v1/plugin/api-engine/keywords', data)
    },

    /**
     * 更新自定义关键字
     */
    updateKeyword(id: number, data: Keyword) {
        return request.put(`/api/v1/plugin/api-engine/keywords/${id}`, data)
    },

    /**
     * 删除自定义关键字
     */
    deleteKeyword(id: number) {
        return request.delete(`/api/v1/plugin/api-engine/keywords/${id}`)
    },

    /**
     * 测试关键字
     */
    testKeyword(id: number, params: any) {
        return request.post(`/api/v1/plugin/api-engine/keywords/${id}/test`, params)
    }
}

