// Copyright (c) 2025 左岚. All rights reserved.
/**
 * 网络请求配置中心
 * 统一管理所有网络相关的配置参数
 */

// 网络请求配置
export const NETWORK_CONFIG = {
  // 基础超时配置
  DEFAULT_TIMEOUT: 30000, // 默认超时时间30秒
  UPLOAD_TIMEOUT: 60000, // 文件上传超时时间60秒
  DOWNLOAD_TIMEOUT: 120000, // 文件下载超时时间120秒

  // 重试配置
  MAX_RETRIES: 2, // 最大重试次数
  RETRY_DELAY_BASE: 1000, // 重试延迟基数(毫秒)

  // 特定API超时配置
  API_TIMEOUTS: {
    LOGIN: 15000, // 登录接口15秒
    LOGOUT: 10000, // 登出接口10秒
    USER_INFO: 20000, // 用户信息20秒
    PERMISSIONS: 25000, // 权限获取25秒
    MENUS: 20000, // 菜单获取20秒
    LOGS: 30000, // 日志查询30秒
    DASHBOARD: 15000, // 仪表板15秒
    FILE_UPLOAD: 60000, // 文件上传60秒
    EXPORT: 120000, // 数据导出120秒
  },

  // 错误重试配置
  RETRY_CONDITIONS: {
    NETWORK_ERROR: true, // 网络错误重试
    TIMEOUT: true, // 超时重试
    SERVER_ERROR: false, // 服务器错误不重试
  },

  // 请求去重与短期缓存（防止重复接口）
  REQUEST_DEDUP: {
    ENABLED: true, // 启用去重
    DEFAULT_TTL: 2000, // 默认去重/缓存时效2秒
    TTLS: {
      '^/menus/get-user-menus$': 5000, // 用户菜单5秒
      '^/users/get-user-roles$': 3000, // 用户角色3秒
      '^/users/get-user-info$': 3000, // 用户信息3秒
      '^/dashboard/get-system-info$': 3000, // 仪表盘系统信息3秒
      '^/dashboard/get-statistics-data$': 3000, // 仪表盘统计3秒
    },
  },
}

// 获取指定API的超时时间
export function getApiTimeout(apiType: keyof typeof NETWORK_CONFIG.API_TIMEOUTS): number {
  return NETWORK_CONFIG.API_TIMEOUTS[apiType] || NETWORK_CONFIG.DEFAULT_TIMEOUT
}

// 计算重试延迟时间
export function getRetryDelay(retryCount: number): number {
  return NETWORK_CONFIG.RETRY_DELAY_BASE * (retryCount + 1)
}

// 判断是否应该重试
export function shouldRetry(error: any, retryCount: number): boolean {
  if (retryCount >= NETWORK_CONFIG.MAX_RETRIES) {
    return false
  }

  const { code, response } = error

  // 网络错误或超时错误重试
  if (code === 'ECONNABORTED' || code === 'NETWORK_ERROR' || !response) {
    return NETWORK_CONFIG.RETRY_CONDITIONS.NETWORK_ERROR || NETWORK_CONFIG.RETRY_CONDITIONS.TIMEOUT
  }

  // 服务器错误不重试
  if (response && response.status >= 500) {
    return NETWORK_CONFIG.RETRY_CONDITIONS.SERVER_ERROR
  }

  return false
}

// 根据URL返回去重TTL
export function getDedupeTTL(url: string): number {
  const conf = NETWORK_CONFIG.REQUEST_DEDUP
  if (!conf?.ENABLED) return 0
  for (const pattern in conf.TTLS) {
    try {
      const re = new RegExp(pattern)
      if (re.test(url)) return conf.TTLS[pattern as keyof typeof conf.TTLS]
    } catch {}
  }
  return conf.DEFAULT_TTL
}
