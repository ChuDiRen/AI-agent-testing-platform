// Copyright (c) 2025 左岚. All rights reserved.
/**
 * 知识库API
 */
import request from './request'

// ==================== 类型定义 ====================

export interface KnowledgeBase {
  kb_id: number
  name: string
  description?: string
  embedding_model: string
  vector_dimension: number
  chunk_size: number
  chunk_overlap: number
  user_id: number
  is_public: boolean
  status: string
  document_count: number
  chunk_count: number
  total_size: number
  created_at: string
  updated_at?: string
}

export interface Document {
  doc_id: number
  kb_id: number
  name: string
  file_path?: string
  file_type: string
  file_size: number
  status: string
  error_message?: string
  chunk_count: number
  char_count: number
  created_at: string
  updated_at?: string
  processed_at?: string
}

export interface SearchResult {
  chunk_id: number
  doc_id: number
  doc_name: string
  content: string
  score: number
  chunk_index: number
  metadata?: Record<string, any>
}

export interface SearchResponse {
  query: string
  results: SearchResult[]
  total: number
  search_time: number
}

// ==================== 知识库管理 ====================

/**
 * 创建知识库
 */
export function createKnowledgeBaseAPI(data: {
  name: string
  description?: string
  embedding_model?: string
  chunk_size?: number
  chunk_overlap?: number
  is_public?: boolean
}) {
  return request<KnowledgeBase>({
    url: '/api/v1/knowledge/bases',
    method: 'post',
    data
  })
}

/**
 * 获取知识库列表
 */
export function getKnowledgeBasesAPI(params?: {
  skip?: number
  limit?: number
}) {
  return request<KnowledgeBase[]>({
    url: '/api/v1/knowledge/bases',
    method: 'get',
    params
  })
}

/**
 * 获取知识库详情
 */
export function getKnowledgeBaseAPI(kbId: number) {
  return request<KnowledgeBase>({
    url: `/api/v1/knowledge/bases/${kbId}`,
    method: 'get'
  })
}

/**
 * 更新知识库
 */
export function updateKnowledgeBaseAPI(kbId: number, data: Partial<KnowledgeBase>) {
  return request<KnowledgeBase>({
    url: `/api/v1/knowledge/bases/${kbId}`,
    method: 'put',
    data
  })
}

/**
 * 删除知识库
 */
export function deleteKnowledgeBaseAPI(kbId: number) {
  return request({
    url: `/api/v1/knowledge/bases/${kbId}`,
    method: 'delete'
  })
}

// ==================== 文档管理 ====================

/**
 * 上传文档
 */
export function uploadDocumentAPI(kbId: number, file: File, useAsync: boolean = true) {
  const formData = new FormData()
  formData.append('kb_id', kbId.toString())
  formData.append('file', file)
  formData.append('use_async', useAsync.toString())

  return request<{
    task_id: string
    doc_id: number
    message: string
  }>({
    url: '/api/v1/knowledge/documents/upload',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

/**
 * 添加文本文档
 */
export function addTextDocumentAPI(data: {
  kb_id: number
  name: string
  content: string
}) {
  return request<Document>({
    url: '/api/v1/knowledge/documents/text',
    method: 'post',
    params: data
  })
}

/**
 * 删除文档
 */
export function deleteDocumentAPI(docId: number) {
  return request({
    url: `/api/v1/knowledge/documents/${docId}`,
    method: 'delete'
  })
}

/**
 * 批量删除文档
 */
export function batchDeleteDocumentsAPI(docIds: number[]) {
  return request({
    url: '/api/v1/knowledge/documents/batch-delete',
    method: 'post',
    data: { doc_ids: docIds }
  })
}

/**
 * 获取文档分块
 */
export function getDocumentChunksAPI(docId: number) {
  return request({
    url: `/api/v1/knowledge/documents/${docId}/chunks`,
    method: 'get'
  })
}

// ==================== 搜索功能 ====================

/**
 * 搜索知识库
 */
export function searchKnowledgeBaseAPI(data: {
  query: string
  kb_id: number
  top_k?: number
  score_threshold?: number
  with_content?: boolean
}) {
  return request<SearchResponse>({
    url: '/api/v1/knowledge/search',
    method: 'post',
    data
  })
}

// ==================== 任务管理 ====================

export interface TaskStatus {
  task_id: string
  state: string
  current?: number
  total?: number
  status?: string
  result?: any
  error?: string
}

/**
 * 获取任务状态
 */
export function getTaskStatusAPI(taskId: string) {
  return request<TaskStatus>({
    url: `/api/v1/knowledge/tasks/${taskId}`,
    method: 'get'
  })
}

/**
 * 批量处理文档
 */
export function batchProcessDocumentsAPI(docIds: number[]) {
  return request({
    url: '/api/v1/knowledge/tasks/batch-process',
    method: 'post',
    data: docIds
  })
}

