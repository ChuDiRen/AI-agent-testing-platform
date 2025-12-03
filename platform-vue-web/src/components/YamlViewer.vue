<template>
  <div class="yaml-viewer">
    <div class="viewer-header" v-if="showToolbar">
      <span class="title">{{ title || 'YAML' }}</span>
      <div class="header-actions">
        <el-button size="small" text @click="toggleExpand">
          {{ isExpanded ? '折叠全部' : '展开全部' }}
        </el-button>
        <el-button v-if="copyable" size="small" type="primary" @click="handleCopy">
          <el-icon><CopyDocument /></el-icon>
          复制
        </el-button>
      </div>
    </div>
    <pre class="yaml-content" :class="{ collapsed: !isExpanded }"><code v-html="highlightedYaml"></code></pre>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { CopyDocument } from '@element-plus/icons-vue'

const props = defineProps({
  content: {
    type: [String, Object],
    default: ''
  },
  title: {
    type: String,
    default: ''
  },
  copyable: {
    type: Boolean,
    default: true
  },
  showToolbar: {
    type: Boolean,
    default: false
  }
})

const isExpanded = ref(true)

const toggleExpand = () => {
  isExpanded.value = !isExpanded.value
}

// JSON 转 YAML
const jsonToYaml = (obj, indent = 0) => {
  const spaces = '  '.repeat(indent)
  let yaml = ''
  
  if (obj === null) return 'null'
  if (obj === undefined) return ''
  if (typeof obj !== 'object') {
    if (typeof obj === 'string') {
      // 多行字符串或含特殊字符的字符串
      if (obj.includes('\n') || obj.includes(':') || obj.includes('#')) {
        return `"${obj.replace(/"/g, '\\"')}"`
      }
      return obj
    }
    return String(obj)
  }
  
  if (Array.isArray(obj)) {
    if (obj.length === 0) return '[]'
    obj.forEach(item => {
      if (typeof item === 'object' && item !== null) {
        yaml += `${spaces}- `
        const itemYaml = jsonToYaml(item, indent + 1)
        // 移除第一行的缩进
        yaml += itemYaml.replace(/^\s+/, '') + '\n'
      } else {
        yaml += `${spaces}- ${jsonToYaml(item, indent + 1)}\n`
      }
    })
    return yaml.trimEnd()
  }
  
  const keys = Object.keys(obj)
  if (keys.length === 0) return '{}'
  
  keys.forEach(key => {
    const value = obj[key]
    if (typeof value === 'object' && value !== null) {
      if (Array.isArray(value) && value.length === 0) {
        yaml += `${spaces}${key}: []\n`
      } else if (!Array.isArray(value) && Object.keys(value).length === 0) {
        yaml += `${spaces}${key}: {}\n`
      } else {
        yaml += `${spaces}${key}:\n${jsonToYaml(value, indent + 1)}\n`
      }
    } else {
      yaml += `${spaces}${key}: ${jsonToYaml(value, indent + 1)}\n`
    }
  })
  
  return yaml.trimEnd()
}

const formattedContent = computed(() => {
  if (!props.content) return ''
  if (typeof props.content === 'object') {
    return jsonToYaml(props.content)
  }
  // 尝试解析 JSON 字符串
  try {
    const parsed = JSON.parse(props.content)
    return jsonToYaml(parsed)
  } catch {
    return props.content
  }
})

// 语法高亮
const highlightedYaml = computed(() => {
  const yaml = formattedContent.value
  if (!yaml) return ''
  
  return yaml
    .replace(/^(\s*)([\w\u4e00-\u9fa5_-]+):/gm, '$1<span class="key">$2</span>:')  // 键名
    .replace(/:\s*(".*?")/g, ': <span class="string">$1</span>')  // 字符串值
    .replace(/:\s*(\d+\.?\d*)/g, ': <span class="number">$1</span>')  // 数字
    .replace(/:\s*(true|false)/g, ': <span class="boolean">$1</span>')  // 布尔
    .replace(/:\s*(null)/g, ': <span class="null">$1</span>')  // null
    .replace(/^(\s*-)/gm, '<span class="dash">$1</span>')  // 列表符号
})

const handleCopy = async () => {
  try {
    await navigator.clipboard.writeText(formattedContent.value)
    ElMessage.success('已复制到剪贴板')
  } catch (error) {
    ElMessage.error('复制失败')
  }
}
</script>

<style scoped>
.yaml-viewer {
  background: #1e1e1e;
  border-radius: 8px;
  overflow: hidden;
}

.viewer-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 16px;
  background: #2d2d2d;
  border-bottom: 1px solid #404040;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.title {
  color: #e0e0e0;
  font-size: 13px;
  font-weight: 500;
}

.yaml-content {
  margin: 0;
  padding: 16px;
  color: #d4d4d4;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 13px;
  line-height: 1.6;
  overflow: auto;
  max-height: 500px;
  white-space: pre;
}

.yaml-content.collapsed {
  max-height: 150px;
}

.yaml-content code {
  font-family: inherit;
}

/* 语法高亮 */
.yaml-content :deep(.key) {
  color: #9cdcfe;
}

.yaml-content :deep(.string) {
  color: #ce9178;
}

.yaml-content :deep(.number) {
  color: #b5cea8;
}

.yaml-content :deep(.boolean) {
  color: #569cd6;
}

.yaml-content :deep(.null) {
  color: #569cd6;
}

.yaml-content :deep(.dash) {
  color: #d4d4d4;
}
</style>
