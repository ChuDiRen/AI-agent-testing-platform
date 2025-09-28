/**
 * 统一错误处理机制
 */

import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '@/store'
import router from '@/router'
import { clearAllTokenData } from '@/utils/tokenValidator' // 导入token清理功能

// 错误类型枚举
export enum ErrorType {
  NETWORK_ERROR = 'NETWORK_ERROR',
  AUTH_ERROR = 'AUTH_ERROR',
  VALIDATION_ERROR = 'VALIDATION_ERROR',
  BUSINESS_ERROR = 'BUSINESS_ERROR',
  UNKNOWN_ERROR = 'UNKNOWN_ERROR',
  TIMEOUT_ERROR = 'TIMEOUT_ERROR'
}

// 错误信息接口
export interface ApiError {
  type: ErrorType
  message: string
  code?: string | number
  details?: any
  timestamp?: string
}

// 错误处理配置
interface ErrorHandlerConfig {
  showMessage?: boolean
  showModal?: boolean
  autoRedirect?: boolean
  logError?: boolean
}

// 默认错误配置
const defaultConfig: ErrorHandlerConfig = {
  showMessage: true,
  showModal: false,
  autoRedirect: true,
  logError: true
}

/**
 * 统一错误处理器
 */
export class ErrorHandler {
  private static instance: ErrorHandler
  private errorHistory: ApiError[] = []
  private maxHistorySize = 50

  private constructor() {}

  public static getInstance(): ErrorHandler {
    if (!ErrorHandler.instance) {
      ErrorHandler.instance = new ErrorHandler()
    }
    return ErrorHandler.instance
  }

  /**
   * 处理API错误
   */
  public async handleApiError(error: any, config: ErrorHandlerConfig = {}): Promise<ApiError> {
    const finalConfig = { ...defaultConfig, ...config }
    const apiError = this.parseError(error)

    // 记录错误
    if (finalConfig.logError) {
      this.logError(apiError)
    }

    // 显示错误消息
    if (finalConfig.showMessage) {
      this.showErrorMessage(apiError)
    }

    // 显示错误弹窗
    if (finalConfig.showModal) {
      this.showErrorModal(apiError)
    }

    // 自动重定向
    if (finalConfig.autoRedirect) {
      await this.handleAutoRedirect(apiError)
    }

    // 添加到错误历史
    this.addToHistory(apiError)

    return apiError
  }

  /**
   * 解析错误对象
   */
  private parseError(error: any): ApiError {
    // 网络错误
    if (!error.response) {
      if (error.code === 'ECONNABORTED' || error.message?.includes('timeout')) {
        return {
          type: ErrorType.TIMEOUT_ERROR,
          message: '请求超时，请检查网络连接',
          code: 'TIMEOUT',
          timestamp: new Date().toISOString()
        }
      }
      
      return {
        type: ErrorType.NETWORK_ERROR,
        message: '网络连接失败，请检查网络设置',
        code: 'NETWORK_ERROR',
        timestamp: new Date().toISOString()
      }
    }

    const { status, data } = error.response
    const errorCode = data?.error_code || data?.code || status
    const errorMessage = data?.message || data?.error || this.getDefaultErrorMessage(status)

    // 根据状态码确定错误类型
    let errorType: ErrorType

    switch (status) {
      case 400:
        errorType = data?.error_code === 'VALIDATION_ERROR' ? ErrorType.VALIDATION_ERROR : ErrorType.BUSINESS_ERROR
        break
      case 401:
      case 403:
        errorType = ErrorType.AUTH_ERROR
        break
      case 422:
        errorType = ErrorType.VALIDATION_ERROR
        break
      case 500:
      case 502:
      case 503:
      case 504:
        errorType = ErrorType.UNKNOWN_ERROR
        break
      default:
        errorType = ErrorType.BUSINESS_ERROR
    }

    return {
      type: errorType,
      message: errorMessage,
      code: errorCode,
      details: data?.error_data || data?.errors,
      timestamp: new Date().toISOString()
    }
  }

  /**
   * 获取默认错误消息
   */
  private getDefaultErrorMessage(status: number): string {
    const messages: Record<number, string> = {
      400: '请求参数错误',
      401: '未登录或登录已过期',
      403: '没有权限访问该资源',
      404: '请求的资源不存在',
      422: '请求数据验证失败',
      429: '请求过于频繁，请稍后重试',
      500: '服务器内部错误',
      502: '网关错误',
      503: '服务暂时不可用',
      504: '请求超时'
    }

    return messages[status] || `请求失败 (${status})`
  }

