import request from '../utils/request'

export const login = (data) => {
  // OAuth2PasswordRequestForm需要表单数据格式
  const params = new URLSearchParams()
  params.append('username', data.username)
  params.append('password', data.password)
  params.append('grant_type', 'password')
  
  return request.post('/auth/login', params, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
  })
}

export const logout = () => {
  return request.post('/auth/logout')
}

export const verifyToken = () => {
  return request.get('/auth/verify-token')
}
