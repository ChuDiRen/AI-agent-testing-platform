<template>
  <el-dialog 
    v-model="visible" 
    title="需要您的确认"
    width="600px"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
  >
    <div class="interrupt-content">
      <el-alert 
        type="warning" 
        :closable="false"
        show-icon
      >
        <template #title>
          <div class="alert-title">AI 助手需要您的输入</div>
        </template>
      </el-alert>

      <div v-if="interrupt" class="interrupt-message">
        <div v-if="interrupt.message" class="message-text">
          {{ interrupt.message }}
        </div>

        <div v-if="interrupt.options && interrupt.options.length > 0" class="options-container">
          <div class="options-title">请选择一个选项：</div>
          <el-radio-group v-model="selectedOption" class="options-group">
            <el-radio 
              v-for="option in interrupt.options" 
              :key="option.value"
              :value="option.value"
              border
            >
              {{ option.label }}
            </el-radio>
          </el-radio-group>
        </div>

        <div v-else class="input-container">
          <el-input
            v-model="userInput"
            type="textarea"
            :rows="3"
            placeholder="请输入您的回复..."
            @keydown.ctrl.enter="handleConfirm"
          />
          <div class="input-hint">
            <el-icon><InfoFilled /></el-icon>
            <span>按 Ctrl+Enter 快速提交</span>
          </div>
        </div>
      </div>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleCancel">取消</el-button>
        <el-button type="primary" @click="handleConfirm" :disabled="!canConfirm">
          确认
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { InfoFilled } from '@element-plus/icons-vue'

const props = defineProps({
  interrupt: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['confirm', 'cancel', 'update:interrupt'])

const visible = ref(false)
const userInput = ref('')
const selectedOption = ref(null)

// 监听 interrupt 变化，显示对话框
watch(() => props.interrupt, (newVal) => {
  if (newVal) {
    visible.value = true
    userInput.value = ''
    selectedOption.value = null
  } else {
    visible.value = false
  }
}, { immediate: true })

const canConfirm = computed(() => {
  if (props.interrupt?.options && props.interrupt.options.length > 0) {
    return selectedOption.value !== null
  }
  return userInput.value.trim().length > 0
})

const handleConfirm = () => {
  if (!canConfirm.value) {
    return
  }

  const response = props.interrupt?.options && props.interrupt.options.length > 0
    ? selectedOption.value
    : userInput.value

  emit('confirm', response)
  visible.value = false
  emit('update:interrupt', null)
}

const handleCancel = () => {
  emit('cancel')
  visible.value = false
  emit('update:interrupt', null)
}
</script>

<style scoped>
.interrupt-content {
  padding: 12px 0;
}

.alert-title {
  font-weight: 600;
  font-size: 15px;
}

.interrupt-message {
  margin-top: 20px;
}

.message-text {
  padding: 16px;
  background-color: #f5f7fa;
  border-radius: 8px;
  border-left: 4px solid #409eff;
  margin-bottom: 20px;
  line-height: 1.6;
  color: #303133;
}

.options-container {
  margin-top: 16px;
}

.options-title {
  font-weight: 600;
  margin-bottom: 12px;
  color: #606266;
}

.options-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.options-group :deep(.el-radio) {
  margin-right: 0;
  width: 100%;
}

.input-container {
  margin-top: 16px;
}

.input-hint {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 8px;
  font-size: 13px;
  color: #909399;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>

