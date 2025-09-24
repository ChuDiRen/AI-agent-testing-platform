// 知识库管理API
import { AxiosResponse } from 'axios'
import http from '@/api/http'

// 知识库相关接口定义
export interface KnowledgeBase {
  id: string
  name: string
  description?: string
  user_id: number
  status: string
  embedding_model: string
  chunk_size: number
  chunk_overlap: number
  document_count: number
  total_chunks: number
  created_at: string
  updated_at: string
}

export interface KnowledgeBaseCreate {
  name: string
  description?: string
  embedding_model?: string
  chunk_size?: number
  chunk_overlap?: number
}

export interface KnowledgeBaseUpdate {
  name?: string
  description?: string
  status?: string
  embedding_model?: string
  chunk_size?: number
  chunk_overlap?: number
}

export interface Document {
  id: string
  knowledge_base_id: string
  title: string
  description?: string
  file_name?: string
  file_type?: string
  file_size?: number
  user_id: number
  status: string
  chunk_count: number
  created_at: string
  updated_at: string
}

export interface DocumentSearchRequest {
  query: string
  limit?: number
  similarity_threshold?: number
}

export interface DocumentChunk {
  id: string
  document_id: string
  chunk_index: number
  content: string
  metadata?: Record<string, any>
  token_count?: number
  similarity_score?: number
}

export interface DocumentSearchResponse {
  query: string
  total_results: number
  chunks: DocumentChunk[]
  response_time: number
}

export interface ChatWithKnowledgeRequest {
  kb_id: string
  query: string
  large_model_id?: string
  similarity_threshold?: number
  max_chunks?: number
  temperature?: number
}

export interface ChatWithKnowledgeResponse {
  query: string
  response: string
  large_model_id: string
  relevant_chunks: DocumentChunk[]
  tokens_used?: number
  cost?: number
  response_time: number
}

// 知识库API
export const knowledgeApi = {
  // 创建知识库
  createKnowledgeBase(data: KnowledgeBaseCreate): Promise<AxiosResponse<any>> {
    return http.post('/knowledge-bases', data)
  },

  // 获取知识库列表
  getKnowledgeBases(params: {
    page?: number
    page_size?: number
    name?: string
  } = {}): Promise<AxiosResponse<any>> {
    return http.get('/knowledge-bases', { params })
  },

  // 获取知识库详情
  getKnowledgeBase(id: string): Promise<AxiosResponse<any>> {
    return http.get(`/knowledge-bases/${id}`)
  },

  // 更新知识库
  updateKnowledgeBase(id: string, data: KnowledgeBaseUpdate): Promise<AxiosResponse<any>> {
    return http.put(`/knowledge-bases/${id}`, data)
  },

  // 删除知识库
  deleteKnowledgeBase(id: string): Promise<AxiosResponse<any>> {
    return http.delete(`/knowledge-bases/${id}`)
  },

  // 上传文档
  uploadDocument(kbId: string, file: File, data: {
    title?: string
    description?: string
  } = {}): Promise<AxiosResponse<any>> {
    const formData = new FormData()
    formData.append('file', file)
    if (data.title) formData.append('title', data.title)
    if (data.description) formData.append('description', data.description)

    return http.post(`/knowledge-bases/${kbId}/documents`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },

  // 获取文档列表
  getDocuments(kbId: string, params: {
    page?: number
    page_size?: number
    title?: string
  } = {}): Promise<AxiosResponse<any>> {
    return http.get(`/knowledge-bases/${kbId}/documents`, { params })
  },

  // 删除文档
  deleteDocument(docId: string): Promise<AxiosResponse<any>> {
    return http.delete(`/documents/${docId}`)
  },

  // 搜索文档
  searchDocuments(kbId: string, data: DocumentSearchRequest): Promise<AxiosResponse<any>> {
    return http.post(`/knowledge-bases/${kbId}/search`, data)
  },

  // 基于知识库对话
  chatWithKnowledge(data: ChatWithKnowledgeRequest): Promise<AxiosResponse<any>> {
    return http.post('/chat-with-knowledge', data)
  }
}

// 知识库工具函数
export const knowledgeUtils = {
  // 格式化文件大小
  formatFileSize(bytes: number): string {
    if (bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  },

  // 获取文件类型图标
  getFileTypeIcon(fileType: string): string {
    const type = fileType?.toLowerCase() || ''
    if (type.includes('pdf')) return 'document'
    if (type.includes('word') || type.includes('doc')) return 'document'
    if (type.includes('text') || type.includes('plain')) return 'document'
    if (type.includes('markdown')) return 'document'
    return 'document'
  },

  // 获取状态标签类型
  getStatusTagType(status: string): string {
    switch (status) {
      case 'active':
        return 'success'
      case 'inactive':
        return 'danger'
      case 'processing':
        return 'warning'
      case 'completed':
        return 'success'
      case 'failed':
        return 'danger'
      default:
        return 'info'
    }
  },

  // 获取状态文本
  getStatusText(status: string): string {
    switch (status) {
      case 'active':
        return '激活'
      case 'inactive':
        return '禁用'
      case 'processing':
        return '处理中'
      case 'completed':
        return '已完成'
      case 'failed':
        return '失败'
      default:
        return '未知'
    }
  },

  // 高亮搜索结果
  highlightSearchResult(content: string, query: string): string {
    if (!query) return content
    const regex = new RegExp(`(${query})`, 'gi')
    return content.replace(regex, '<mark>$1</mark>')
  },

  // 截断文本
  truncateText(text: string, maxLength: number = 100): string {
    if (!text) return ''
    if (text.length <= maxLength) return text
    return text.substring(0, maxLength) + '...'
  },

  // 计算相似度百分比
  formatSimilarity(score: number): string {
    return `${Math.round(score * 100)}%`
  },

  // 验证知识库名称
  validateKnowledgeBaseName(name: string): { valid: boolean; message?: string } {
    if (!name || name.trim().length === 0) {
      return { valid: false, message: '知识库名称不能为空' }
    }
    if (name.length > 100) {
      return { valid: false, message: '知识库名称不能超过100个字符' }
    }
    if (!/^[\u4e00-\u9fa5a-zA-Z0-9_-]+$/.test(name)) {
      return { valid: false, message: '知识库名称只能包含中文、英文、数字、下划线和连字符' }
    }
    return { valid: true }
  },

  // 验证文件类型
  validateFileType(file: File): { valid: boolean; message?: string } {
    const allowedTypes = [
      'text/plain',
      'text/markdown',
      'application/pdf',
      'application/msword',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    ]
    
    const allowedExtensions = ['.txt', '.md', '.pdf', '.doc', '.docx']
    const fileExtension = file.name.toLowerCase().substring(file.name.lastIndexOf('.'))
    
    if (!allowedTypes.includes(file.type) && !allowedExtensions.includes(fileExtension)) {
      return { 
        valid: false, 
        message: '仅支持 .txt, .md, .pdf, .doc, .docx 格式的文件' 
      }
    }
    
    // 文件大小限制 10MB
    if (file.size > 10 * 1024 * 1024) {
      return { 
        valid: false, 
        message: '文件大小不能超过 10MB' 
      }
    }
    
    return { valid: true }
  }
}
