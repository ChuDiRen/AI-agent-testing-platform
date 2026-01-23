import request from '../utils/request'

export const getUserInfo = () => {
  return request.get('/users/me')
}

export const updateUser = (userId, data) => {
  return request.put(`/users/${userId}`, data)
}

export const getUsers = (params) => {
  return request.get('/users', { params })
}

export const createUser = (data) => {
  return request.post('/users', data)
}

export const deleteUser = (userId) => {
  return request.delete(`/users/${userId}`)
}

export const changePassword = (userId, data) => {
  return request.post(`/users/${userId}/password/change`, data)
}

export const resetPassword = (userId, data) => {
  return request.post(`/users/${userId}/password/reset`, data)
}

export const getLogs = (params) => {
  return request.get('/logs', { params })
}
