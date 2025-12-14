/**
 * useLangGraph - LangGraph SSE连接和状态管理
 */
import { ref, reactive } from 'vue'

export function useLangGraph() {
    const isGenerating = ref(false)
    const currentStage = ref('init')
    const progress = ref(0)
    const message = ref('')
    const completedStages = ref([])
    const testCases = ref([])
    const error = ref(null)
    const qualityScore = ref(0)

    let eventSource = null

    const startGeneration = async (requirement, testType, modelConfig) => {
        // 重置状态
        isGenerating.value = true
        currentStage.value = 'init'
        progress.value = 0
        message.value = '准备生成...'
        completedStages.value = []
        testCases.value = []
        error.value = null
        qualityScore.value = 0

        // 构建请求体
        const body = JSON.stringify({
            requirement,
            test_type: testType,
            max_iterations: 2,
            model_config: modelConfig
        })

        try {
            // 使用fetch发送POST请求并处理SSE
            const response = await fetch('/api/LangGraph/generate/stream', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body
            })

            const reader = response.body.getReader()
            const decoder = new TextDecoder()

            while (true) {
                const { done, value } = await reader.read()
                if (done) break

                const text = decoder.decode(value)
                const lines = text.split('\n')

                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        try {
                            const event = JSON.parse(line.slice(6))
                            handleEvent(event)
                        } catch (e) {
                            console.error('Parse error:', e)
                        }
                    }
                }
            }
        } catch (e) {
            error.value = e.message
            console.error('Generation error:', e)
        } finally {
            isGenerating.value = false
        }
    }

    const handleEvent = (event) => {
        switch (event.type) {
            case 'stage_start':
                currentStage.value = event.data.stage
                message.value = event.data.message
                break
            case 'stage_progress':
                currentStage.value = event.data.stage
                message.value = event.data.message
                progress.value = event.data.progress
                if (event.data.progress === 100) {
                    if (!completedStages.value.includes(event.data.stage)) {
                        completedStages.value.push(event.data.stage)
                    }
                }
                break
            case 'testcase':
                try {
                     let cases = event.data
                     if (typeof cases === 'string') {
                         const jsonMatch = cases.match(/```json\s*([\s\S]*?)\s*```/)
                         if (jsonMatch) {
                             cases = JSON.parse(jsonMatch[1])
                         } else {
                             try {
                                 cases = JSON.parse(cases)
                             } catch (e) {
                                 console.warn('Raw parse failed', e)
                             }
                         }
                     }
                     if (cases && cases.test_cases) {
                         testCases.value = cases.test_cases
                     } else if (Array.isArray(cases)) {
                         testCases.value = cases
                     }
                } catch (e) {
                    console.error('Failed to parse test cases:', e)
                }
                break
            case 'done':
                qualityScore.value = event.data.quality_score
                isGenerating.value = false
                break
            case 'error':
                error.value = event.data.error
                isGenerating.value = false
                break
        }
    }

    return {
        isGenerating,
        currentStage,
        progress,
        message,
        completedStages,
        testCases,
        error,
        qualityScore,
        startGeneration
    }
}
