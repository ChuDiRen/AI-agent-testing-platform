<template>
  <div class="base-search">
    <el-form
      ref="formRef"
      :model="model"
      :inline="true"
      class="search-form"
      @submit.prevent
    >
      <slot />
      <el-form-item class="search-actions">
        <el-button type="primary" icon="Search" @click="handleSearch" :loading="loading">
          查询
        </el-button>
        <el-button icon="Refresh" @click="handleReset">重置</el-button>
        <slot name="actions" />
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  model: {
    type: Object,
    required: true
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['search', 'reset'])
const formRef = ref(null)

const handleSearch = () => {
  emit('search')
}

const handleReset = () => {
  if (formRef.value) {
    formRef.value.resetFields()
  }
  emit('reset')
}

defineExpose({
  formRef
})
</script>

<style scoped>
.base-search {
  background-color: var(--bg-card);
  border-radius: 8px;
  margin-bottom: 16px;
  padding: 18px 18px 0;
  box-shadow: var(--shadow-sm);
}

.search-form {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

:deep(.el-form-item) {
  margin-bottom: 18px;
  margin-right: 0;
}

.search-actions {
  margin-left: auto;
}
</style>
