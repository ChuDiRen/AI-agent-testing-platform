<template>
  <div class="page-container">
    <el-card class="page-card">
      <template #header>
        <h3>{{ caseId > 0 ? '编辑用例' : '新增用例' }}</h3>
      </template>

      <el-form ref="formRef" :model="caseForm" :rules="rules" label-width="120px">
        <el-form-item label="项目" prop="project_id">
          <el-select v-model="caseForm.project_id" placeholder="请选择项目" filterable>
            <el-option v-for="project in projectList" :key="project.id" :label="project.project_name" :value="project.id" />
          </el-select>
        </el-form-item>

        <el-form-item label="用例名称" prop="case_name">
          <el-input v-model="caseForm.case_name" placeholder="请输入用例名称" />
        </el-form-item>

        <el-form-item label="用例描述" prop="case_desc">
          <el-input v-model="caseForm.case_desc" type="textarea" :rows="3" placeholder="请输入用例描述" />
        </el-form-item>

        <el-divider>步骤管理</el-divider>

        <div class="steps-section">
          <el-button type="primary" @click="handleAddStep">添加步骤</el-button>

          <el-table :data="stepsList" border stripe style="margin-top: 15px">
            <el-table-column prop="run_order" label="序号" width="80" />
            <el-table-column prop="step_desc" label="步骤描述" show-overflow-tooltip />
            <el-table-column label="操作类型" width="120">
              <template #default="scope">
                {{ getOperationTypeName(scope.row.operation_type_id) }}
              </template>
            </el-table-column>
            <el-table-column label="关键字" width="120">
              <template #default="scope">
                {{ getKeywordName(scope.row.keyword_id) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="200" fixed="right">
              <template #default="scope">
                <el-button type="primary" size="small" @click="handleEditStep(scope.row, scope.$index)">编辑</el-button>
                <el-button type="danger" size="small" @click="handleDeleteStep(scope.$index)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <el-form-item label="执行器" style="margin-top: 24px">
          <el-select v-model="currentExecutorCode" placeholder="选择执行器" clearable style="width: 260px">
            <el-option
              v-for="exe in executorList"
              :key="exe.plugin_code"
              :label="exe.plugin_name"
              :value="exe.plugin_code"
            />
          </el-select>
        </el-form-item>

        <el-form-item style="margin-top: 30px">
          <el-button type="primary" @click="handleSubmit">保存用例</el-button>
          <el-button type="success" @click="handleGenerateYaml">生成YAML</el-button>
          <el-button type="info" @click="handleExecute">执行测试</el-button>
          <el-button @click="handleBack">返回</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 步骤编辑器 -->
    <StepEditor
      v-model="stepEditorVisible"
      :step-data="currentStep"
      :is-edit="isEditStep"
      :next-order="getNextOrder()"
      @confirm="handleStepConfirm"
    />
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import { queryById, insertData, updateData, generateYaml, executeCaseWithPolling } from './apiInfoCase.js'
import { queryAll as queryProjects } from '../project/apiProject.js'
import { queryAll as queryOperationType } from '../keyword/operationType.js'
import { queryAll as queryKeywords } from '../keyword/apiKeyWord.js'
import StepEditor from './components/StepEditor.vue'
import { listExecutors } from '../task/apiTask.js'

const router = useRouter()
const formRef = ref(null)

// 用例ID
const caseId = ref(0)

// 表单数据
const caseForm = reactive({
  project_id: null,
  case_name: '',
  case_desc: ''
})

// 步骤列表
const stepsList = ref([])

// 项目列表
const projectList = ref([])
const operationTypeList = ref([])
const keywordList = ref([])

// 执行器列表与当前选择
const executorList = ref([])
const currentExecutorCode = ref('')

// 步骤编辑器
const stepEditorVisible = ref(false)
const currentStep = ref(null)
const isEditStep = ref(false)
const currentStepIndex = ref(-1)

// 表单验证规则
const rules = {
  project_id: [{ required: true, message: '请选择项目', trigger: 'change' }],
  case_name: [{ required: true, message: '请输入用例名称', trigger: 'blur' }]
}

// 加载下拉数据
const loadProjects = async () => {
  const res = await queryProjects()
  if (res.data.code === 200) projectList.value = res.data.data || []
}

const loadOperationTypes = async () => {
  const res = await queryOperationType()
  if (res.data.code === 200) operationTypeList.value = res.data.data || []
}

const loadKeywords = async () => {
  const res = await queryKeywords()
  if (res.data.code === 200) keywordList.value = res.data.data || []
}

// 加载执行器列表
const loadExecutors = async () => {
  try {
    const res = await listExecutors()
    if (res.data.code === 200) {
      executorList.value = res.data.data || []
      if (!currentExecutorCode.value && executorList.value.length > 0) {
        currentExecutorCode.value = executorList.value[0].plugin_code
      }
    } else {
      ElMessage.error(res.data.msg || '加载执行器列表失败')
    }
  } catch (error) {
    console.error('加载执行器列表失败:', error)
    ElMessage.error('加载执行器列表失败，请稍后重试')
  }
}

// 获取操作类型名称
const getOperationTypeName = (id) => {
  const type = operationTypeList.value.find(t => t.id === id)
  return type ? type.operation_type_name : '-'
}

// 获取关键字名称
const getKeywordName = (id) => {
  const keyword = keywordList.value.find(k => k.id === id)
  return keyword ? keyword.name : '-'
}

// 获取下一个序号
const getNextOrder = () => {
  if (stepsList.value.length === 0) return 1
  return Math.max(...stepsList.value.map(s => s.run_order)) + 1
}

// 添加步骤
const handleAddStep = () => {
  currentStep.value = null
  isEditStep.value = false
  stepEditorVisible.value = true
}

// 编辑步骤
const handleEditStep = (step, index) => {
  currentStep.value = { ...step }
  currentStepIndex.value = index
  isEditStep.value = true
  stepEditorVisible.value = true
}

// 删除步骤
const handleDeleteStep = (index) => {
  stepsList.value.splice(index, 1)
}

// 步骤确认
const handleStepConfirm = (stepData) => {
  if (isEditStep.value) {
    // 编辑模式
    stepsList.value[currentStepIndex.value] = stepData
  } else {
    // 新增模式
    stepsList.value.push(stepData)
  }
  // 按序号排序
  stepsList.value.sort((a, b) => a.run_order - b.run_order)
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    
    const data = {
      ...caseForm,
      steps: stepsList.value.map(step => ({
        run_order: step.run_order,
        step_desc: step.step_desc,
        operation_type_id: step.operation_type_id,
        keyword_id: step.keyword_id,
        step_data: step.step_data
      }))
    }
    
    if (caseId.value > 0) {
      data.id = caseId.value
      const res = await updateData(data)
      if (res.data.code === 200) {
        ElMessage.success('更新成功')
        router.push('/ApiInfoCaseList')
      } else {
        ElMessage.error(res.data.msg || '更新失败')
      }
    } else {
      const res = await insertData(data)
      if (res.data.code === 200) {
        ElMessage.success('创建成功')
        router.push('/ApiInfoCaseList')
      } else {
        ElMessage.error(res.data.msg || '创建失败')
      }
    }
  })
}

