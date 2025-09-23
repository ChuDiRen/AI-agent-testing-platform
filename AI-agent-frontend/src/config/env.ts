/**
 * 环境配置管理
 */

interface AppConfig {
  // 环境信息
  env: string
  // API配置
  apiBaseUrl: string
  apiPrefix: string
  // 应用信息
  appTitle: string
  appVersion: string
  // 功能开关
  enableMock: boolean
  enableDevtools: boolean
  enableDebug: boolean
  // 其他配置
  uploadSizeLimit: number
  requestTimeout: number
}

/**
 * 获取环境变量
 */
function getEnvValue(key: string, defaultValue: string = ''): string {
  return import.meta.env[key] || defaultValue
}

/**
 * 获取布尔型环境变量
 */
function getBooleanEnvValue(key: string, defaultValue: boolean = false): boolean {
  const value = getEnvValue(key)
  if (!value) return defaultValue
  return value.toLowerCase() === 'true'
}

/**
 * 获取数字型环境变量
 */
function getNumberEnvValue(key: string, defaultValue: number = 0): number {
  const value = getEnvValue(key)
  if (!value) return defaultValue
  const num = Number(value)
  return isNaN(num) ? defaultValue : num
}

/**
 * 应用配置
 */
export const appConfig: AppConfig = {
  // 环境信息
  env: getEnvValue('VITE_ENV', 'development'),
  
  // API配置
  apiBaseUrl: getEnvValue('VITE_API_BASE_URL', 'http://localhost:8000'),
  apiPrefix: getEnvValue('VITE_API_PREFIX', '/api/v1'),
  
  // 应用信息
  appTitle: getEnvValue('VITE_APP_TITLE', 'AI智能代理测试平台'),
  appVersion: getEnvValue('VITE_APP_VERSION', '1.0.0'),
  
  // 功能开关
  enableMock: getBooleanEnvValue('VITE_ENABLE_MOCK', false),
  enableDevtools: getBooleanEnvValue('VITE_ENABLE_DEVTOOLS', false),
  enableDebug: getBooleanEnvValue('VITE_ENABLE_DEBUG', false),
  
  // 其他配置
  uploadSizeLimit: getNumberEnvValue('VITE_UPLOAD_SIZE_LIMIT', 10485760), // 10MB
  requestTimeout: getNumberEnvValue('VITE_REQUEST_TIMEOUT', 30000), // 30秒
}

/**
 * 是否为开发环境
 */
export const isDevelopment = appConfig.env === 'development'

/**
 * 是否为生产环境
 */
export const isProduction = appConfig.env === 'production'

/**
 * 完整的API基础URL
 */
export const fullApiUrl = `${appConfig.apiBaseUrl}${appConfig.apiPrefix}`

/**
 * 打印配置信息（仅在开发环境）
 */
if (isDevelopment && appConfig.enableDebug) {
  console.log('🔧 应用配置:', appConfig)
  console.log('🌐 API地址:', fullApiUrl)
}

export default appConfig
