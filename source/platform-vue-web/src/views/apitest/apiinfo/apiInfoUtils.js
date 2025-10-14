/**
 * 接口信息相关工具函数
 */

// 请求方法类型映射
export const METHOD_TYPES = {
    GET: { label: 'GET', type: 'success', color: '#67C23A' },
    POST: { label: 'POST', type: 'primary', color: '#409EFF' },
    PUT: { label: 'PUT', type: 'warning', color: '#E6A23C' },
    DELETE: { label: 'DELETE', type: 'danger', color: '#F56C6C' },
    PATCH: { label: 'PATCH', type: 'info', color: '#909399' },
    HEAD: { label: 'HEAD', type: '', color: '#C0C4CC' },
    OPTIONS: { label: 'OPTIONS', type: '', color: '#C0C4CC' }
}

// 获取请求方法标签类型
export const getMethodTagType = (method) => {
    return METHOD_TYPES[method]?.type || ''
}

// 获取请求方法颜色
export const getMethodColor = (method) => {
    return METHOD_TYPES[method]?.color || '#C0C4CC'
}

// 验证URL格式
export const validateUrl = (url) => {
    if (!url) return false
    const pattern = /^(https?:\/\/)?([\da-z\.-]+)\.([a-z\.]{2,6})([\/\w \.-]*)*\/?$/
    return pattern.test(url) || url.startsWith('http://') || url.startsWith('https://')
}

// 格式化JSON字符串
export const formatJson = (data) => {
    if (!data) return ''
    if (typeof data === 'string') {
        try {
            const obj = JSON.parse(data)
            return JSON.stringify(obj, null, 2)
        } catch {
            return data
        }
    } else if (typeof data === 'object') {
        return JSON.stringify(data, null, 2)
    }
    return data
}

// 解析JSON字符串
export const parseJson = (jsonStr) => {
    try {
        return JSON.parse(jsonStr)
    } catch {
        return null
    }
}

// 变量替换（支持 ${varName} 格式）
export const replaceVariables = (str, variables) => {
    if (!str || !variables) return str

    let result = str
    Object.keys(variables).forEach(key => {
        const regex = new RegExp(`\\$\\{${key}\\}`, 'g')
        result = result.replace(regex, variables[key])
    })

    return result
}

// 提取URL参数
export const extractUrlParams = (url) => {
    if (!url || !url.includes('?')) return {}

    const paramsStr = url.split('?')[1]
    const params = {}

    paramsStr.split('&').forEach(param => {
        const [key, value] = param.split('=')
        if (key) {
            params[key] = decodeURIComponent(value || '')
        }
    })

    return params
}

// 构建URL（带参数）
export const buildUrl = (baseUrl, params) => {
    if (!params || Object.keys(params).length === 0) return baseUrl

    const queryString = Object.keys(params)
        .filter(key => params[key] !== null && params[key] !== undefined)
        .map(key => `${encodeURIComponent(key)}=${encodeURIComponent(params[key])}`)
        .join('&')

    return queryString ? `${baseUrl}?${queryString}` : baseUrl
}

// 深拷贝对象
export const deepClone = (obj) => {
    if (obj === null || typeof obj !== 'object') return obj

    if (obj instanceof Date) return new Date(obj)
    if (obj instanceof Array) return obj.map(item => deepClone(item))

    const clonedObj = {}
    Object.keys(obj).forEach(key => {
        clonedObj[key] = deepClone(obj[key])
    })

    return clonedObj
}

// 生成UUID
export const generateUuid = () => {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
        const r = Math.random() * 16 | 0
        const v = c === 'x' ? r : (r & 0x3 | 0x8)
        return v.toString(16)
    })
}

// 下载文件
export const downloadFile = (content, filename, type = 'text/plain') => {
    const blob = new Blob([content], { type })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    a.click()
    URL.revokeObjectURL(url)
}

// 复制到剪贴板
export const copyToClipboard = async (text) => {
    try {
        await navigator.clipboard.writeText(text)
        return true
    } catch {
        // 降级方案
        const textarea = document.createElement('textarea')
        textarea.value = text
        textarea.style.position = 'fixed'
        textarea.style.opacity = '0'
        document.body.appendChild(textarea)
        textarea.select()
        const success = document.execCommand('copy')
        document.body.removeChild(textarea)
        return success
    }
}

// 防抖函数
export const debounce = (func, wait = 300) => {
    let timeout
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout)
            func(...args)
        }
        clearTimeout(timeout)
        timeout = setTimeout(later, wait)
    }
}

// 节流函数
export const throttle = (func, limit = 300) => {
    let inThrottle
    return function executedFunction(...args) {
        if (!inThrottle) {
            func(...args)
            inThrottle = true
            setTimeout(() => inThrottle = false, limit)
        }
    }
}

