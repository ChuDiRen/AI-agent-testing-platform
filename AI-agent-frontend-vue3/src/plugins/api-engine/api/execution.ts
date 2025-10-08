/**
 * API引擎插件 - 执行管理API
 */
import request from '@/utils/request'

export interface Execution {
    execution_id?: number
    case_id: number
    task_id?: string // Celery任务ID
    status: string // pending/running/success/failed/error
    result?: any // 执行结果(JSON格式)
    logs?: string // 执行日志
    error_message?: string // 错误信息
    duration?: number // 执行时长(秒)
    steps_total?: number // 总步骤数
    steps_passed?: number // 通过步骤数
    steps_failed?: number // 失败步骤数
    executed_by?: number // 执行人ID
    executed_at?: string // 执行时间
    finished_at?: string // 完成时间
}

export interface ExecutionListParams {
    page?: number
    page_size?: number
    case_id?: number
    status?: string
}

export const executionAPI = {
    /**
     * 执行测试用例
     */
    executeCase(caseId: number, context?: any) {
        return request.post(`/api/v1/plugin/api-engine/executions/${caseId}/execute`, {
            context: context || {}
        })
    },

    /**
     * 查询执行状态
     */
    getExecutionStatus(taskId: string) {
        return request.get(`/api/v1/plugin/api-engine/executions/task/${taskId}/status`)
    },

    /**
     * 获取执行历史列表
     */
    getExecutions(params?: ExecutionListParams) {
        return request.get('/api/v1/plugin/api-engine/executions', { params })
    },

    /**
     * 获取执行详情
     */
    getExecutionById(id: number) {
        return request.get(`/api/v1/plugin/api-engine/executions/${id}`)
    },

    /**
     * 删除执行记录
     */
    deleteExecution(id: number) {
        return request.delete(`/api/v1/plugin/api-engine/executions/${id}`)
    },

    /**
     * SSE日志流URL (需要在组件中使用EventSource)
     */
    getLogStreamUrl(taskId: string): string {
        const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
        return `${baseURL}/api/v1/plugin/api-engine/executions/task/${taskId}/log-stream`
    }
}

