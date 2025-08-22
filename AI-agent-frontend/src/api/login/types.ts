// 重新导出通用类型，保持向后兼容
export type { 
  LoginRequest as ILoginParams,
  LoginResponse,
  UserInfo,
  ApiResponse
} from '@/api/types'

export interface ILoginApi {
  login: (params: import('@/api/types').LoginRequest) => Promise<import('@/api/types').ApiResponse<import('@/api/types').LoginResponse>>
}
