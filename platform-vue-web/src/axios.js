import axios from "axios" // 修复循环导入问题
import { ref } from "vue"
import { ElLoading, ElMessage } from 'element-plus'
import router from './router/index.js'

const service = axios.create({
    baseURL: "/api"
})
const nums = ref(0)
const loading = ref(null)

// 是否正在刷新 token
let isRefreshing = false
// 等待刷新 token 的请求队列
let requestsQueue = []

function open() {
    if (nums.value <= 0) {
        loading.value = ElLoading.service({
            lock: true,
            text: '加载中',
            background: 'rgba(0, 0, 0, 0.05)',
        })
    }
    nums.value++
}

function close() {
    nums.value--
    if (nums.value <= 0) {
        nums.value = 0
        loading.value?.close()
    }
}

// 获取 token
function getToken() {
    return localStorage.getItem('token')
}

// 设置 token
function setToken(token) {
    localStorage.setItem('token', token)
}

// 刷新 token
async function refreshToken() {
    const token = getToken()
    if (!token) return null

    try {
        const response = await axios.post('/api/refreshToken', {}, {
            headers: { 'Authorization': `Bearer ${token}` }
        })
        if (response.data.code === 200 && response.data.data?.access_token) {
            const newToken = response.data.data.access_token
            setToken(newToken)
            return newToken
        }
        return null
    } catch (error) {
        console.error('刷新 token 失败:', error)
        return null
    }
}

// 添加请求拦截器
service.interceptors.request.use(config => {
    open()
    // 自动添加 token
    const token = getToken()
    if (token) {
        config.headers['Authorization'] = `Bearer ${token}`
    }
    return config
}, error => {
    close()
    ElMessage.error('网络异常，请稍后再试')
    return Promise.reject(error)
})

// 添加响应拦截器
service.interceptors.response.use(response => {
    close()
    if (response.data.code != 200) {
        // 401 表示 token 过期，但不在这里处理（在 error 中处理 HTTP 401）
        if (response.data.code !== 401) {
            ElMessage.error(response.data.msg + ',状态码:' + response.data.code)
        }
    }
    return response
}, async error => {
    close()

    const originalRequest = error.config

    // 处理 401 错误（token 过期）
    if (error.response?.status === 401 && !originalRequest._retry) {
        // 如果是刷新 token 请求本身失败，直接跳转登录
        if (originalRequest.url?.includes('/refreshToken')) {
            ElMessage.error('登录已过期，请重新登录')
            router.push('/login')
            return Promise.reject(error)
        }

        // 标记为已重试，避免无限循环
        originalRequest._retry = true

        // 如果正在刷新 token，将请求加入队列等待
        if (isRefreshing) {
            return new Promise((resolve, reject) => {
                requestsQueue.push({ resolve, reject, config: originalRequest })
            })
        }

        isRefreshing = true

        try {
            // 刷新 token
            const newToken = await refreshToken()

            if (newToken) {
                // 更新原请求的 token
                originalRequest.headers['Authorization'] = `Bearer ${newToken}`

                // 重新发送队列中的请求
                requestsQueue.forEach(({ resolve, config }) => {
                    config.headers['Authorization'] = `Bearer ${newToken}`
                    resolve(service(config))
                })
                requestsQueue = []

                // 重新发送原请求
                return service(originalRequest)
            } else {
                // 刷新失败，跳转登录
                ElMessage.error('登录已过期，请重新登录')
                router.push('/login')
                return Promise.reject(error)
            }
        } catch (refreshError) {
            // 刷新失败，跳转登录
            ElMessage.error('登录已过期，请重新登录')
            router.push('/login')
            return Promise.reject(refreshError)
        } finally {
            isRefreshing = false
        }
    }

    // 处理其他 HTTP 错误
    if (error.response) {
        switch (error.response.status) {
            case 403:
                ElMessage.error('无权限访问')
                router.push('/403')
                break
            case 500:
                ElMessage.error('服务器错误')
                router.push('/500')
                break
            case 404:
                ElMessage.error('请求的资源不存在')
                break
            default:
                ElMessage.error('网络异常，请稍后再试')
        }
    } else {
        ElMessage.error('网络异常，请稍后再试')
    }

    return Promise.reject(error)
})

export default service