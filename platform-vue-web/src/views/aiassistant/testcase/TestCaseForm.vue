<template>
  <el-dialog
    :title="dialogTitle"
    v-model="visible"
    width="900px"
    :close-on-click-modal="false"
    @close="handleClose"
  >
    <el-form :model="form" :rules="rules" ref="formRef" label-width="120px">
      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="用例名称" prop="case_name">
            <el-input v-model="form.case_name" placeholder="请输入用例名称" :disabled="viewMode" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="所属项目" prop="project_id">
            <el-select v-model="form.project_id" placeholder="请选择项目" :disabled="viewMode" style="width: 100%">
              <el-option v-for="p in projects" :key="p.id" :label="p.project_name" :value="p.id" />
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>
      <el-row :gutter="20">
        <el-col :span="8">
          <el-form-item label="测试类型" prop="test_type">
            <el-select v-model="form.test_type" placeholder="请选择" :disabled="viewMode" style="width: 100%">
              <el-option label="API" value="API" />
              <el-option label="Web" value="Web" />
              <el-option label="App" value="App" />
              <el-option label="通用" value="通用" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="优先级" prop="priority">
            <el-select v-model="form.priority" placeholder="请选择" :disabled="viewMode" style="width: 100%">
              <el-option label="P0" value="P0" />
              <el-option label="P1" value="P1" />
              <el-option label="P2" value="P2" />
              <el-option label="P3" value="P3" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="模块名称">
            <el-input v-model="form.module_name" placeholder="请输入模块名称" :disabled="viewMode" />
          </el-form-item>
        </el-col>
      </el-row>
      <el-form-item label="前置条件">
        <el-input v-model="form.precondition" type="textarea" :rows="2" placeholder="请输入前置条件" :disabled="viewMode" />
      </el-form-item>
      <el-form-item label="测试步骤" prop="test_steps">
        <JsonEditor 
          v-model="testStepsJson" 
          title="测试步骤（JSON数组格式）" 
          :readonly="viewMode"
          :show-preview="false"
          @save="handleStepsSave"
        />
      </el-form-item>
      <el-form-item label="预期结果" prop="expected_result">
        <el-input v-model="form.expected_result" type="textarea" :rows="3" placeholder="请输入预期结果" :disabled="viewMode" />
      </el-form-item>
      <el-form-item label="测试数据">
        <JsonEditor 
          v-model="testDataJson" 
          title="测试数据（JSON格式）" 
          :readonly="viewMode"
          :show-preview="false"
          @save="handleDataSave"
        />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="handleClose">{{ viewMode ? '关闭' : '取消' }}</el-button>
      <el-button v-if="!viewMode" type="primary" @click="handleSubmit" :loading="submitLoading">确定</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, watch, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { insertData, updateData } from './testcase'
import JsonEditor from '~/components/JsonEditor.vue'

// Props
const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  formData: {
    type: Object,
    default: () => ({})
  },
  viewMode: {
    type: Boolean,
    default: false
  },
  projects: {
    type: Array,
    default: () => []
  }
})

// Emits
const emit = defineEmits(['update:modelValue', 'success'])

// 对话框显示状态
const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

// 表单引用
const formRef = ref(null)
const submitLoading = ref(false)

// 是否为编辑模式
const isEdit = computed(() => !!props.formData.id)

// 对话框标题
const dialogTitle = computed(() => {
  if (props.viewMode) return '查看用例'
  return isEdit.value ? '编辑用例' : '新增用例'
})

// 表单数据
const form = reactive({
  id: null,
  case_name: '',
  project_id: null,
  test_type: 'API',
  priority: 'P1',
  module_name: '',
  precondition: '',
  test_steps: [],
  expected_result: '',
  test_data: {}
})

// JSON编辑器数据
const testStepsJson = ref('[]')
const testDataJson = ref('{}')

// 表单验证规则
const rules = {
  case_name: [{ required: true, message: '请输入用例名称', trigger: 'blur' }],
  project_id: [{ required: true, message: '请选择所属项目', trigger: 'change' }],
  test_type: [{ required: true, message: '请选择测试类型', trigger: 'change' }],
  priority: [{ required: true, message: '请选择优先级', trigger: 'change' }],
  expected_result: [{ required: true, message: '请输入预期结果', trigger: 'blur' }]
}

// 重置表单
const resetForm = () => {
  Object.assign(form, {
    id: null,
    case_name: '',
    project_id: null,
    test_type: 'API',
    priority: 'P1',
    module_name: '',
    precondition: '',
    test_steps: [],
    expected_result: '',
    test_data: {}
  })
  testStepsJson.value = '[]'
  testDataJson.value = '{}'
  formRef.value?.clearValidate()
}

// 监听formData变化，更新表单数据
watch(() => props.formData, (newData) => {
  if (newData && Object.keys(newData).length > 0) {
    Object.assign(form, newData)
    // 更新JSON编辑器内容
    testStepsJson.value = JSON.stringify(newData.test_steps || [], null, 2)
    testDataJson.value = JSON.stringify(newData.test_data || {}, null, 2)
  } else {
    resetForm()
  }
}, { immediate: true, deep: true })

// 处理测试步骤保存
const handleStepsSave = (jsonStr) => {
  try {
    form.test_steps = JSON.parse(jsonStr)
  } catch (error) {
    ElMessage.warning('测试步骤JSON格式有误')
  }
}

// 处理测试数据保存
const handleDataSave = (jsonStr) => {
  try {
    form.test_data = JSON.parse(jsonStr)
  } catch (error) {
    ElMessage.warning('测试数据JSON格式有误')
  }
}

// 提交表单
const handleSubmit = async () => {
  if (props.viewMode) {
    handleClose()
    return
  }
  
  try {
    await formRef.value.validate()
    
    // 验证JSON数据
    try {
      form.test_steps = JSON.parse(testStepsJson.value)
    } catch (error) {
      ElMessage.error('测试步骤JSON格式有误')
      return
    }
    
    try {
      form.test_data = JSON.parse(testDataJson.value)
    } catch (error) {
      ElMessage.error('测试数据JSON格式有误')
      return
    }
    
    submitLoading.value = true
    
    const data = { ...form }
    if (isEdit.value) {
      delete data.create_time
      delete data.modify_time
    } else {
      delete data.id
    }
    
    const res = isEdit.value 
      ? await updateData(data) 
      : await insertData(data)
      
    if (res.data.code === 200) {
      ElMessage.success(res.data.msg || res.data.message || (isEdit.value ? '更新成功' : '新增成功'))
      emit('success')
      handleClose()
    } else {
      ElMessage.error(res.data.msg || res.data.message || '操作失败')
    }
  } catch (error) {
    console.error('提交失败:', error)
    if (error !== false) {
      ElMessage.error('操作失败')
    }
  } finally {
    submitLoading.value = false
  }
}

// 关闭对话框
const handleClose = () => {
  resetForm()
  visible.value = false
}
</script>

<style scoped>
:deep(.el-form-item__label) {
  font-weight: 500;
}
</style>

