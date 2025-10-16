<template>
  <div class="json-editor">
    <div class="editor-header">
      <span class="title">{{ title }}</span>
      <div class="actions">
        <el-button type="text" icon="el-icon-check" @click="handleFormat">格式化</el-button>
        <el-button type="text" icon="el-icon-document-copy" @click="handleCopy">复制</el-button>
        <el-button type="text" icon="el-icon-refresh" @click="handleReset">重置</el-button>
        <el-button v-if="!readonly" type="primary" size="small" @click="handleSave">保存</el-button>
      </div>
    </div>
    <div class="editor-content">
      <textarea
        ref="textareaRef"
        v-model="editorContent"
        :readonly="readonly"
        :placeholder="placeholder"
        @input="handleInput"
        class="json-textarea"
        :class="{ 'has-error': hasError }"
      ></textarea>
      <div v-if="hasError" class="error-message">
        <i class="el-icon-warning"></i>
        {{ errorMessage }}
      </div>
    </div>
    <div v-if="showPreview" class="editor-preview">
      <div class="preview-header">预览</div>
      <div class="preview-content">
        <pre><code>{{ previewContent }}</code></pre>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

const props = defineProps({
  modelValue: {
    type: [String, Object, Array],
    default: ''
  },
  title: {
    type: String,
    default: 'JSON编辑器'
  },
  readonly: {
    type: Boolean,
    default: false
  },
  placeholder: {
    type: String,
    default: '请输入JSON内容...'
  },
  showPreview: {
    type: Boolean,
    default: true
  },
  autoFormat: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['update:modelValue', 'change', 'save'])

const textareaRef = ref(null)
const editorContent = ref('')
const hasError = ref(false)
const errorMessage = ref('')
const originalContent = ref('')

// 预览内容
const previewContent = computed(() => {
  if (hasError.value) return '// JSON格式错误，无法预览'
  try {
    const obj = JSON.parse(editorContent.value || '{}')
    return JSON.stringify(obj, null, 2)
  } catch (error) {
    return '// JSON格式错误，无法预览'
  }
})

// 初始化内容
const initContent = () => {
  let content = ''
  if (typeof props.modelValue === 'string') {
    content = props.modelValue
  } else if (props.modelValue !== null && props.modelValue !== undefined) {
    content = JSON.stringify(props.modelValue, null, 2)
  }
  editorContent.value = content
  originalContent.value = content
  validateJson()
}

// 验证JSON格式
const validateJson = () => {
  if (!editorContent.value.trim()) {
    hasError.value = false
    errorMessage.value = ''
    return true
  }
  
  try {
    JSON.parse(editorContent.value)
    hasError.value = false
    errorMessage.value = ''
    return true
  } catch (error) {
    hasError.value = true
    errorMessage.value = `JSON格式错误: ${error.message}`
    return false
  }
}

// 输入处理
const handleInput = () => {
  validateJson()
  if (!hasError.value) {
    try {
      const obj = JSON.parse(editorContent.value || '{}')
      emit('update:modelValue', obj)
      emit('change', obj)
    } catch (error) {
      // 忽略错误，等待用户继续输入
    }
  }
}

// 格式化JSON
const handleFormat = () => {
  if (!validateJson()) {
    ElMessage.error('JSON格式错误，无法格式化')
    return
  }
  
  try {
    const obj = JSON.parse(editorContent.value)
    editorContent.value = JSON.stringify(obj, null, 2)
    ElMessage.success('格式化成功')
  } catch (error) {
    ElMessage.error('格式化失败')
  }
}

// 复制到剪贴板
const handleCopy = async () => {
  try {
    await navigator.clipboard.writeText(editorContent.value)
    ElMessage.success('复制成功')
  } catch (error) {
    // 降级方案
    const textarea = document.createElement('textarea')
    textarea.value = editorContent.value
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

// 重置
const handleReset = () => {
  editorContent.value = originalContent.value
  validateJson()
  ElMessage.success('已重置')
}

// 保存
const handleSave = () => {
  if (!validateJson()) {
    ElMessage.error('JSON格式错误，无法保存')
    return
  }
  
  try {
    const obj = JSON.parse(editorContent.value || '{}')
    originalContent.value = editorContent.value
    emit('update:modelValue', obj)
    emit('save', obj)
    ElMessage.success('保存成功')
  } catch (error) {
    ElMessage.error('保存失败')
  }
}

// 监听外部值变化
watch(() => props.modelValue, () => {
  initContent()
}, { deep: true })

// 初始化
onMounted(() => {
  initContent()
  if (props.autoFormat && editorContent.value) {
    handleFormat()
  }
})
</script>

<style scoped>
.json-editor {
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  background: #fff;
  overflow: hidden;
}

.editor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 15px;
  background: #f5f7fa;
  border-bottom: 1px solid #dcdfe6;
}

.editor-header .title {
  font-weight: 600;
  color: #303133;
  font-size: 14px;
}

.editor-header .actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

.editor-content {
  position: relative;
}

.json-textarea {
  width: 100%;
  min-height: 300px;
  max-height: 500px;
  padding: 15px;
  border: none;
  outline: none;
  resize: vertical;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 13px;
  line-height: 1.6;
  color: #2c3e50;
  background: #fafafa;
  box-sizing: border-box;
}

.json-textarea:focus {
  background: #fff;
}

.json-textarea.has-error {
  background: #fff5f5;
  border-bottom: 2px solid #f56c6c;
}

.json-textarea[readonly] {
  background: #f5f7fa;
  cursor: not-allowed;
}

.error-message {
  padding: 10px 15px;
  background: #fef0f0;
  border-top: 1px solid #fde2e2;
  color: #f56c6c;
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 5px;
}

.editor-preview {
  border-top: 1px solid #dcdfe6;
}

.preview-header {
  padding: 8px 15px;
  background: #f5f7fa;
  border-bottom: 1px solid #ebeef5;
  font-size: 13px;
  font-weight: 600;
  color: #606266;
}

.preview-content {
  max-height: 300px;
  overflow: auto;
  padding: 15px;
  background: #fafafa;
}

.preview-content pre {
  margin: 0;
  padding: 0;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 13px;
  line-height: 1.6;
  color: #2c3e50;
}

.preview-content code {
  display: block;
  padding: 0;
  margin: 0;
  background: transparent;
  color: inherit;
}

/* 滚动条样式 */
.preview-content::-webkit-scrollbar,
.json-textarea::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

.preview-content::-webkit-scrollbar-thumb,
.json-textarea::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
}

.preview-content::-webkit-scrollbar-thumb:hover,
.json-textarea::-webkit-scrollbar-thumb:hover {
  background: #a0a0a0;
}

.preview-content::-webkit-scrollbar-track,
.json-textarea::-webkit-scrollbar-track {
  background: #f0f0f0;
}
</style>

