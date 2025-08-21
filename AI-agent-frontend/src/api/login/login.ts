import http from '@/api/http'
import * as T from './types'

const loginApi: T.ILoginApi = {
  login(params) {
    return http.post('/login', params)
  }
}
export {
  loginApi,
}
