import { Client } from '@langchain/langgraph-sdk'
import { v4 as uuidv4 } from 'uuid'

/**
 * LangGraph 客户端配置
 * @returns {Client} LangGraph 客户端实例
 */
export const createLangGraphClient = () => {
    const apiUrl = import.meta.env.VITE_LANGGRAPH_API_URL || 'http://localhost:2024'
    const apiKey = import.meta.env.VITE_LANGSMITH_API_KEY || null

    return new Client({
        apiUrl,
        ...(apiKey && { apiKey })
    })
}

/**
 * 流式消息处理
 * @param {Client} client - LangGraph 客户端
 * @param {string} threadId - 线程 ID
 * @param {object} message - 消息对象
 * @param {function} onChunk - 流式数据回调
 * @param {function} onEvent - 事件回调
 */
export const streamMessages = async (client, threadId, message, onChunk, onEvent) => {
    const assistantId = import.meta.env.VITE_LANGGRAPH_ASSISTANT_ID || 'agent'

    try {
        const stream = client.runs.stream(
            threadId,
            assistantId,
            {
                input: { messages: [message] },
                streamMode: ['messages', 'events']
            }
        )

        for await (const chunk of stream) {
            // 处理消息流
            if (chunk.event === 'messages/partial') {
                onChunk && onChunk(chunk.data)
            }

            // 处理事件流（工具调用、中断等）
            if (chunk.event && onEvent) {
                onEvent(chunk)
            }
        }
    } catch (error) {
        console.error('Stream error:', error)
        throw error
    }
}

/**
 * 获取线程列表
 * @param {Client} client - LangGraph 客户端
 * @returns {Promise<Array>} 线程列表
 */
export const getThreads = async (client) => {
    try {
        const threads = await client.threads.list()
        return threads
    } catch (error) {
        console.error('Get threads error:', error)
        return []
    }
}

/**
 * 创建新线程
 * @param {Client} client - LangGraph 客户端
 * @param {object} metadata - 线程元数据
 * @returns {Promise<object>} 新创建的线程
 */
export const createThread = async (client, metadata = {}) => {
    try {
        const thread = await client.threads.create({
            metadata: {
                title: '新对话',
                created_at: new Date().toISOString(),
                ...metadata
            }
        })
        return thread
    } catch (error) {
        console.error('Create thread error:', error)
        throw error
    }
}

/**
 * 获取线程详情
 * @param {Client} client - LangGraph 客户端
 * @param {string} threadId - 线程 ID
 * @returns {Promise<object>} 线程详情
 */
export const getThread = async (client, threadId) => {
    try {
        const thread = await client.threads.get(threadId)
        return thread
    } catch (error) {
        console.error('Get thread error:', error)
        throw error
    }
}

/**
 * 获取线程状态
 * @param {Client} client - LangGraph 客户端
 * @param {string} threadId - 线程 ID
 * @returns {Promise<object>} 线程状态
 */
export const getThreadState = async (client, threadId) => {
    try {
        const state = await client.threads.getState(threadId)
        return state
    } catch (error) {
        console.error('Get thread state error:', error)
        throw error
    }
}

/**
 * 删除线程
 * @param {Client} client - LangGraph 客户端
 * @param {string} threadId - 线程 ID
 */
export const deleteThread = async (client, threadId) => {
    try {
        await client.threads.delete(threadId)
    } catch (error) {
        console.error('Delete thread error:', error)
        throw error
    }
}

/**
 * 更新线程元数据
 * @param {Client} client - LangGraph 客户端
 * @param {string} threadId - 线程 ID
 * @param {object} metadata - 新的元数据
 */
export const updateThreadMetadata = async (client, threadId, metadata) => {
    try {
        await client.threads.update(threadId, { metadata })
    } catch (error) {
        console.error('Update thread metadata error:', error)
        throw error
    }
}

