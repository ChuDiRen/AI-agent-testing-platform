<template>
  <div class="base-form-container">
    <el-card class="form-card">
      <template #header>
        <div class="card-header">
          <span>{{ title }}</span>
          <el-button @click="handleBack">返回</el-button>
        </div>
      </template>
      
      <div class="form-content">
        <el-form
          ref="formRef"
          :model="model"
          :rules="rules"
          :label-width="labelWidth"
          v-bind="$attrs"
        >
          <slot />
          
          <el-form-item class="form-footer">
            <el-button type="primary" @click="handleSubmit" :loading="loading">保存</el-button>
            <el-button @click="handleBack">取消</el-button>
          </el-form-item>
        </el-form>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const props = defineProps({
  title: {
    type: String,
    default: '表单'
  },
  model: {
    type: Object,
    required: true
  },
  rules: {
    type: Object,
    default: () => ({})
  },
  loading: {
    type: Boolean,
    default: false
  },
  labelWidth: {
    type: String,
    default: '100px'
  }
})

const emit = defineEmits(['submit', 'cancel'])
const router = useRouter()
const formRef = ref(null)

const handleBack = () => {
  emit('cancel')
  router.back()
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate((valid, fields) => {
    if (valid) {
      emit('submit')
    }
  })
}

defineExpose({
  formRef
})
</script>

<style scoped>
.base-form-container {
  padding: 20px;
  background-color: var(--bg-secondary);
  min-height: calc(100vh - 84px);
}

.form-card {
  /* 表单卡片充分利用可用空间 */
  width: 100%;
  max-width: none;
  margin: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.form-content {
  padding: 20px;
  max-width: 800px; /* 表单内容限制宽度，保持可读性 */
}

/* 大屏幕适配 */
@media (min-width: 1400px) {
  .form-content {
    max-width: 900px;
    padding: 24px 32px;
  }
}

@media (min-width: 1920px) {
  .base-form-container {
    padding: 24px 32px;
  }
  
  .form-content {
    max-width: 1000px;
  }
}

.form-footer {
  margin-top: 40px;
  display: flex;
  justify-content: center;
}

/* 全局表单样式增强 */
/* 让常用表单组件占满父容器宽度 */
:deep(.el-select),
:deep(.el-tree-select),
:deep(.el-input-number),
:deep(.el-cascader),
:deep(.el-date-editor) {
  width: 100%;
}

/* 查看模式样式优化 */
:deep(.el-input.is-disabled .el-input__wrapper),
:deep(.el-select.is-disabled .el-input__wrapper) {
  background-color: #f5f7fa;
  cursor: not-allowed;
}

/* 只读输入框样式 */
:deep(.el-input__inner[readonly]),
:deep(.el-textarea__inner[readonly]) {
  cursor: text !important;
  user-select: text !important;
  background-color: #ffffff !important;
  color: var(--el-text-color-primary);
}

:deep(.el-input__inner[readonly]:hover),
:deep(.el-textarea__inner[readonly]:hover) {
  background-color: #fafafa !important;
}

:deep(.el-input.is-readonly:hover .el-input__wrapper),
:deep(.el-textarea.is-readonly:hover .el-textarea__inner) {
  box-shadow: 0 0 0 1px var(--el-border-color) inset;
}

:deep(.el-radio.is-disabled),
:deep(.el-select.is-disabled) {
  opacity: 0.6;
}

/* 移除卡片头部边框 */
:deep(.el-card__header) {
  border-bottom: none;
}
</style>
