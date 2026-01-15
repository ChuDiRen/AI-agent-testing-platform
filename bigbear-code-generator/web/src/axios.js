import axios from "axios"
import { ElLoading, ElMessage } from 'element-plus'
import router from './router/index.js'
import { useUserStore } from '~/stores/index.js'

const service = axios.create({
    baseURL: "/api",
    timeout: 30000 // 30秒超时
})

// Loading 状态管理
let loadingInstance = null
let requestCount = 0

/**
 * 显示 Loading
 */
function showLoading() {
    requestCount++
    if (requestCount === 1) {
        loadingInstance = ElLoading.service({
            lock: true,
            text: '加载中...',
            background: 'rgba(0, 0, 0, 0.05)',
            spinner: 'el-icon-loading'
        })
    }
}

/**
 * 关闭 Loading
 */
function hideLoading() {
    requestCount--
    if (requestCount === 0 && loadingInstance) {
        loadingInstance.close()
        loadingInstance = null
    }
    if (requestCount < 0) {
        requestCount = 0
    }
}

/**
 * 获取 Token
 */
export function getToken() {
    return localStorage.getItem('token')
}

/**
 * 设置 Token
 */
export function setToken(token) {
    if (token) {
        localStorage.setItem('token', token)
    } else {
        localStorage.removeItem('token')
    }
}

/**
 * 从响应中提取新的 Token
 */
function extractTokenFromResponse(response) {
    const token = response.data?.data?.access_token || response.data?.data?.token
    if (token) {
        setToken(token)
        return token
    }
    return null
}

/**
 * 显示错误消息
 */
function showError(error) {
    // 优先使用后端返回的错误消息
    if (error.response?.data?.msg) {
        ElMessage.error(error.response.data.msg)
    } else if (error.message) {
        ElMessage.error(error.message)
    } else {
        ElMessage.error('网络异常，请稍后再试')
    }
}

/**
 * 处理 HTTP 状态码错误
 */
function handleHttpError(error) {
    const status = error.response?.status

    switch (status) {
        case 401:
            // Token 过期或无效，在拦截器中统一处理
            break
        case 403:
            ElMessage.error('无权限访问')
            router.push('/403')
            break
        case 404:
            ElMessage.error('请求的资源不存在')
            break
        case 500:
            ElMessage.error('服务器错误')
            router.push('/500')
            break
        case 502:
        case 503:
        case 504:
            ElMessage.error('服务暂时不可用，请稍后再试')
            break
        default:
            if (status && status >= 500) {
                ElMessage.error('服务器错误，请稍后再试')
            }
    }
}

/**
 * 检查是否需要跳转到登录页
 */
function shouldRedirectToLogin(error) {
    const status = error.response?.status
    const url = error.config?.url

    // 401 错误（Token 过期）但不是刷新 Token 的请求
    if (status === 401 && !url?.includes('/refreshToken')) {
        return true
    }

    return false
}

/**
 * 清除用户信息并跳转到登录页
 */
function clearUserAndRedirect() {
    const userStore = useUserStore()
    userStore.clearUserInfo()
    ElMessage.warning('登录已过期，请重新登录')
    router.push('/login')
}

// 请求拦截器
service.interceptors.request.use(
    config => {
        // 显示 Loading（可以在特定请求中通过 skipLoading: true 跳过）
        if (!config.skipLoading) {
            showLoading()
        }

        // 自动添加 Token
        const token = getToken()
        if (token) {
            config.headers = config.headers || {}
            config.headers['Authorization'] = `Bearer ${token}`
        }

        return config
    },
    error => {
        hideLoading()
        ElMessage.error('网络异常，请稍后再试')
        return Promise.reject(error)
    }
)

// 响应拦截器
service.interceptors.response.use(
    response => {
        hideLoading()

        // 提取并保存新的 Token（如果有的话）
        const newToken = extractTokenFromResponse(response)
        if (newToken) {
            console.log('Token 已刷新')
        }

        // 检查业务状态码
        if (response.data?.code && response.data.code !== 200) {
            // 401 表示 Token 过期
            if (response.data.code === 401) {
                clearUserAndRedirect()
                return Promise.reject(new Error('Token 已过期'))
            }

            // 其他业务错误
            const errorMsg = response.data.msg || '操作失败'
            if (response.data.code !== 401) {
                ElMessage.error(errorMsg)
            }

            return Promise.reject(new Error(errorMsg))
        }

        return response
    },
    error => {
        hideLoading()

        // 处理 HTTP 错误
        if (error.response) {
            handleHttpError(error)

            // 检查是否需要跳转到登录页
            if (shouldRedirectToLogin(error)) {
                clearUserAndRedirect()
            }
        } else {
            // 网络错误或超时
            showError(error)
        }

        return Promise.reject(error)
    }
)

export default service