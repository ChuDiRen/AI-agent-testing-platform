<template>
  <div class="request-params">
    <div class="param-list">
      <div v-for="(param, index) in params" :key="index" class="param-row">
        <el-checkbox v-model="param.enabled" />
        <el-input v-model="param.key" placeholder="参数名" class="param-key" />
        <el-input v-model="param.value" placeholder="参数值" class="param-value" />
        <el-input v-model="param.description" placeholder="说明" class="param-desc" />
        <el-button type="danger" icon="Delete" circle @click="removeParam(index)" />
      </div>
    </div>
    <el-button type="primary" icon="Plus" @click="addParam">添加参数</el-button>
  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue'

const props = defineProps({
  modelValue: {
    type: String,
    default: '{}'
  }
})

const emit = defineEmits(['update:modelValue'])

// 参数列表
const params = ref([])

// 初始化参数列表
const initParams = () => {
  try {
    const obj = JSON.parse(props.modelValue || '{}')
    params.value = Object.keys(obj).map(key => ({
      enabled: true,
      key,
      value: obj[key],
      description: ''
    }))
    
    if (params.value.length === 0) {
      addParam()
    }
  } catch {
    params.value = []
    addParam()
  }
}

// 添加参数
const addParam = () => {
  params.value.push({
    enabled: true,
    key: '',
    value: '',
    description: ''
  })
}

// 删除参数
const removeParam = (index) => {
  params.value.splice(index, 1)
  updateModelValue()
}

// 更新modelValue
const updateModelValue = () => {
  const obj = {}
  params.value.forEach(param => {
    if (param.enabled && param.key) {
      obj[param.key] = param.value
    }
  })
  emit('update:modelValue', JSON.stringify(obj))
}

// 监听参数变化
watch(params, updateModelValue, { deep: true })

// 监听modelValue变化
watch(() => props.modelValue, (newVal, oldVal) => {
  if (newVal !== oldVal) {
    initParams()
  }
}, { immediate: true })
</script>

<style scoped lang="scss">
.request-params {
  .param-list {
    margin-bottom: 15px;
  }

  .param-row {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 10px;

    .param-key {
      width: 200px;
    }

    .param-value {
      flex: 1;
    }

    .param-desc {
      width: 200px;
    }
  }
}
</style>

