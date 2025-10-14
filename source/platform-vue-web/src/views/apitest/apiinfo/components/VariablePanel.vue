<template>
  <div class="variable-panel">
    <div class="variable-list">
      <div v-for="(variable, index) in variables" :key="index" class="variable-row">
        <el-input v-model="variable.key" placeholder="变量名" class="variable-key" />
        <el-input v-model="variable.value" placeholder="变量值" class="variable-value" />
        <el-input v-model="variable.description" placeholder="说明" class="variable-desc" />
        <el-button type="danger" icon="Delete" circle @click="removeVariable(index)" />
      </div>
    </div>
    <el-button type="primary" icon="Plus" @click="addVariable">添加变量</el-button>

    <div class="variable-help">
      <el-alert title="变量使用说明" type="info" :closable="false">
        <p>在请求中使用 <code>${'{'}变量名{'}'}</code> 来引用变量值</p>
        <p>例如：URL中使用 <code>http://api.example.com/${'{'} base_url {'}'}/users</code></p>
      </el-alert>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  modelValue: {
    type: Object,
    default: () => ({})
  }
})

const emit = defineEmits(['update:modelValue'])

// 变量列表
const variables = ref([])

// 初始化变量列表
const initVariables = () => {
  const obj = props.modelValue || {}
  variables.value = Object.keys(obj).map(key => ({
    key,
    value: obj[key],
    description: ''
  }))
}

// 添加变量
const addVariable = () => {
  variables.value.push({
    key: '',
    value: '',
    description: ''
  })
}

// 删除变量
const removeVariable = (index) => {
  variables.value.splice(index, 1)
  updateModelValue()
}

// 更新modelValue
const updateModelValue = () => {
  const obj = {}
  variables.value.forEach(variable => {
    if (variable.key) {
      obj[variable.key] = variable.value
    }
  })
  emit('update:modelValue', obj)
}

// 监听variables变化
watch(variables, updateModelValue, { deep: true })

// 监听modelValue变化
watch(() => props.modelValue, (newVal, oldVal) => {
  if (JSON.stringify(newVal) !== JSON.stringify(oldVal)) {
    initVariables()
  }
}, { immediate: true, deep: true })
</script>

<style scoped lang="scss">
.variable-panel {
  .variable-list {
    margin-bottom: 15px;
  }

  .variable-row {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 10px;

    .variable-key {
      width: 200px;
    }

    .variable-value {
      flex: 1;
    }

    .variable-desc {
      width: 200px;
    }
  }

  .variable-help {
    margin-top: 20px;

    code {
      background: #f5f5f5;
      padding: 2px 6px;
      border-radius: 3px;
      font-family: 'Courier New', monospace;
    }

    p {
      margin: 5px 0;
    }
  }
}
</style>

