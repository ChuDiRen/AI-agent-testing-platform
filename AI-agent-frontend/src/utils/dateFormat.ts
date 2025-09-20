// Copyright (c) 2025 左岚. All rights reserved.
/**
 * 日期时间格式化工具
 * 统一管理所有时间格式化相关功能
 */

/**
 * 标准时间格式配置
 */
export const DATE_FORMATS = {
  // 标准格式：2025/9/13 09:36:19
  STANDARD: 'YYYY/M/D HH:mm:ss',
  // 日期格式：2025/9/13
  DATE_ONLY: 'YYYY/M/D',
  // 时间格式：09:36:19
  TIME_ONLY: 'HH:mm:ss',
  // 短时间格式：09:36
  TIME_SHORT: 'HH:mm',
  // 月日格式：9/13
  MONTH_DAY: 'M/D',
  // 年月格式：2025/9
  YEAR_MONTH: 'YYYY/M',
} as const

/**
 * 格式化日期时间为标准格式：2025/9/13 09:36:19
 * @param date 日期字符串、Date对象或时间戳
 * @param format 格式化模板，默认为标准格式
 * @returns 格式化后的时间字符串
 */
export function formatDateTime(
  date: string | Date | number | null | undefined,
  format: string = DATE_FORMATS.STANDARD,
): string {
  if (!date) return ''

  try {
    let dateObj: Date

    if (typeof date === 'string') {
      // 处理ISO格式字符串
      dateObj = new Date(date)
    } else if (typeof date === 'number') {
      // 处理时间戳
      dateObj = new Date(date)
    } else if (date instanceof Date) {
      dateObj = date
    } else {
      return ''
    }

    // 检查日期是否有效
    if (isNaN(dateObj.getTime())) {
      return ''
    }

    // 手动格式化，避免依赖第三方库
    const year = dateObj.getFullYear()
    const month = dateObj.getMonth() + 1
    const day = dateObj.getDate()
    const hours = dateObj.getHours()
    const minutes = dateObj.getMinutes()
    const seconds = dateObj.getSeconds()

    return format
      .replace('YYYY', year.toString())
      .replace('M', month.toString())
      .replace('D', day.toString())
      .replace('HH', hours.toString().padStart(2, '0'))
      .replace('mm', minutes.toString().padStart(2, '0'))
      .replace('ss', seconds.toString().padStart(2, '0'))
  } catch (error) {
    console.warn('日期格式化失败:', error)
    return ''
  }
}

/**
 * 格式化为标准日期时间格式：2025/9/13 09:36:19
 */
export function formatStandardDateTime(date: string | Date | number | null | undefined): string {
  return formatDateTime(date, DATE_FORMATS.STANDARD)
}

/**
 * 格式化为日期格式：2025/9/13
 */
export function formatDate(date: string | Date | number | null | undefined): string {
  return formatDateTime(date, DATE_FORMATS.DATE_ONLY)
}

/**
 * 格式化为时间格式：09:36:19
 */
export function formatTime(date: string | Date | number | null | undefined): string {
  return formatDateTime(date, DATE_FORMATS.TIME_ONLY)
}

/**
 * 格式化为短时间格式：09:36
 */
export function formatTimeShort(date: string | Date | number | null | undefined): string {
  return formatDateTime(date, DATE_FORMATS.TIME_SHORT)
}

/**
 * 相对时间格式化（如：刚刚、5分钟前、1小时前等）
 */
export function formatRelativeTime(date: string | Date | number | null | undefined): string {
  if (!date) return ''

  try {
    const dateObj = new Date(date)
    const now = new Date()
    const diff = now.getTime() - dateObj.getTime()

    if (diff < 0) return formatStandardDateTime(date) // 未来时间直接显示

    const seconds = Math.floor(diff / 1000)
    const minutes = Math.floor(seconds / 60)
    const hours = Math.floor(minutes / 60)
    const days = Math.floor(hours / 24)

    if (seconds < 60) return '刚刚'
    if (minutes < 60) return `${minutes}分钟前`
    if (hours < 24) return `${hours}小时前`
    if (days < 7) return `${days}天前`

    // 超过7天显示标准格式
    return formatStandardDateTime(date)
  } catch (error) {
    return formatStandardDateTime(date)
  }
}

/**
 * 获取当前时间的标准格式字符串
 */
export function getCurrentDateTime(): string {
  return formatStandardDateTime(new Date())
}

/**
 * 获取当前日期的标准格式字符串
 */
export function getCurrentDate(): string {
  return formatDate(new Date())
}

/**
 * 判断是否为今天
 */
export function isToday(date: string | Date | number | null | undefined): boolean {
  if (!date) return false

  try {
    const dateObj = new Date(date)
    const today = new Date()

    return (
      dateObj.getFullYear() === today.getFullYear() &&
      dateObj.getMonth() === today.getMonth() &&
      dateObj.getDate() === today.getDate()
    )
  } catch (error) {
    return false
  }
}

/**
 * 判断是否为昨天
 */
export function isYesterday(date: string | Date | number | null | undefined): boolean {
  if (!date) return false

  try {
    const dateObj = new Date(date)
    const yesterday = new Date()
    yesterday.setDate(yesterday.getDate() - 1)

    return (
      dateObj.getFullYear() === yesterday.getFullYear() &&
      dateObj.getMonth() === yesterday.getMonth() &&
      dateObj.getDate() === yesterday.getDate()
    )
  } catch (error) {
    return false
  }
}

/**
 * 智能时间格式化
 * 今天显示时间，昨天显示"昨天 时间"，其他显示完整日期时间
 */
export function formatSmartDateTime(date: string | Date | number | null | undefined): string {
  if (!date) return ''

  if (isToday(date)) {
    return `今天 ${formatTime(date)}`
  } else if (isYesterday(date)) {
    return `昨天 ${formatTime(date)}`
  } else {
    return formatStandardDateTime(date)
  }
}
