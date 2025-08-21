//http.ts
import axios, { InternalAxiosRequestConfig, AxiosResponse } from 'axios'
import { NProgressStart, NProgressDone } from '@/utils/nprogress'
import { BASE_URL } from './baseUrl'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getToken, removeToken } from '@/utils/auth'

const router = useRouter()

// 设置请求头和请求路径
axios.defaults.baseURL = BASE_URL
axios.defaults.timeout = 10000
axios.defaults.headers.post['Content-Type'] = 'application/json;charset=UTF-8'
axios.interceptors.request.use(
  (config): InternalAxiosRequestConfig<any> => {
    const token = getToken()
    if (token) {
      config.headers.Authorization = token
    }
    return config
  },
  (err) => {
    return err
  }
)
// 响应拦截
axios.interceptors.response.use(
  (res): AxiosResponse<any, any> => {
    if (res.data.code == 401) {
      removeToken()
      router.push({
        path: '/login'
      }).catch(e => console.log(e))
    } else if (res.data.code != 200) {
      ElMessage({
        type: 'error',
        message: res.data.msg || '操作失败',
      })
      console.error(res.data)
    }
    return res
  },
  (err) => {
    const { status, data } = err.response
    ElMessage({
      type: 'error',
      message: data?.msg || '操作失败',
    })
    if (status === 401) {
      removeToken()
      router.push({
        path: '/login'
      }).catch(e => console.log(e))
    }
    return err.response // 返回接口返回的错误信息
  }
)

interface ResType<T> {
  code: number
  data?: T
  msg: string
  err?: string
}
interface Http {
  get<T>(url: string, params?: unknown): Promise<ResType<T>>
  post<T>(url: string, params?: any): Promise<ResType<T>>
  upload<T>(url: string, params: unknown): Promise<ResType<T>>
  download(url: string): void
}

const http: Http = {
  get(url, params) {
    return new Promise((resolve, reject) => {
      NProgressStart()
      axios
        .get(url, { params })
        .then((res) => {
          NProgressDone()
          resolve(res.data)
        })
        .catch((err) => {
          NProgressDone()
          reject(err.data)
        })
    })
  },
  post(url, params) {
    return new Promise((resolve, reject) => {
      NProgressStart()
      axios
        .post(url, JSON.stringify(params))
        .then((res) => {
          NProgressDone()
          resolve(res.data)
        })
        .catch((err) => {
          NProgressDone()
          reject(err.data)
        })
    })
  },
  upload(url, params) {
    return new Promise((resolve, reject) => {
      NProgressStart()
      axios
        .post(url, params, {
          headers: { 'Content-Type': 'multipart/form-data' },
        })
        .then((res) => {
          NProgressDone()
          resolve(res.data)
        })
        .catch((err) => {
          NProgressDone()
          reject(err.data)
        })
    })
  },
  download(url) {
    const iframe = document.createElement('iframe')
    iframe.style.display = 'none'
    iframe.src = url
    iframe.onload = function () {
      document.body.removeChild(iframe)
    }
    document.body.appendChild(iframe)
  },
}
export default http
