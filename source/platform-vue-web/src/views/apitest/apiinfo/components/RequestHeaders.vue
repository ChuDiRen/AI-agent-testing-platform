<template>
  <div class="request-headers">
    <div class="header-list">
      <div v-for="(header, index) in headers" :key="index" class="header-row">
        <el-checkbox v-model="header.enabled" />
        <el-input v-model="header.key" placeholder="Header名称" class="header-key" />
        <el-input v-model="header.value" placeholder="Header值" class="header-value" />
        <el-input v-model="header.description" placeholder="说明" class="header-desc" />
        <el-button type="danger" icon="Delete" circle @click="removeHeader(index)" />
      </div>
    </div>
    <el-button type="primary" icon="Plus" @click="addHeader">添加Header</el-button>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  modelValue: {
    type: String,
    default: '{}'
  }
})

const emit = defineEmits(['update:modelValue'])

// Header列表
const headers = ref([])

// 初始化Header列表
const initHeaders = () => {
  try {
    const obj = JSON.parse(props.modelValue || '{}')
    headers.value = Object.keys(obj).map(key => ({
      enabled: true,
      key,
      value: obj[key],
      description: ''
    }))
    
    if (headers.value.length === 0) {
      addHeader()
    }
  } catch {
    headers.value = []
    addHeader()
  }
}

// 添加Header
const addHeader = () => {
  headers.value.push({
    enabled: true,
    key: '',
    value: '',
    description: ''
  })
}

// 删除Header
const removeHeader = (index) => {
  headers.value.splice(index, 1)
  updateModelValue()
}

// 更新modelValue
const updateModelValue = () => {
  const obj = {}
  headers.value.forEach(header => {
    if (header.enabled && header.key) {
      obj[header.key] = header.value
    }
  })
  emit('update:modelValue', JSON.stringify(obj))
}

// 监听headers变化
watch(headers, updateModelValue, { deep: true })

// 监听modelValue变化
watch(() => props.modelValue, (newVal, oldVal) => {
  if (newVal !== oldVal) {
    initHeaders()
  }
}, { immediate: true })
</script>

<style scoped lang="scss">
.request-headers {
  .header-list {
    margin-bottom: 15px;
  }

  .header-row {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 10px;

    .header-key {
      width: 200px;
    }

    .header-value {
      flex: 1;
    }

    .header-desc {
      width: 200px;
    }
  }
}
</style>

