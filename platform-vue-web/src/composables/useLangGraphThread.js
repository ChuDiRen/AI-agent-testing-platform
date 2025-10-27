import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import {
    createLangGraphClient,
    getThreads,
    createThread,
    deleteThread,
    updateThreadMetadata
} from '@/api/langgraph'

/**
 * LangGraph 线程管理 Composable
 */
export function useLangGraphThread() {
    const client = ref(null)
    const threads = ref([])
    const currentThreadId = ref(null)
    const loading = ref(false)

    // 初始化客户端
    const initClient = () => {
        if (!client.value) {
            try {
                client.value = createLangGraphClient()
                return true
            } catch (error) {
                console.error('Failed to initialize LangGraph client:', error)
                ElMessage.error('初始化客户端失败')
                return false
            }
        }
        return true
    }

    // 获取线程列表
    const fetchThreads = async () => {
        if (!initClient()) {
            return
        }

        loading.value = true
        try {
            const result = await getThreads(client.value)
            threads.value = result.map(thread => ({
                id: thread.thread_id,
                title: thread.metadata?.title || '新对话',
                createdAt: thread.created_at,
                updatedAt: thread.updated_at,
                metadata: thread.metadata || {}
            }))
        } catch (error) {
            console.error('Fetch threads error:', error)
            ElMessage.error('获取对话列表失败')
        } finally {
            loading.value = false
        }
    }

    // 创建新线程
    const createNewThread = async (title = '新对话') => {
        if (!initClient()) {
            return null
        }

        loading.value = true
        try {
            const thread = await createThread(client.value, {
                title,
                created_at: new Date().toISOString()
            })

            const newThread = {
                id: thread.thread_id,
                title,
                createdAt: new Date().toISOString(),
                updatedAt: new Date().toISOString(),
                metadata: { title }
            }

            threads.value.unshift(newThread)
            currentThreadId.value = newThread.id

            ElMessage.success('创建新对话成功')
            return newThread
        } catch (error) {
            console.error('Create thread error:', error)
            ElMessage.error('创建对话失败')
            return null
        } finally {
            loading.value = false
        }
    }

    // 切换线程
    const switchThread = (threadId) => {
        if (threadId === currentThreadId.value) {
            return
        }

        const thread = threads.value.find(t => t.id === threadId)
        if (thread) {
            currentThreadId.value = threadId
            ElMessage.success(`切换到: ${thread.title}`)
        } else {
            ElMessage.error('线程不存在')
        }
    }

    // 删除线程
    const removeThread = async (threadId) => {
        if (!initClient()) {
            return
        }

        try {
            await deleteThread(client.value, threadId)

            threads.value = threads.value.filter(t => t.id !== threadId)

            // 如果删除的是当前线程，切换到第一个线程或清空
            if (currentThreadId.value === threadId) {
                currentThreadId.value = threads.value.length > 0 ? threads.value[0].id : null
            }

            ElMessage.success('删除对话成功')
        } catch (error) {
            console.error('Delete thread error:', error)
            ElMessage.error('删除对话失败')
        }
    }

    // 更新线程标题
    const updateThreadTitle = async (threadId, newTitle) => {
        if (!initClient()) {
            return
        }

        try {
            await updateThreadMetadata(client.value, threadId, { title: newTitle })

            const thread = threads.value.find(t => t.id === threadId)
            if (thread) {
                thread.title = newTitle
                thread.metadata.title = newTitle
            }

            ElMessage.success('更新标题成功')
        } catch (error) {
            console.error('Update thread title error:', error)
            ElMessage.error('更新标题失败')
        }
    }

    // 计算属性
    const currentThread = computed(() => {
        return threads.value.find(t => t.id === currentThreadId.value)
    })

    const hasThreads = computed(() => threads.value.length > 0)

    return {
        // 状态
        threads,
        currentThreadId,
        currentThread,
        loading,
        hasThreads,

        // 方法
        initClient,
        fetchThreads,
        createNewThread,
        switchThread,
        removeThread,
        updateThreadTitle
    }
}