  /**
   * 显示错误消息
   */
  private showErrorMessage(error: ApiError): void {
    const messageType = this.getMessageType(error.type)
    
    ElMessage({
      type: messageType,
      message: error.message,
      duration: 5000,
      showClose: true
    })
  }

  /**
   * 显示错误弹窗
   */
  private showErrorModal(error: ApiError): void {
    ElMessageBox.alert(error.message, '错误提示', {
      type: 'error',
      confirmButtonText: '确定'
    })
  }

  /**
   * 获取消息类型
   */
  private getMessageType(errorType: ErrorType): 'success' | 'warning' | 'info' | 'error' {
    switch (errorType) {
      case ErrorType.VALIDATION_ERROR:
        return 'warning'
      case ErrorType.AUTH_ERROR:
      case ErrorType.NETWORK_ERROR:
      case ErrorType.UNKNOWN_ERROR:
      case ErrorType.TIMEOUT_ERROR:
        return 'error'
      default:
        return 'error'
    }
  }

  /**
   * 自动重定向处理
   */
  private async handleAutoRedirect(error: ApiError): Promise<void> {
    if (error.type === ErrorType.AUTH_ERROR) {
      // 认证错误，使用统一的token清理功能
      await clearAllTokenData()
      
      // 清除用户store数据
      try {
        const userStore = useUserStore()
        await userStore.clearUserData()
      } catch (e) {
        console.warn('Failed to clear user data, Pinia may not be initialized')
      }

      if (router.currentRoute.value.path !== '/login') {
        // 延迟跳转，提供更好的用户体验
        setTimeout(() => {
          router.push('/login')
        }, 1000)
      }
    }
  }

  /**
   * 记录错误日志
   */
  private logError(error: ApiError): void {
    const logData = {
      ...error,
      url: window.location.href,
      userAgent: navigator.userAgent,
      timestamp: new Date().toISOString()
    }

    console.error('API Error:', logData)

    // 在生产环境中，可以发送到错误监控服务
    if (import.meta.env.PROD) {
      this.sendToMonitoring(logData)
    }
  }

  /**
   * 发送到监控服务（可选）
   */
  private sendToMonitoring(_errorData: any): void {
    // 这里可以集成第三方错误监控服务，如 Sentry
    // try {
    //   // 发送到监控服务
    // } catch (e) {
    //   console.error('Failed to send error to monitoring service:', e)
    // }
  }

  /**
   * 添加到错误历史
   */
  private addToHistory(error: ApiError): void {
    this.errorHistory.unshift(error)
    
    // 保持历史记录在限制范围内
    if (this.errorHistory.length > this.maxHistorySize) {
      this.errorHistory = this.errorHistory.slice(0, this.maxHistorySize)
    }
  }

  /**
   * 获取错误历史
   */
  public getErrorHistory(): ApiError[] {
    return [...this.errorHistory]
  }

  /**
   * 清除错误历史
   */
  public clearErrorHistory(): void {
    this.errorHistory = []
  }

  /**
   * 获取特定类型的错误
   */
  public getErrorsByType(type: ErrorType): ApiError[] {
    return this.errorHistory.filter(error => error.type === type)
  }
}

// 导出单例实例
export const errorHandler = ErrorHandler.getInstance()

// 便捷方法
export const handleApiError = async (error: any, config?: ErrorHandlerConfig) => {
  return await errorHandler.handleApiError(error, config)
}

// 错误处理装饰器
export function withErrorHandling(config?: ErrorHandlerConfig) {
  return function (_target: any, _propertyKey: string, descriptor: PropertyDescriptor) {
    const originalMethod = descriptor.value

    descriptor.value = async function (...args: any[]) {
      try {
        return await originalMethod.apply(this, args)
      } catch (error) {
        handleApiError(error, config)
        throw error
      }
    }

    return descriptor
  }
}

// 验证错误处理工具
export const validationErrorUtils = {
  /**
   * 格式化验证错误
   */
  formatValidationErrors(errors: any[]): string {
    if (!Array.isArray(errors)) return '数据验证失败'
    
    return errors
      .map(error => {
        if (error.field && error.message) {
          return `${error.field}: ${error.message}`
        }
        return error.message || error.msg || '验证失败'
      })
      .join('; ')
  },

  /**
   * 显示表单验证错误
   */
  showValidationErrors(errors: any[], formRef?: any): void {
    if (formRef && formRef.setFields) {
      // Element Plus 表单验证
      const fieldErrors: Record<string, string> = {}
      errors.forEach(error => {
        if (error.field) {
          fieldErrors[error.field] = error.message
        }
      })
      formRef.setFields(fieldErrors)
    } else {
      // 显示通用错误消息
      const message = this.formatValidationErrors(errors)
      ElMessage.warning(message)
    }
  }
}
