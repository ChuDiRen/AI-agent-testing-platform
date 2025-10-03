// Copyright (c) 2025 左岚. All rights reserved.
/**
 * 全局错误处理
 */
import { ElMessage, ElNotification } from 'element-plus'

interface ErrorOptions {
  showMessage?: boolean
  showNotification?: boolean
  logError?: boolean
  customMessage?: string
}

export function useErrorHandler() {
  /**
   * 处理错误
   */
  const handleError = (error: any, options: ErrorOptions = {}) => {
    const {
      showMessage = true,
      showNotification = false,
      logError = true,
      customMessage
    } = options

    // 控制台输出错误（开发环境）
    if (logError && import.meta.env.DEV) {
      console.error('Error:', error)
    }

    // 提取错误消息
    let message = customMessage || '操作失败，请稍后重试'
    if (error?.response?.data?.msg) {
      message = error.response.data.msg
    } else if (error?.message) {
      message = error.message
    }

    // 显示错误提示
    if (showMessage) {
      ElMessage.error(message)
    }

    if (showNotification) {
      ElNotification.error({
        title: '错误',
        message,
        duration: 5000
      })
    }

    return message
  }

  /**
   * 处理网络错误
   */
  const handleNetworkError = (error: any) => {
    if (!navigator.onLine) {
      ElMessage.error('网络连接已断开，请检查网络设置')
      return
    }

    const status = error?.response?.status
    switch (status) {
      case 400:
        handleError(error, { customMessage: '请求参数错误' })
        break
      case 401:
        handleError(error, { customMessage: '登录已过期，请重新登录' })
        // 可以在这里触发跳转到登录页
        break
      case 403:
        handleError(error, { customMessage: '没有权限访问该资源' })
        break
      case 404:
        handleError(error, { customMessage: '请求的资源不存在' })
        break
      case 500:
        handleError(error, { customMessage: '服务器错误，请联系管理员' })
        break
      case 503:
        handleError(error, { customMessage: '服务暂时不可用，请稍后重试' })
        break
      default:
        handleError(error)
    }
  }

  /**
   * 表单验证错误处理
   */
  const handleValidationError = (errors: Record<string, string[]>) => {
    const firstError = Object.values(errors)[0]?.[0]
    if (firstError) {
      ElMessage.warning(firstError)
    }
  }

  /**
   * 业务错误处理
   */
  const handleBusinessError = (code: number, message?: string) => {
    const errorMessages: Record<number, string> = {
      1001: '用户不存在',
      1002: '密码错误',
      1003: '账号已被禁用',
      2001: '权限不足',
      3001: '数据不存在',
      3002: '数据已存在',
      4001: '操作过于频繁，请稍后重试'
    }

    const msg = message || errorMessages[code] || '操作失败'
    ElMessage.error(msg)
  }

  return {
    handleError,
    handleNetworkError,
    handleValidationError,
    handleBusinessError
  }
}

