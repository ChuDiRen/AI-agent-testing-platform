import request from '../utils/request'

export const getDocuments = (params) => {
  return request.get('/documents', { params })
}

export const getDocument = (docId) => {
  return request.get(`/documents/${docId}`)
}

export const uploadDocument = (formData) => {
  return request.post('/documents/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

export const updateDocument = (docId, data) => {
  return request.put(`/documents/${docId}`, data)
}

export const deleteDocument = (docId) => {
  return request.delete(`/documents/${docId}`)
}

export const indexDocument = (docId) => {
  return request.post(`/documents/${docId}/index`)
}

export const reindexDocument = (docId) => {
  return request.post(`/documents/${docId}/reindex`)
}

export const batchIndexDocuments = (docIds) => {
  return request.post('/documents/batch-index', { doc_ids: docIds })
}

export const deleteDocumentIndex = (docId) => {
  return request.delete(`/documents/${docId}/index`)
}
