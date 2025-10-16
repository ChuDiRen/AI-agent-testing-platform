<template>
  <div class="yaml-viewer">
    <div class="viewer-header">
      <span class="title">{{ title }}</span>
      <div class="actions">
        <el-button type="text" icon="el-icon-document-copy" @click="handleCopy">复制</el-button>
        <el-button type="text" icon="el-icon-download" @click="handleDownload">下载</el-button>
        <el-button v-if="editable" type="text" icon="el-icon-edit" @click="handleEdit">编辑</el-button>
      </div>
    </div>
    <div class="viewer-content" ref="contentRef">
      <pre><code>{{ formattedContent }}</code></pre>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'

const props = defineProps({
  content: {
    type: String,
    default: ''
  },
  title: {
    type: String,
    default: 'YAML内容'
  },
  editable: {
    type: Boolean,
    default: false
  },
  filename: {
    type: String,
    default: 'content.yaml'
  }
})

const emit = defineEmits(['edit', 'update'])

const contentRef = ref(null)

// 格式化YAML内容（添加语法高亮样式的类名）
const formattedContent = computed(() => {
  if (!props.content) return '# 暂无内容'
  return props.content
})

// 复制到剪贴板
const handleCopy = async () => {
  try {
    await navigator.clipboard.writeText(props.content)
    ElMessage.success('复制成功')
  } catch (error) {
    // 降级方案：使用传统方法
    const textarea = document.createElement('textarea')
    textarea.value = props.content
    textarea.style.position = 'fixed'
    textarea.style.opacity = '0'
    document.body.appendChild(textarea)
    textarea.select()
    try {
      document.execCommand('copy')
      ElMessage.success('复制成功')
    } catch (e) {
      ElMessage.error('复制失败')
    }
    document.body.removeChild(textarea)
  }
}

// 下载为YAML文件
const handleDownload = () => {
  try {
    const blob = new Blob([props.content], { type: 'text/yaml;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = props.filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
    ElMessage.success('下载成功')
  } catch (error) {
    ElMessage.error('下载失败')
  }
}

// 编辑
const handleEdit = () => {
  emit('edit', props.content)
}

// 监听内容变化，自动滚动到底部
watch(() => props.content, () => {
  if (contentRef.value) {
    contentRef.value.scrollTop = contentRef.value.scrollHeight
  }
})
</script>

<style scoped>
.yaml-viewer {
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  background: #fff;
  overflow: hidden;
}

.viewer-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 15px;
  background: #f5f7fa;
  border-bottom: 1px solid #dcdfe6;
}

.viewer-header .title {
  font-weight: 600;
  color: #303133;
  font-size: 14px;
}

.viewer-header .actions {
  display: flex;
  gap: 5px;
}

.viewer-content {
  max-height: 500px;
  overflow: auto;
  padding: 15px;
  background: #fafafa;
}

.viewer-content pre {
  margin: 0;
  padding: 0;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 13px;
  line-height: 1.6;
  color: #2c3e50;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.viewer-content code {
  display: block;
  padding: 0;
  margin: 0;
  background: transparent;
  color: inherit;
}

/* 滚动条样式 */
.viewer-content::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

.viewer-content::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
}

.viewer-content::-webkit-scrollbar-thumb:hover {
  background: #a0a0a0;
}

.viewer-content::-webkit-scrollbar-track {
  background: #f0f0f0;
}
</style>

