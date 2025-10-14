/**
 * 时间格式化工具
 * 统一时间格式为 YYYY-MM-DD HH:MM:SS
 */

/**
 * 格式化时间字符串或Date对象为标准格式
 * @param {string|Date} time - 时间字符串或Date对象
 * @returns {string} 格式化后的时间字符串 YYYY-MM-DD HH:MM:SS
 */
export function formatDateTime(time) {
    if (!time) return ''

    let date
    if (typeof time === 'string') {
        date = new Date(time)
    } else if (time instanceof Date) {
        date = time
    } else {
        return ''
    }

    // 检查日期是否有效
    if (isNaN(date.getTime())) {
        return ''
    }

    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')
    const hours = String(date.getHours()).padStart(2, '0')
    const minutes = String(date.getMinutes()).padStart(2, '0')
    const seconds = String(date.getSeconds()).padStart(2, '0')

    return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`
}

/**
 * 格式化时间为日期格式
 * @param {string|Date} time - 时间字符串或Date对象
 * @returns {string} 格式化后的日期字符串 YYYY-MM-DD
 */
export function formatDate(time) {
    if (!time) return ''

    let date
    if (typeof time === 'string') {
        date = new Date(time)
    } else if (time instanceof Date) {
        date = time
    } else {
        return ''
    }

    // 检查日期是否有效
    if (isNaN(date.getTime())) {
        return ''
    }

    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')

    return `${year}-${month}-${day}`
}

/**
 * 获取当前时间的标准格式字符串
 * @returns {string} 当前时间 YYYY-MM-DD HH:MM:SS
 */
export function getCurrentDateTime() {
    return formatDateTime(new Date())
}

/**
 * 获取当前日期的标准格式字符串
 * @returns {string} 当前日期 YYYY-MM-DD
 */
export function getCurrentDate() {
    return formatDate(new Date())
}
