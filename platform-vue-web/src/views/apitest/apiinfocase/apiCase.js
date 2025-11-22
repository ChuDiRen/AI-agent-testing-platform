/**
 * API用例相关接口 - 兼容层
 * 从 apiInfoCase.js 重新导出关键字相关函数
 */

import {
    queryKeywordsByType as _queryKeywordsByType,
    getKeywordFields as _getKeywordFields
} from './apiInfoCase.js'

/**
 * 根据操作类型ID查询关键字列表
 * @param {Number} operationTypeId - 操作类型ID
 * @returns {Promise}
 */
export function queryKeywordsByType(operationTypeId) {
    return _queryKeywordsByType(operationTypeId)
}

/**
 * 获取关键字的字段描述
 * @param {Number} keywordId - 关键字ID
 * @returns {Promise}
 */
export function getKeywordFields(keywordId) {
    return _getKeywordFields(keywordId)
}

// 也可以直接重新导出所有函数
export * from './apiInfoCase.js'
