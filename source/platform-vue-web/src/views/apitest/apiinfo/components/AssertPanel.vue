<template>
  <div class="assert-panel">
    <div class="assert-list">
      <div v-for="(assertion, index) in assertions" :key="index" class="assert-row">
        <el-card class="assert-card">
          <div class="assert-header">
            <el-input v-model="assertion.description" placeholder="断言描述" style="flex: 1" />
            <el-button type="danger" icon="Delete" circle @click="removeAssertion(index)" />
          </div>
          
          <el-form :model="assertion" label-width="100px" class="assert-form">
            <el-form-item label="断言类型">
              <el-select v-model="assertion.type">
                <el-option label="文本比较" value="assert_text_comparators" />
                <el-option label="JSONPath提取" value="assert_json_path" />
                <el-option label="状态码" value="assert_status_code" />
              </el-select>
            </el-form-item>

            <!-- 文本比较 -->
            <template v-if="assertion.type === 'assert_text_comparators'">
              <el-form-item label="实际值">
                <el-input v-model="assertion.actual_value" placeholder="如: ${response.code}" />
              </el-form-item>
              <el-form-item label="比较运算符">
                <el-select v-model="assertion.operator">
                  <el-option label="等于 (==)" value="==" />
                  <el-option label="不等于 (!=)" value="!=" />
                  <el-option label="包含 (in)" value="in" />
                  <el-option label="大于 (>)" value=">" />
                  <el-option label="小于 (<)" value="<" />
                  <el-option label="大于等于 (>=)" value=">=" />
                  <el-option label="小于等于 (<=)" value="<=" />
                </el-select>
              </el-form-item>
              <el-form-item label="期望值">
                <el-input v-model="assertion.expected_value" placeholder="期望的值" />
              </el-form-item>
            </template>

            <!-- JSONPath提取 -->
            <template v-if="assertion.type === 'assert_json_path'">
              <el-form-item label="提取路径">
                <el-input v-model="assertion.extract_path" placeholder="如: $.data.code" />
              </el-form-item>
              <el-form-item label="期望值">
                <el-input v-model="assertion.expected_value" placeholder="期望的值" />
              </el-form-item>
            </template>

            <!-- 状态码 -->
            <template v-if="assertion.type === 'assert_status_code'">
              <el-form-item label="期望状态码">
                <el-input v-model="assertion.expected_value" placeholder="如: 200" />
              </el-form-item>
            </template>
          </el-form>
        </el-card>
      </div>
    </div>
    <el-button type="primary" icon="Plus" @click="addAssertion">添加断言</el-button>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  modelValue: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['update:modelValue'])

// 断言列表
const assertions = ref([...props.modelValue])

// 添加断言
const addAssertion = () => {
  assertions.value.push({
    description: '',
    type: 'assert_text_comparators',
    actual_value: '',
    operator: '==',
    expected_value: '',
    extract_path: ''
  })
}

// 删除断言
const removeAssertion = (index) => {
  assertions.value.splice(index, 1)
  updateModelValue()
}

// 更新modelValue
const updateModelValue = () => {
  emit('update:modelValue', assertions.value)
}

// 监听assertions变化
watch(assertions, updateModelValue, { deep: true })

// 监听modelValue变化
watch(() => props.modelValue, (newVal) => {
  assertions.value = [...newVal]
}, { deep: true })
</script>

<style scoped lang="scss">
.assert-panel {
  .assert-list {
    margin-bottom: 15px;
  }

  .assert-row {
    margin-bottom: 15px;
  }

  .assert-card {
    .assert-header {
      display: flex;
      gap: 10px;
      margin-bottom: 15px;
    }

    .assert-form {
      margin-top: 10px;
    }
  }
}
</style>

