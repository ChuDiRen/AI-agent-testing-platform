<template>
  <div class="yaml-preview">
    <div class="yaml-actions">
      <el-button size="small" @click="copyYaml">复制YAML</el-button>
      <el-button size="small" @click="downloadYaml">下载YAML</el-button>
    </div>
    <pre class="yaml-content">{{ yamlContent }}</pre>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { ElMessage } from 'element-plus'

const props = defineProps({
  apiInfo: {
    type: Object,
    required: true
  },
  contextVars: {
    type: Object,
    default: () => ({})
  },
  assertions: {
    type: Array,
    default: () => []
  }
})

// 生成YAML内容
const yamlContent = computed(() => {
  const testName = props.apiInfo.api_name || '接口测试'
  const method = props.apiInfo.request_method || 'GET'
  const url = props.apiInfo.request_url || ''

  let yaml = `desc: ${testName}\n`
  yaml += `steps:\n`
  yaml += `  - ${testName}:\n`
  yaml += `      关键字: send_request\n`
  yaml += `      method: ${method}\n`
  yaml += `      url: ${url}\n`

  // 添加参数
  if (props.apiInfo.request_params && props.apiInfo.request_params !== '{}') {
    try {
      const params = JSON.parse(props.apiInfo.request_params)
      if (Object.keys(params).length > 0) {
        yaml += `      params:\n`
        Object.entries(params).forEach(([key, value]) => {
          yaml += `        ${key}: ${value}\n`
        })
      }
    } catch (e) {
      // 忽略解析错误
    }
  }

  // 添加请求头
  if (props.apiInfo.request_headers && props.apiInfo.request_headers !== '{}') {
    try {
      const headers = JSON.parse(props.apiInfo.request_headers)
      if (Object.keys(headers).length > 0) {
        yaml += `      headers:\n`
        Object.entries(headers).forEach(([key, value]) => {
          yaml += `        ${key}: ${value}\n`
        })
      }
    } catch (e) {
      // 忽略解析错误
    }
  }

  // 添加请求体（仅POST/PUT/PATCH）
  if (['POST', 'PUT', 'PATCH'].includes(method)) {
    // JSON数据
    if (props.apiInfo.requests_json_data && props.apiInfo.requests_json_data !== '{}') {
      try {
        const jsonData = JSON.parse(props.apiInfo.requests_json_data)
        if (Object.keys(jsonData).length > 0) {
          yaml += `      json:\n`
          Object.entries(jsonData).forEach(([key, value]) => {
            yaml += `        ${key}: ${typeof value === 'string' ? value : JSON.stringify(value)}\n`
          })
        }
      } catch (e) {
        // 忽略解析错误
      }
    }
    // form-data
    else if (props.apiInfo.request_form_datas && props.apiInfo.request_form_datas !== '{}') {
      try {
        const formData = JSON.parse(props.apiInfo.request_form_datas)
        if (Object.keys(formData).length > 0) {
          yaml += `      data:\n`
          Object.entries(formData).forEach(([key, value]) => {
            yaml += `        ${key}: ${value}\n`
          })
        }
      } catch (e) {
        // 忽略解析错误
      }
    }
  }

  // 添加断言
  if (props.assertions && props.assertions.length > 0) {
    props.assertions.forEach((assertion, index) => {
      if (assertion.type === 'assert_text_comparators') {
        yaml += `  - ${assertion.description || `断言${index + 1}`}:\n`
        yaml += `      关键字: assert_text_comparators\n`
        yaml += `      VALUE: ${assertion.actual_value}\n`
        yaml += `      EXPECTED: ${assertion.expected_value}\n`
        yaml += `      OP_STR: ${assertion.operator || '=='}\n`
      }
    })
  }

  // 添加数据驱动（如果有变量）
  if (props.contextVars && Object.keys(props.contextVars).length > 0) {
    yaml += `\nddts:\n`
    yaml += `  - desc: ${testName}_数据\n`
    Object.entries(props.contextVars).forEach(([key, value]) => {
      yaml += `    ${key}: ${value}\n`
    })
  }

  return yaml
})

// 复制YAML
const copyYaml = async () => {
  try {
    await navigator.clipboard.writeText(yamlContent.value)
    ElMessage.success('已复制到剪贴板')
  } catch (e) {
    ElMessage.error('复制失败')
  }
}

// 下载YAML
const downloadYaml = () => {
  const filename = `${props.apiInfo.api_name || 'test'}.yaml`
  const blob = new Blob([yamlContent.value], { type: 'text/yaml' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  a.click()
  URL.revokeObjectURL(url)
  ElMessage.success('下载成功')
}
</script>

<style scoped lang="scss">
.yaml-preview {
  .yaml-actions {
    margin-bottom: 10px;
    display: flex;
    gap: 10px;
  }

  .yaml-content {
    background: #f5f5f5;
    padding: 15px;
    border-radius: 4px;
    overflow: auto;
    max-height: 350px;
    font-size: 12px;
    font-family: 'Courier New', monospace;
    white-space: pre-wrap;
    word-wrap: break-word;
  }
}
</style>

