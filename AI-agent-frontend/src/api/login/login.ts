import http from '@/api/http'
import type { LoginRequest, LoginResponse, ApiResponse } from '@/api/types'

// 保持向后兼容
export interface ILoginApi {
  login(params: LoginRequest): Promise<ApiResponse<LoginResponse>>
}

const loginApi: ILoginApi = {
  login(params) {
    return http.post<LoginResponse>('/users/login', params)
  },
}

export { loginApi }
