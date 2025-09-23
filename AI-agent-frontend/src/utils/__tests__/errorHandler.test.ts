/**
 * 错误处理器测试
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ErrorHandler, ErrorType, handleApiError } from '../errorHandler'

// Mock Element Plus
vi.mock('element-plus', () => ({
  ElMessage: vi.fn(),
  ElMessageBox: {
    alert: vi.fn()
  }
}))

// Mock router
const mockPush = vi.fn()
vi.mock('@/router', () => ({
  default: {
    push: mockPush,
    currentRoute: {
      value: {
        path: '/test'
      }
    }
  }
}))

// Mock user store
const mockClearUserData = vi.fn()
vi.mock('@/store', () => ({
  useUserStore: () => ({
    clearUserData: mockClearUserData
  })
}))

describe('ErrorHandler', () => {
  let errorHandler: ErrorHandler

  beforeEach(() => {
    vi.clearAllMocks()
    errorHandler = ErrorHandler.getInstance()
    errorHandler.clearErrorHistory()
  })

  describe('parseError', () => {
    it('should parse network error correctly', () => {
      const networkError = {
        message: 'Network Error',
        code: 'ECONNABORTED'
      }

      const result = errorHandler.handleApiError(networkError, { showMessage: false })

      expect(result.type).toBe(ErrorType.TIMEOUT_ERROR)
      expect(result.message).toContain('请求超时')
    })

    it('should parse 401 error correctly', () => {
      const authError = {
        response: {
          status: 401,
          data: {
            message: '未登录'
          }
        }
      }

      const result = errorHandler.handleApiError(authError, { showMessage: false })

      expect(result.type).toBe(ErrorType.AUTH_ERROR)
      expect(result.message).toBe('未登录')
    })

    it('should parse validation error correctly', () => {
      const validationError = {
        response: {
          status: 422,
          data: {
            message: '数据验证失败',
            error_code: 'VALIDATION_ERROR'
          }
        }
      }

      const result = errorHandler.handleApiError(validationError, { showMessage: false })

      expect(result.type).toBe(ErrorType.VALIDATION_ERROR)
      expect(result.message).toBe('数据验证失败')
    })

    it('should parse server error correctly', () => {
      const serverError = {
        response: {
          status: 500,
          data: {
            message: '服务器内部错误'
          }
        }
      }

      const result = errorHandler.handleApiError(serverError, { showMessage: false })

      expect(result.type).toBe(ErrorType.UNKNOWN_ERROR)
      expect(result.message).toBe('服务器内部错误')
    })
  })

  describe('showErrorMessage', () => {
    it('should show error message when enabled', () => {
      const error = {
        response: {
          status: 400,
          data: {
            message: '请求参数错误'
          }
        }
      }

      errorHandler.handleApiError(error, { showMessage: true })

      expect(ElMessage).toHaveBeenCalledWith({
        type: 'error',
        message: '请求参数错误',
        duration: 5000,
        showClose: true
      })
    })

    it('should not show message when disabled', () => {
      const error = {
        response: {
          status: 400,
          data: {
            message: '请求参数错误'
          }
        }
      }

      errorHandler.handleApiError(error, { showMessage: false })

      expect(ElMessage).not.toHaveBeenCalled()
    })
  })

  describe('autoRedirect', () => {
    it('should redirect to login on auth error', () => {
      const authError = {
        response: {
          status: 401,
          data: {
            message: '未登录'
          }
        }
      }

      errorHandler.handleApiError(authError, { autoRedirect: true, showMessage: false })

      expect(mockClearUserData).toHaveBeenCalled()
      expect(mockPush).toHaveBeenCalledWith('/login')
    })

    it('should not redirect when disabled', () => {
      const authError = {
        response: {
          status: 401,
          data: {
            message: '未登录'
          }
        }
      }

      errorHandler.handleApiError(authError, { autoRedirect: false, showMessage: false })

      expect(mockPush).not.toHaveBeenCalled()
    })
  })

  describe('error history', () => {
    it('should add errors to history', () => {
      const error1 = { response: { status: 400, data: { message: 'Error 1' } } }
      const error2 = { response: { status: 500, data: { message: 'Error 2' } } }

      errorHandler.handleApiError(error1, { showMessage: false })
      errorHandler.handleApiError(error2, { showMessage: false })

      const history = errorHandler.getErrorHistory()
      expect(history).toHaveLength(2)
      expect(history[0].message).toBe('Error 2') // 最新的在前
      expect(history[1].message).toBe('Error 1')
    })

    it('should limit history size', () => {
      // 创建超过最大历史记录数的错误
      for (let i = 0; i < 60; i++) {
        const error = { response: { status: 400, data: { message: `Error ${i}` } } }
        errorHandler.handleApiError(error, { showMessage: false })
      }

      const history = errorHandler.getErrorHistory()
      expect(history.length).toBeLessThanOrEqual(50) // 默认最大50条
    })

    it('should filter errors by type', () => {
      const networkError = { message: 'Network Error' }
      const authError = { response: { status: 401, data: { message: 'Auth Error' } } }

      errorHandler.handleApiError(networkError, { showMessage: false })
      errorHandler.handleApiError(authError, { showMessage: false })

      const authErrors = errorHandler.getErrorsByType(ErrorType.AUTH_ERROR)
      expect(authErrors).toHaveLength(1)
      expect(authErrors[0].message).toBe('Auth Error')
    })

    it('should clear error history', () => {
      const error = { response: { status: 400, data: { message: 'Test Error' } } }
      errorHandler.handleApiError(error, { showMessage: false })

      expect(errorHandler.getErrorHistory()).toHaveLength(1)

      errorHandler.clearErrorHistory()
      expect(errorHandler.getErrorHistory()).toHaveLength(0)
    })
  })

  describe('getDefaultErrorMessage', () => {
    it('should return correct message for known status codes', () => {
      const testCases = [
        { status: 400, expected: '请求参数错误' },
        { status: 401, expected: '未登录或登录已过期' },
        { status: 403, expected: '没有权限访问该资源' },
        { status: 404, expected: '请求的资源不存在' },
        { status: 422, expected: '请求数据验证失败' },
        { status: 500, expected: '服务器内部错误' },
        { status: 502, expected: '网关错误' },
        { status: 503, expected: '服务暂时不可用' }
      ]

      testCases.forEach(({ status, expected }) => {
        const error = { response: { status, data: {} } }
        const result = errorHandler.handleApiError(error, { showMessage: false })
        expect(result.message).toBe(expected)
      })
    })

    it('should return generic message for unknown status codes', () => {
      const error = { response: { status: 418, data: {} } }
      const result = errorHandler.handleApiError(error, { showMessage: false })
      expect(result.message).toBe('请求失败 (418)')
    })
  })

  describe('convenience function', () => {
    it('should work with handleApiError function', () => {
      const error = { response: { status: 400, data: { message: 'Test Error' } } }
      const result = handleApiError(error, { showMessage: false })

      expect(result.type).toBe(ErrorType.BUSINESS_ERROR)
      expect(result.message).toBe('Test Error')
    })
  })

  describe('singleton pattern', () => {
    it('should return same instance', () => {
      const instance1 = ErrorHandler.getInstance()
      const instance2 = ErrorHandler.getInstance()

      expect(instance1).toBe(instance2)
    })
  })
})

describe('validationErrorUtils', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('formatValidationErrors', () => {
    const { validationErrorUtils } = require('../errorHandler')

    it('should format field errors correctly', () => {
      const errors = [
        { field: 'username', message: '用户名不能为空' },
        { field: 'email', message: '邮箱格式不正确' }
      ]

      const result = validationErrorUtils.formatValidationErrors(errors)
      expect(result).toBe('username: 用户名不能为空; email: 邮箱格式不正确')
    })

    it('should handle errors without field', () => {
      const errors = [
        { message: '验证失败1' },
        { msg: '验证失败2' }
      ]

      const result = validationErrorUtils.formatValidationErrors(errors)
      expect(result).toBe('验证失败1; 验证失败2')
    })

    it('should return default message for non-array input', () => {
      const result = validationErrorUtils.formatValidationErrors('not an array' as any)
      expect(result).toBe('数据验证失败')
    })

    it('should handle empty array', () => {
      const result = validationErrorUtils.formatValidationErrors([])
      expect(result).toBe('')
    })
  })

  describe('showValidationErrors', () => {
    const { validationErrorUtils } = require('../errorHandler')

    it('should set form fields when formRef provided', () => {
      const mockSetFields = vi.fn()
      const formRef = { setFields: mockSetFields }

      const errors = [
        { field: 'username', message: '用户名不能为空' },
        { field: 'email', message: '邮箱格式不正确' }
      ]

      validationErrorUtils.showValidationErrors(errors, formRef)

      expect(mockSetFields).toHaveBeenCalledWith({
        username: '用户名不能为空',
        email: '邮箱格式不正确'
      })
      expect(ElMessage).not.toHaveBeenCalled()
    })

    it('should show general message when no formRef', () => {
      const errors = [
        { field: 'username', message: '用户名不能为空' }
      ]

      validationErrorUtils.showValidationErrors(errors)

      expect(ElMessage.warning).toHaveBeenCalledWith('username: 用户名不能为空')
    })
  })
})
