/**
 * Test Execution Composable
 * 专门用于测试执行的WebSocket集成
 */
import { ref, computed, watch } from 'vue'
import { useWebSocket } from './useWebSocket'

export function useTestExecution(executionId) {
    // 使用基础WebSocket功能
    const {
        isConnected,
        messages,
        error,
        connect,
        disconnect,
        clearMessages,
        getMessagesByType
    } = useWebSocket(executionId)

    // 测试执行特定状态
    const progress = ref(0)
    const currentStep = ref('')
    const totalSteps = ref(0)
    const currentStepIndex = ref(0)
    const status = ref('idle') // idle | running | completed | failed
    const stepResults = ref([])
    const startTime = ref(null)
    const endTime = ref(null)

    // 计算属性
    const isRunning = computed(() => status.value === 'running')
    const isCompleted = computed(() => status.value === 'completed')
    const isFailed = computed(() => status.value === 'failed')
    const duration = computed(() => {
        if (!startTime.value) return 0
        const end = endTime.value || new Date()
        return Math.floor((end - startTime.value) / 1000) // 秒
    })

    // 格式化持续时间
    const formatDuration = computed(() => {
        const seconds = duration.value
        const hours = Math.floor(seconds / 3600)
        const minutes = Math.floor((seconds % 3600) / 60)
        const secs = seconds % 60

        if (hours > 0) {
            return `${hours}时${minutes}分${secs}秒`
        } else if (minutes > 0) {
            return `${minutes}分${secs}秒`
        } else {
            return `${secs}秒`
        }
    })

    // 监听消息变化，更新测试执行状态
    watch(messages, (newMessages) => {
        if (newMessages.length === 0) return

        const latestMessage = newMessages[newMessages.length - 1]
        handleMessage(latestMessage)
    }, { deep: true })

    // 处理不同类型的消息
    const handleMessage = (message) => {
        console.log('[TestExecution] 处理消息:', message)

        switch (message.type) {
            case 'start':
                handleStart(message)
                break
            case 'progress':
                handleProgress(message)
                break
            case 'step_start':
                handleStepStart(message)
                break
            case 'step_end':
                handleStepEnd(message)
                break
            case 'complete':
                handleComplete(message)
                break
            case 'error':
            case 'failed':
                handleError(message)
                break
            default:
                console.log('[TestExecution] 未知消息类型:', message.type)
        }
    }

    // 处理测试开始
    const handleStart = (message) => {
        status.value = 'running'
        startTime.value = new Date()
        totalSteps.value = message.total_steps || 0
        currentStepIndex.value = 0
        progress.value = 0
        stepResults.value = []
        console.log('[TestExecution] 测试开始')
    }

    // 处理进度更新
    const handleProgress = (message) => {
        progress.value = message.progress || 0
        currentStepIndex.value = message.current_step || 0
        totalSteps.value = message.total_steps || totalSteps.value
        currentStep.value = message.step_name || message.message || ''
    }

    // 处理步骤开始
    const handleStepStart = (message) => {
        currentStep.value = message.step_name || ''
        currentStepIndex.value = message.current_step || 0
        totalSteps.value = message.total_steps || totalSteps.value
        progress.value = message.progress || 0

        console.log(`[TestExecution] 步骤开始: ${currentStep.value} (${currentStepIndex.value}/${totalSteps.value})`)
    }

    // 处理步骤结束
    const handleStepEnd = (message) => {
        const stepResult = {
            stepIndex: message.current_step || currentStepIndex.value,
            stepName: message.step_name || currentStep.value,
            status: message.status || 'unknown',
            message: message.message || '',
            timestamp: message.timestamp || new Date().toISOString()
        }

        stepResults.value.push(stepResult)
        progress.value = message.progress || progress.value

        console.log(`[TestExecution] 步骤结束: ${stepResult.stepName} - ${stepResult.status}`)
    }

    // 处理测试完成
    const handleComplete = (message) => {
        status.value = message.status === 'failed' ? 'failed' : 'completed'
        progress.value = 100
        endTime.value = new Date()
        currentStep.value = message.message || '测试完成'

        console.log(`[TestExecution] 测试完成: ${status.value}`)
    }

    // 处理错误
    const handleError = (message) => {
        status.value = 'failed'
        endTime.value = new Date()
        currentStep.value = message.message || message.error || '测试失败'

        console.error('[TestExecution] 测试失败:', message)
    }

    // 开始测试执行监听
    const startExecution = () => {
        clearMessages()
        status.value = 'idle'
        progress.value = 0
        currentStep.value = ''
        stepResults.value = []
        startTime.value = null
        endTime.value = null

        connect()
        console.log('[TestExecution] 开始监听测试执行')
    }

    // 停止测试执行监听
    const stopExecution = () => {
        disconnect()
        console.log('[TestExecution] 停止监听测试执行')
    }

    // 重置状态
    const reset = () => {
        status.value = 'idle'
        progress.value = 0
        currentStep.value = ''
        currentStepIndex.value = 0
        totalSteps.value = 0
        stepResults.value = []
        startTime.value = null
        endTime.value = null
        clearMessages()
    }

    // 获取失败的步骤
    const getFailedSteps = () => {
        return stepResults.value.filter(step => step.status === 'failed')
    }

    // 获取成功的步骤
    const getPassedSteps = () => {
        return stepResults.value.filter(step => step.status === 'passed')
    }

    // 获取步骤统计
    const getStepStats = () => {
        return {
            total: stepResults.value.length,
            passed: getPassedSteps().length,
            failed: getFailedSteps().length,
            passRate: stepResults.value.length > 0
                ? Math.round((getPassedSteps().length / stepResults.value.length) * 100)
                : 0
        }
    }

    return {
        // WebSocket状态
        isConnected,
        error,

        // 测试执行状态
        progress,
        currentStep,
        currentStepIndex,
        totalSteps,
        status,
        stepResults,
        duration,
        formatDuration,

        // 计算属性
        isRunning,
        isCompleted,
        isFailed,

        // 方法
        startExecution,
        stopExecution,
        reset,
        getFailedSteps,
        getPassedSteps,
        getStepStats,

        // 原始消息（用于调试）
        messages
    }
}
