/**
 * YAML测试用例生成工具
 */

import { parseJson, replaceVariables } from './apiInfoUtils.js'

/**
 * 生成YAML测试用例
 * @param {Object} apiInfo - 接口信息
 * @param {Object} options - 配置选项
 * @returns {String} YAML格式字符串
 */
export const generateYaml = (apiInfo, options = {}) => {
    const {
        testName = apiInfo.api_name || '接口测试',
        contextVars = {},
        preScript = [],
        postScript = [],
        variableExtracts = [],
        assertions = []
    } = options

    let yaml = `desc: ${testName}\n`

    // 添加前置脚本
    if (preScript && preScript.length > 0) {
        yaml += `pre_script:\n`
        preScript.forEach(script => {
            yaml += `  - ${script}\n`
        })
    }

    yaml += `steps:\n`

    // 主请求步骤
    yaml += generateRequestStep(apiInfo, testName)

    // 变量提取步骤
    if (variableExtracts && variableExtracts.length > 0) {
        variableExtracts.forEach(extract => {
            yaml += generateExtractStep(extract)
        })
    }

    // 断言步骤
    if (assertions && assertions.length > 0) {
        assertions.forEach(assertion => {
            yaml += generateAssertionStep(assertion)
        })
    }

    // 添加后置脚本
    if (postScript && postScript.length > 0) {
        yaml += `post_script:\n`
        postScript.forEach(script => {
            yaml += `  - ${script}\n`
        })
    }

    // 添加数据驱动
    if (contextVars && Object.keys(contextVars).length > 0) {
        yaml += `\nddts:\n`
        yaml += `  - desc: ${testName}_数据\n`
        Object.entries(contextVars).forEach(([key, value]) => {
            yaml += `    ${key}: ${value}\n`
        })
    }

    return yaml
}

/**
 * 生成请求步骤
 */
const generateRequestStep = (apiInfo, stepName) => {
    const method = apiInfo.request_method || 'GET'
    const url = apiInfo.request_url || ''

    let yaml = `  - ${stepName}:\n`
    yaml += `      关键字: send_request\n`
    yaml += `      method: ${method}\n`
    yaml += `      url: ${url}\n`

    // 添加URL参数
    const params = parseJson(apiInfo.request_params)
    if (params && Object.keys(params).length > 0) {
        yaml += `      params:\n`
        Object.entries(params).forEach(([key, value]) => {
            yaml += `        ${key}: ${value}\n`
        })
    }

    // 添加请求头
    const headers = parseJson(apiInfo.request_headers)
    if (headers && Object.keys(headers).length > 0) {
        yaml += `      headers:\n`
        Object.entries(headers).forEach(([key, value]) => {
            yaml += `        ${key}: ${value}\n`
        })
    }

    // 添加请求体（仅POST/PUT/PATCH）
    if (['POST', 'PUT', 'PATCH'].includes(method)) {
        // JSON数据
        const jsonData = parseJson(apiInfo.requests_json_data)
        if (jsonData && Object.keys(jsonData).length > 0) {
            yaml += `      json:\n`
            yaml += formatJsonToYaml(jsonData, 8)
        }
        // form-data
        else {
            const formData = parseJson(apiInfo.request_form_datas)
            if (formData && Object.keys(formData).length > 0) {
                yaml += `      data:\n`
                Object.entries(formData).forEach(([key, value]) => {
                    yaml += `        ${key}: ${value}\n`
                })
            }
        }

        // 文件上传
        const files = parseJson(apiInfo.request_files)
        if (files && Object.keys(files).length > 0) {
            yaml += `      files:\n`
            Object.entries(files).forEach(([key, value]) => {
                yaml += `        ${key}: ${value}\n`
            })
        }
    }

    return yaml
}

/**
 * 生成变量提取步骤
 */
const generateExtractStep = (extract) => {
    const stepName = extract.description || `提取_${extract.var_name}`

    let yaml = `  - ${stepName}:\n`
    yaml += `      关键字: ex_jsonData\n`
    yaml += `      EXVALUE: ${extract.extract_path}\n`
    yaml += `      VARNAME: ${extract.var_name}\n`
    yaml += `      INDEX: ${extract.index || 0}\n`

    return yaml
}

/**
 * 生成断言步骤
 */
const generateAssertionStep = (assertion) => {
    const stepName = assertion.description || '断言验证'

    let yaml = `  - ${stepName}:\n`

    if (assertion.type === 'assert_text_comparators') {
        yaml += `      关键字: assert_text_comparators\n`
        yaml += `      VALUE: ${assertion.actual_value}\n`
        yaml += `      EXPECTED: ${assertion.expected_value}\n`
        yaml += `      OP_STR: ${assertion.operator || '=='}\n`
    } else if (assertion.type === 'assert_json_path') {
        yaml += `      关键字: ex_jsonData\n`
        yaml += `      EXVALUE: ${assertion.extract_path}\n`
        yaml += `      VARNAME: temp_${stepName}\n`
        yaml += `      INDEX: 0\n`
    } else if (assertion.type === 'assert_status_code') {
        yaml += `      关键字: assert_text_comparators\n`
        yaml += `      VALUE: \${response.status_code}\n`
        yaml += `      EXPECTED: ${assertion.expected_value}\n`
        yaml += `      OP_STR: ==\n`
    }

    return yaml
}

/**
 * 格式化JSON对象为YAML格式
 */
const formatJsonToYaml = (obj, indent = 0) => {
    let yaml = ''
    const spaces = ' '.repeat(indent)

    Object.entries(obj).forEach(([key, value]) => {
        if (typeof value === 'object' && value !== null && !Array.isArray(value)) {
            yaml += `${spaces}${key}:\n`
            yaml += formatJsonToYaml(value, indent + 2)
        } else if (Array.isArray(value)) {
            yaml += `${spaces}${key}:\n`
            value.forEach(item => {
                if (typeof item === 'object') {
                    yaml += `${spaces}  -\n`
                    yaml += formatJsonToYaml(item, indent + 4)
                } else {
                    yaml += `${spaces}  - ${item}\n`
                }
            })
        } else {
            yaml += `${spaces}${key}: ${value}\n`
        }
    })

    return yaml
}

/**
 * 验证YAML格式
 */
export const validateYaml = (yamlStr) => {
    try {
        // 简单验证：检查基本结构
        if (!yamlStr.includes('desc:')) return false
        if (!yamlStr.includes('steps:')) return false
        return true
    } catch {
        return false
    }
}

/**
 * YAML转JSON（简单实现）
 */
export const yamlToJson = (yamlStr) => {
    // 这里需要一个完整的YAML解析器，暂时返回null
    // 可以使用 js-yaml 库来实现
    console.warn('YAML转JSON功能需要引入 js-yaml 库')
    return null
}

