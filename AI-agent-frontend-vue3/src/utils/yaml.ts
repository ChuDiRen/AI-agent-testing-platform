/**
 * YAML工具类
 */
import * as yaml from 'js-yaml'

export interface YamlTestCase {
  desc?: string
  pre_script?: any[]
  steps?: Array<Record<string, any>>
  post_script?: any[]
  ddts?: any[]
  context?: Record<string, any>
}

export interface FormTestCase {
  desc?: string
  pre_script?: any[]
  steps: Array<{
    name: string
    keyword: string
    params: Record<string, any>
  }>
  post_script?: any[]
  ddts?: any[]
  context?: Record<string, any>
}

export class YamlUtils {
  /**
   * 解析YAML字符串
   */
  static parse(yamlStr: string): YamlTestCase {
    try {
      const parsed = yaml.load(yamlStr) as YamlTestCase
      return parsed || {}
    } catch (error) {
      throw new Error(`YAML解析失败: ${error instanceof Error ? error.message : String(error)}`)
    }
  }

  /**
   * 将对象转换为YAML字符串
   */
  static stringify(obj: YamlTestCase): string {
    try {
      return yaml.dump(obj, {
        indent: 2,
        lineWidth: 120,
        noRefs: true,
        sortKeys: false,
        allowUnicode: true
      })
    } catch (error) {
      throw new Error(`YAML生成失败: ${error instanceof Error ? error.message : String(error)}`)
    }
  }

  /**
   * 验证YAML格式
   */
  static validate(yamlStr: string): { valid: boolean; error?: string } {
    try {
      yaml.load(yamlStr)
      return { valid: true }
    } catch (error) {
      return {
        valid: false,
        error: error instanceof Error ? error.message : String(error)
      }
    }
  }

  /**
   * 格式化YAML字符串
   */
  static format(yamlStr: string): string {
    try {
      const parsed = this.parse(yamlStr)
      return this.stringify(parsed)
    } catch (error) {
      throw new Error(`YAML格式化失败: ${error instanceof Error ? error.message : String(error)}`)
    }
  }

  /**
   * 将表单格式转换为YAML格式
   */
  static formToYaml(formCase: FormTestCase): string {
    const yamlCase: YamlTestCase = {
      desc: formCase.desc,
      pre_script: formCase.pre_script,
      steps: [],
      post_script: formCase.post_script,
      ddts: formCase.ddts,
      context: formCase.context
    }

    // 转换步骤格式
    if (formCase.steps) {
      yamlCase.steps = formCase.steps.map(step => {
        const stepObj: Record<string, any> = {}
        stepObj[step.keyword] = step.params
        return stepObj
      })
    }

    return this.stringify(yamlCase)
  }

  /**
   * 将YAML格式转换为表单格式
   */
  static yamlToForm(yamlStr: string): FormTestCase {
    const yamlCase = this.parse(yamlStr)

    const formCase: FormTestCase = {
      desc: yamlCase.desc,
      pre_script: yamlCase.pre_script || [],
      steps: [],
      post_script: yamlCase.post_script || [],
      ddts: yamlCase.ddts || [],
      context: yamlCase.context || {}
    }

    // 转换步骤格式
    if (yamlCase.steps && Array.isArray(yamlCase.steps)) {
      formCase.steps = yamlCase.steps.map((step, index) => {
        const keyword = Object.keys(step)[0]
        const params = step[keyword] || {}

        return {
          name: `步骤 ${index + 1}`,
          keyword,
          params
        }
      })
    }

    return formCase
  }

  /**
   * 生成默认的YAML模板
   */
  static generateTemplate(desc: string = '测试用例'): string {
    const template: YamlTestCase = {
      desc,
      steps: [
        {
          send_request: {
            url: 'https://api.example.com/test',
            method: 'GET',
            headers: {
              'Content-Type': 'application/json'
            }
          }
        },
        {
          assert_status_code: {
            EXPECTED: 200
          }
        }
      ]
    }

    return this.stringify(template)
  }

  /**
   * 获取YAML结构信息
   */
  static getStructure(yamlStr: string): {
    hasDesc: boolean
    hasPreScript: boolean
    stepCount: number
    hasPostScript: boolean
    hasDdts: boolean
    hasContext: boolean
  } {
    const yamlCase = this.parse(yamlStr)

    return {
      hasDesc: !!yamlCase.desc,
      hasPreScript: !!(yamlCase.pre_script && yamlCase.pre_script.length > 0),
      stepCount: (yamlCase.steps && yamlCase.steps.length) || 0,
      hasPostScript: !!(yamlCase.post_script && yamlCase.post_script.length > 0),
      hasDdts: !!(yamlCase.ddts && yamlCase.ddts.length > 0),
      hasContext: !!(yamlCase.context && Object.keys(yamlCase.context).length > 0)
    }
  }

  /**
   * 合并YAML配置
   */
  static merge(baseYaml: string, overrideYaml: string): string {
    const base = this.parse(baseYaml)
    const override = this.parse(overrideYaml)

    const merged = {
      ...base,
      ...override,
      // 特殊处理数组合并
      steps: override.steps || base.steps || [],
      pre_script: override.pre_script || base.pre_script || [],
      post_script: override.post_script || base.post_script || [],
      ddts: override.ddts || base.ddts || [],
      context: { ...base.context, ...override.context }
    }

    return this.stringify(merged)
  }
}