// 生成YAML
const handleGenerateYaml = async () => {
  if (caseId.value === 0) {
    ElMessage.warning('请先保存用例')
    return
  }
  
  const res = await generateYaml({ case_id: caseId.value })
  if (res.data.code === 200) {
    ElMessage.success('YAML生成成功')
    console.log(res.data.data.yaml_content)
  } else {
    ElMessage.error(res.data.msg || '生成失败')
  }
}

// 执行测试
// 执行状态
const executing = ref(false)
const executeStatus = ref('')

const handleExecute = async () => {
  if (caseId.value === 0) {
    ElMessage.warning('请先保存用例')
    return
  }
  
  executing.value = true
  executeStatus.value = '正在提交...'
  
  try {
    const result = await executeCaseWithPolling(
      {
        case_id: caseId.value,
        test_name: `${caseForm.case_name}_${new Date().getTime()}`,
        executor_code: currentExecutorCode.value || undefined
      },
      {
        onProgress: (status, data) => {
          executeStatus.value = status === 'running' ? '正在执行...' : status
        },
        interval: 2000,
        timeout: 120000
      }
    )
    
    if (result.status === 'completed' || result.status === 'passed') {
      ElMessage.success('测试执行成功')
    } else {
      ElMessage.error(result.error_message || '测试执行失败')
    }
  } catch (error) {
    ElMessage.error(error.message || '执行失败')
  } finally {
    executing.value = false
    executeStatus.value = ''
  }
}

// 返回
const handleBack = () => {
  router.push('/ApiInfoCaseList')
}

// 加载用例数据
const loadCaseData = async (id) => {
  const res = await queryById(id)
  if (res.data.code === 200 && res.data.data) {
    const data = res.data.data
    caseForm.project_id = data.project_id
    caseForm.case_name = data.case_name
    caseForm.case_desc = data.case_desc
    
    // 加载步骤
    stepsList.value = (data.steps || []).map(step => ({
      run_order: step.run_order,
      step_desc: step.step_desc,
      operation_type_id: step.operation_type_id,
      keyword_id: step.keyword_id,
      step_data: step.step_data ? JSON.parse(step.step_data) : {}
    }))
  }
}

onMounted(async () => {
  await Promise.all([loadProjects(), loadOperationTypes(), loadKeywords(), loadExecutors()])
  
  const id = router.currentRoute.value.query.id
  if (id) {
    caseId.value = Number(id)
    await loadCaseData(caseId.value)
  }
})
</script>

<style scoped>
@import '~/styles/common-form.css';

.steps-section {
  padding: 20px;
  background: #f5f7fa;
  border-radius: 4px;
}
</style>

