import axios from '@/axios'

const module_name = "AiConversation"

// 创建对话
export function createConversation(data) {
    return axios.post(`/${module_name}/create`, data)
}

// 获取对话列表
export function getConversations(params) {
    return axios.get(`/${module_name}/list`, { params })
}

// 获取对话消息
export function getMessages(conversationId) {
    return axios.get(`/${module_name}/${conversationId}/messages`)
}

// 更新对话标题
export function updateTitle(conversationId, title) {
    return axios.put(`/${module_name}/${conversationId}/title`, null, { params: { title } })
}

// 删除对话
export function deleteConversation(conversationId) {
    return axios.delete(`/${module_name}/${conversationId}`)
}

// 流式对话（通过EventSource实现）
export function chatStream(data) {
    const params = new URLSearchParams(data)
    return new EventSource(`/api/${module_name}/chat?${params.toString()}`)
}

// 批量保存测试用例
export function batchInsertTestCases(data) {
    return axios.post('/TestCase/batch-insert', data)
}

export default {
    createConversation,
    getConversations,
    getMessages,
    updateTitle,
    deleteConversation,
    chatStream,
    batchInsertTestCases
}
