<template>
  <div class="page-container">
    <!-- 顶部固定操作栏 -->
    <div class="top-header">
      <div class="header-left">
        <el-button link @click="handleBack">
          <el-icon :size="20"><Back /></el-icon>
        </el-button>
        <div class="title-info">
          <h3 class="title">{{ caseId > 0 ? '编辑用例' : '新增用例' }}</h3>
          <span class="subtitle">{{ caseForm.case_name || '未命名用例' }}</span>
        </div>
      </div>
      <div class="header-right">
        <el-select 
          v-model="currentExecutorCode" 
          placeholder="选择执行器" 
          style="width: 180px"
          size="default"
        >
          <template #prefix><el-icon><VideoPlay /></el-icon></template>
          <el-option
            v-for="exe in executorList"
            :key="exe.plugin_code"
            :label="exe.plugin_name"
            :value="exe.plugin_code"
          />
        </el-select>
        <el-button type="primary" @click="handleSubmit">保存用例</el-button>
        <el-button type="success" @click="handleExecute" :loading="executing">
          <el-icon class="el-icon--left"><VideoPlay /></el-icon>
          {{ executing ? executeStatus : '调试运行' }}
        </el-button>
      </div>
    </div>

    <div class="content-wrapper">
      <el-form ref="formRef" :model="caseForm" :rules="rules" label-width="80px" label-position="left">
        <!-- 基础信息卡片 -->
        <el-card class="info-card" shadow="hover">
          <div class="card-title">基础信息</div>
          <el-row :gutter="40">
            <el-col :span="8">
              <el-form-item label="所属项目" prop="project_id">
                <el-select v-model="caseForm.project_id" placeholder="请选择项目" filterable style="width: 100%">
                  <el-option v-for="project in projectList" :key="project.id" :label="project.project_name" :value="project.id" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="16">
              <el-form-item label="用例名称" prop="case_name">
                <el-input v-model="caseForm.case_name" placeholder="请输入用例名称" />
              </el-form-item>
            </el-col>
          </el-row>
          <el-row>
            <el-col :span="24">
              <el-form-item label="用例描述" prop="case_desc" class="mb-0">
                <el-input 
                  v-model="caseForm.case_desc" 
                  type="textarea" 
                  :rows="1" 
                  placeholder="请输入用例描述"
                  resize="none"
                />
              </el-form-item>
            </el-col>
          </el-row>
        </el-card>

        <!-- 步骤管理卡片 -->
        <el-card class="step-card" shadow="hover">
          <div class="card-header-row">
            <div class="card-title">用例步骤</div>
            <el-button type="primary" plain size="small" icon="Plus" @click="handleAddStep">添加步骤</el-button>
          </div>
          
          <div class="step-list">
            <el-table 
              :data="stepsList" 
              border 
              stripe 
              header-cell-class-name="table-header"
              class="custom-table"
            >
              <el-table-column prop="run_order" label="序号" width="70" align="center" />
              <el-table-column prop="step_desc" label="步骤描述" min-width="250" show-overflow-tooltip>
                <template #default="{ row }">
                  <span class="step-desc-text">{{ row.step_desc }}</span>
                </template>
              </el-table-column>
              <el-table-column label="操作类型" width="140">
                <template #default="{ row }">
                  <el-tag size="small" effect="light" class="op-type-tag">{{ getOperationTypeName(row.operation_type_id) }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column label="关键字" width="180">
                <template #default="{ row }">
                  <span class="keyword-text">{{ getKeywordName(row.keyword_id) }}</span>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="140" align="center" fixed="right">
                <template #default="{ row, $index }">
                  <el-button type="primary" link @click="handleEditStep(row, $index)">编辑</el-button>
                  <el-button type="danger" link @click="handleDeleteStep($index)">删除</el-button>
                </template>
              </el-table-column>
            </el-table>
            
            <div v-if="stepsList.length === 0" class="empty-state">
              <el-empty description="暂无测试步骤" :image-size="80">
                <el-button type="primary" plain @click="handleAddStep">立即添加</el-button>
              </el-empty>
            </div>
          </div>
        </el-card>
      </el-form>
    </div>

    <!-- 步骤编辑器 -->
    <StepEditor
      v-model="stepEditorVisible"
      :step-data="currentStep"
      :is-edit="isEditStep"
      :next-order="getNextOrder()"
      @confirm="handleStepConfirm"
    />

    <!-- 执行结果弹窗 -->
    <ExecutionResultDialog
      v-model="resultDialogVisible"
      :result-data="executionResult"
    />
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import { queryById, insertData, updateData, executeCase, getExecutionStatus } from './apiInfoCase.js'
import { queryAll as queryProjects } from '../project/apiProject.js'
import { queryAll as queryOperationType } from '../keyword/operationType.js'
import { queryAll as queryKeywords } from '../keyword/apiKeyWord.js'
import StepEditor from './components/StepEditor.vue'
import ExecutionResultDialog from './components/ExecutionResultDialog.vue'
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

// 执行测试
// 执行状态
const executing = ref(false)
const executeStatus = ref('')

// 执行结果弹窗
const resultDialogVisible = ref(false)
const executionResult = ref({})

// 执行用例（调用后端统一接口，后端负责 YAML 构建）
const handleExecute = async () => {
  if (caseId.value === 0) {
    ElMessage.warning('请先保存用例')
    return
  }
  
  if (stepsList.value.length === 0) {
    ElMessage.warning('请先添加测试步骤')
    return
  }
  
  if (!currentExecutorCode.value) {
    ElMessage.warning('请选择执行器')
    return
  }
  
  executing.value = true
  executeStatus.value = '正在提交...'
  
  try {
    // 调用后端统一执行接口，只传 case_id，后端负责构建 YAML
    const res = await executeCase({
      case_id: caseId.value,
      executor_code: currentExecutorCode.value,
      test_name: caseForm.case_name
    })
    
    if (res.data.code === 200) {
      const result = res.data.data || {}
      ElMessage.success('用例已提交执行')
      
      // 跳转到测试历史页面查看执行结果
      setTimeout(() => {
        router.push('/ApiHistoryList')
      }, 1000)
    } else {
      ElMessage.error(res.data.msg || '执行失败')
    }
  } catch (error) {
    console.error('执行失败:', error)
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
      step_data: step.step_data || {}
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
.page-container {
  min-height: 100vh;
  background-color: #f5f7fa;
}

/* 顶部固定操作栏 */
.top-header {
  position: sticky;
  top: 0;
  z-index: 100;
  background: #fff;
  height: 60px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 24px;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.title-info {
  display: flex;
  flex-direction: column;
}

.title-info .title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  line-height: 1.2;
}

.title-info .subtitle {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

/* 内容区域 */
.content-wrapper {
  margin: 24px;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* 大屏幕适配 */
@media (min-width: 1920px) {
  .content-wrapper {
    margin: 32px 48px;
    gap: 28px;
  }
}

@media (min-width: 2560px) {
  .content-wrapper {
    margin: 40px 64px;
    gap: 32px;
  }
}

/* 卡片通用样式 */
.info-card, .step-card {
  border: none;
  border-radius: 4px;
}

.card-title {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 20px;
  padding-left: 10px;
  border-left: 3px solid #409eff;
  line-height: 1;
}

.card-header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.card-header-row .card-title {
  margin-bottom: 0;
}

/* 表单微调 */
:deep(.el-form-item__label) {
  font-weight: 500;
  color: #606266;
}

.mb-0 {
  margin-bottom: 0 !important;
}

/* 表格样式优化 */
.custom-table {
  border-radius: 4px;
  overflow: hidden;
}

:deep(.table-header) {
  background-color: #f5f7fa !important;
  color: #606266;
  font-weight: 600;
  height: 44px;
}

.step-desc-text {
  color: #303133;
  font-family: 'Menlo', 'Monaco', monospace;
  font-size: 13px;
}

.op-type-tag {
  font-weight: 500;
}

.keyword-text {
  color: #409eff;
  font-family: monospace;
  background: #ecf5ff;
  padding: 2px 6px;
  border-radius: 2px;
  font-size: 12px;
}

.empty-state {
  padding: 40px 0;
  background: #fff;
  border: 1px solid #ebeef5;
  border-top: none;
}
</style>

