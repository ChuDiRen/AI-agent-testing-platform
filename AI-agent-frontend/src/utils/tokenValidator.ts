// Copyright (c) 2025 左岚. All rights reserved.

import { getToken, getRefreshToken, removeToken, removeRefreshToken } from './auth'

// Token版本控制
const TOKEN_VERSION_KEY = 'vite-vue3-ts-token-version'
const CURRENT_TOKEN_VERSION = '1.0.0'

// 设置token版本
export const setTokenVersion = (version: string = CURRENT_TOKEN_VERSION): void => {
  localStorage.setItem(TOKEN_VERSION_KEY, version)
}

// 获取token版本
export const getTokenVersion = (): string | null => {
  return localStorage.getItem(TOKEN_VERSION_KEY)
}

// 检查token版本是否匹配
export const isTokenVersionValid = (): boolean => {
  const currentVersion = getTokenVersion()
  return currentVersion === CURRENT_TOKEN_VERSION
}

// JWT token解析（简单版本，仅用于检查过期时间）
export const parseJWT = (token: string): any => {
  try {
    const base64Url = token.split('.')[1]
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/')
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split('')
        .map(c => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join('')
    )
    return JSON.parse(jsonPayload)
  } catch (error) {
    console.warn('Failed to parse JWT token:', error)
    return null
  }
}

// 检查token是否过期
export const isTokenExpired = (token: string): boolean => {
  const payload = parseJWT(token)
  if (!payload || !payload.exp) {
    return true // 无法解析或没有过期时间，视为过期
  }
  
  const currentTime = Math.floor(Date.now() / 1000)
  return payload.exp < currentTime
}

// 检查token是否有效（格式正确且未过期）
export const isTokenValid = (token: string): boolean => {
  if (!token || token.trim() === '') {
    return false
  }
  
  // 检查JWT格式（应该有3个部分，用.分隔）
  const parts = token.split('.')
  if (parts.length !== 3) {
    return false
  }
  
  // 检查是否过期
  return !isTokenExpired(token)
}

// 清理所有token相关数据
export const clearAllTokenData = (): void => {
  console.log('Clearing all token data...')
  
  // 清理认证相关的cookies和localStorage
  removeToken()
  removeRefreshToken()
  
  // 清理localStorage中的其他认证相关数据
  const keysToRemove = [
    TOKEN_VERSION_KEY,
    'vite-vue3-ts-user-info',
    'vite-vue3-ts-permissions',
    'vite-vue3-ts-routes'
  ]
  
  keysToRemove.forEach(key => {
    localStorage.removeItem(key)
  })
  
  // 清理sessionStorage中的认证相关数据
  const sessionKeysToRemove = [
    'vite-vue3-ts-token',
    'vite-vue3-ts-refresh-token',
    'user-info',
    'permissions'
  ]
  
  sessionKeysToRemove.forEach(key => {
    sessionStorage.removeItem(key)
  })
  
  console.log('All token data cleared')
}

// 自动检测并清理无效token
export const autoCleanupInvalidTokens = (): boolean => {
  console.log('Starting automatic token validation...')
  
  let needsCleanup = false
  
  // 检查token版本
  if (!isTokenVersionValid()) {
    console.log('Token version mismatch, cleanup needed')
    needsCleanup = true
  }
  
  // 检查access token
  const accessToken = getToken()
  if (accessToken && !isTokenValid(accessToken)) {
    console.log('Invalid access token detected, cleanup needed')
    needsCleanup = true
  }
  
  // 检查refresh token
  const refreshToken = getRefreshToken()
  if (refreshToken && !isTokenValid(refreshToken)) {
    console.log('Invalid refresh token detected, cleanup needed')
    needsCleanup = true
  }
  
  // 如果需要清理，执行清理操作
  if (needsCleanup) {
    clearAllTokenData()
    console.log('Invalid tokens cleaned up successfully')
    return true
  }
  
  // 如果token有效，更新版本标记
  if (accessToken && isTokenValid(accessToken)) {
    setTokenVersion()
    console.log('Tokens are valid, version updated')
  }
  
  return false
}

// 初始化token验证器（在应用启动时调用）
export const initTokenValidator = (): boolean => {
  console.log('Initializing token validator...')
  
  const wasCleanedUp = autoCleanupInvalidTokens()
  
  if (wasCleanedUp) {
    console.log('Token validator: Cleanup performed, user needs to re-login')
  } else {
    console.log('Token validator: All tokens are valid')
  }
  
  return wasCleanedUp
}