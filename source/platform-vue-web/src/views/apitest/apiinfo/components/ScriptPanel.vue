<template>
  <div class="script-panel">
    <div class="script-list">
      <div v-for="(script, index) in scripts" :key="index" class="script-row">
        <el-input
          v-model="scripts[index]"
          type="textarea"
          :rows="3"
          :placeholder="placeholder"
          class="script-input"
        />
        <el-button type="danger" icon="Delete" circle @click="removeScript(index)" />
      </div>
    </div>
    <el-button type="primary" icon="Plus" @click="addScript">添加脚本</el-button>
    
    <div class="script-help">
      <el-collapse>
        <el-collapse-item title="脚本帮助" name="help">
          <p>支持的关键字：</p>
          <ul>
            <li><code>send_request</code> - 发送HTTP请求</li>
            <li><code>ex_jsonData</code> - 提取JSON数据</li>
            <li><code>assert_text_comparators</code> - 文本断言</li>
            <li><code>set_variable</code> - 设置变量</li>
          </ul>
          <p>示例：</p>
          <pre>关键字: ex_jsonData
EXVALUE: $.data.token
VARNAME: auth_token
INDEX: 0</pre>
        </el-collapse-item>
      </el-collapse>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  modelValue: {
    type: Array,
    default: () => []
  },
  placeholder: {
    type: String,
    default: '请输入脚本内容'
  }
})

const emit = defineEmits(['update:modelValue'])

// 脚本列表
const scripts = ref([...props.modelValue])

// 添加脚本
const addScript = () => {
  scripts.value.push('')
}

// 删除脚本
const removeScript = (index) => {
  scripts.value.splice(index, 1)
  updateModelValue()
}

// 更新modelValue
const updateModelValue = () => {
  emit('update:modelValue', scripts.value.filter(s => s.trim()))
}

// 监听scripts变化
watch(scripts, updateModelValue, { deep: true })

// 监听modelValue变化
watch(() => props.modelValue, (newVal) => {
  scripts.value = [...newVal]
}, { deep: true })
</script>

<style scoped lang="scss">
.script-panel {
  .script-list {
    margin-bottom: 15px;
  }

  .script-row {
    display: flex;
    gap: 10px;
    margin-bottom: 10px;

    .script-input {
      flex: 1;
    }
  }

  .script-help {
    margin-top: 20px;

    pre {
      background: #f5f5f5;
      padding: 10px;
      border-radius: 4px;
      font-size: 12px;
    }

    code {
      background: #f5f5f5;
      padding: 2px 6px;
      border-radius: 3px;
      font-family: 'Courier New', monospace;
    }

    ul {
      padding-left: 20px;
    }
  }
}
</style>

