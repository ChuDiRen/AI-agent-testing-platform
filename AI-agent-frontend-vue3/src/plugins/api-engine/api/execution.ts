/**
 * API引擎插件 - 执行管理API
 */
import request from '@/utils/request'

export interface Execution {
    execution_id?: number
    case_id: number
    suite_id?: number
    executor_id?: number
    start_time?: string
    end_time?: string
    duration?: number
    status: string
    log_output?: string
    result_summary?: any
    report_url?: string
    celery_task_id?: string
}

export interface ExecutionListParams {
    page?: number
    page_size?: number
    case_id?: number
    suite_id?: number
    status?: string
}

export const executionAPI = {
    /**
     * 执行测试用例
     */
    executeCase(caseId: number, context?: any) {
        return request.post(`/api/v1/api-engine/executions/${caseId}/execute`, {
            context: context || {}
        })
    },

    /**
     * 查询执行状态
     */
    getExecutionStatus(taskId: string) {
        return request.get(`/api/v1/api-engine/executions/${taskId}/status`)
    },

    /**
     * 获取执行历史列表
     */
    getExecutions(params?: ExecutionListParams) {
        return request.get('/api/v1/api-engine/executions', { params })
    },

    /**
     * 获取执行详情
     */
    getExecutionById(id: number) {
        return request.get(`/api/v1/api-engine/executions/${id}`)
    },

    /**
     * SSE日志流URL (需要在组件中使用EventSource)
     */
    getLogStreamUrl(taskId: string): string {
        const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
        return `${baseURL}/api/v1/api-engine/executions/${taskId}/log-stream`
    }
}

