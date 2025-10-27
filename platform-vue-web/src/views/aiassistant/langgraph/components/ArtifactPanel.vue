<template>
  <el-drawer
    v-model="visible"
    :title="title || 'Artifact'"
    direction="rtl"
    size="45%"
    :before-close="handleClose"
  >
    <div class="artifact-content">
      <!-- 工具栏 -->
      <div class="artifact-toolbar">
        <el-button-group>
          <el-button size="small" @click="handleCopy">
            <el-icon><DocumentCopy /></el-icon>
            复制
          </el-button>
          <el-button size="small" @click="handleDownload">
            <el-icon><Download /></el-icon>
            下载
          </el-button>
        </el-button-group>
      </div>

      <!-- 内容展示 -->
      <div class="artifact-body">
        <!-- Markdown 内容 -->
        <div v-if="contentType === 'markdown'" class="markdown-content">
          <div v-html="renderedMarkdown" />
        </div>

        <!-- 代码内容 -->
        <div v-else-if="contentType === 'code'" class="code-content">
          <pre><code :class="`language-${language}`">{{ content }}</code></pre>
        </div>

        <!-- 纯文本内容 -->
        <div v-else class="text-content">
          <pre>{{ content }}</pre>
        </div>
      </div>
    </div>
  </el-drawer>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { DocumentCopy, Download } from '@element-plus/icons-vue'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  title: {
    type: String,
    default: 'Artifact'
  },
  content: {
    type: String,
    default: ''
  },
  contentType: {
    type: String,
    default: 'text', // text, markdown, code
    validator: (value) => ['text', 'markdown', 'code'].includes(value)
  },
  language: {
    type: String,
    default: 'javascript'
  }
})

const emit = defineEmits(['update:modelValue', 'close'])

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

// 简单的 Markdown 渲染（可以后续集成 markdown-it 或其他库）
const renderedMarkdown = computed(() => {
  if (props.contentType !== 'markdown') return ''
  
  // 这里是简化版本，实际应该使用专业的 Markdown 解析器
  let html = props.content
    .replace(/### (.*)/g, '<h3>$1</h3>')
    .replace(/## (.*)/g, '<h2>$1</h2>')
    .replace(/# (.*)/g, '<h1>$1</h1>')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/`(.*?)`/g, '<code>$1</code>')
    .replace(/\n/g, '<br>')
  
  return html
})

const handleClose = () => {
  emit('close')
  visible.value = false
}

const handleCopy = async () => {
  try {
    await navigator.clipboard.writeText(props.content)
    ElMessage.success('复制成功')
  } catch (error) {
    console.error('Copy failed:', error)
    ElMessage.error('复制失败')
  }
}

const handleDownload = () => {
  try {
    const blob = new Blob([props.content], { type: 'text/plain;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `artifact_${Date.now()}.${getFileExtension()}`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
    ElMessage.success('下载成功')
  } catch (error) {
    console.error('Download failed:', error)
    ElMessage.error('下载失败')
  }
}

const getFileExtension = () => {
  const extensions = {
    'markdown': 'md',
    'code': props.language === 'javascript' ? 'js' : props.language,
    'text': 'txt'
  }
  return extensions[props.contentType] || 'txt'
}
</script>

<style scoped>
.artifact-content {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.artifact-toolbar {
  padding: 12px;
  border-bottom: 1px solid #e4e7ed;
  background-color: #f5f7fa;
}

.artifact-body {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  background-color: #fff;
}

.markdown-content,
.text-content,
.code-content {
  line-height: 1.8;
  color: #303133;
}

.markdown-content :deep(h1) {
  font-size: 24px;
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 2px solid #e4e7ed;
}

.markdown-content :deep(h2) {
  font-size: 20px;
  margin-bottom: 12px;
  margin-top: 20px;
}

.markdown-content :deep(h3) {
  font-size: 16px;
  margin-bottom: 10px;
  margin-top: 16px;
}

.markdown-content :deep(code) {
  background-color: #f5f7fa;
  padding: 2px 6px;
  border-radius: 3px;
  font-family: 'Courier New', monospace;
  font-size: 14px;
}

.code-content pre {
  background-color: #f5f7fa;
  padding: 16px;
  border-radius: 8px;
  overflow-x: auto;
  margin: 0;
}

.code-content code {
  font-family: 'Courier New', monospace;
  font-size: 14px;
  line-height: 1.6;
}

.text-content pre {
  white-space: pre-wrap;
  word-break: break-word;
  margin: 0;
  font-family: 'Courier New', monospace;
  font-size: 14px;
}
</style>

