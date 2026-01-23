import request from '../utils/request'

export const askQuestion = (data) => {
  // 后端期望的是表单数据格式，不是JSON对象
  const params = new URLSearchParams()
  params.append('message', data.message)
  if (data.conversation_id) {
    params.append('session_id', data.conversation_id)
  }
  if (data.top_k) {
    params.append('top_k', data.top_k)
  }
  if (data.score_threshold) {
    params.append('score_threshold', data.score_threshold)
  }
  
  return request.post('/chat', params, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
  })
}

export const chatWithHistory = (data) => {
  const params = new URLSearchParams()
  params.append('message', data.message)
  params.append('session_id', data.session_id)
  
  return request.post('/chat/with-history', params, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
  })
}

export const getChatHistory = (conversationId) => {
  return request.get(`/chat/history/${conversationId}`)
}

export const clearChatHistory = (conversationId) => {
  return request.delete(`/chat/history/${conversationId}`)
}

export const searchDocuments = (data) => {
  const params = new URLSearchParams()
  params.append('query', data.query)
  if (data.top_k) {
    params.append('top_k', data.top_k)
  }
  
  return request.post('/chat/search', params, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
  })
}
