<template>
  <div class="test-execution-view">
    <el-card class="page-card">
      <template #header>
        <div class="card-header">
          <h3>测试执行监控</h3>
          <div class="actions">
            <el-button type="primary" @click="startNewTest" :disabled="isExecuting">
              <el-icon><VideoPlay /></el-icon>
              开始测试
            </el-button>
            <el-button @click="stopTest" :disabled="!isExecuting">
              <el-icon><VideoPause /></el-icon>
              停止测试
            </el-button>
          </div>
        </div>
      </template>

      <!-- 测试配置 -->
      <el-form v-if="!executionId" class="test-config" label-width="100px">
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="执行器">
              <el-select v-model="currentExecutorCode" placeholder="请选择执行器" style="width: 100%">
                <el-option
                  v-for="executor in executorList"
                  :key="executor.plugin_code"
                  :label="executor.plugin_name"
                  :value="executor.plugin_code"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="测试类型">
              <el-select v-model="testConfig.type" placeholder="请选择" style="width: 100%">
                <el-option label="单个用例" value="case" />
                <el-option label="测试集合" value="collection" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="测试ID">
              <el-input v-model="testConfig.id" placeholder="请输入测试ID" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <!-- 动态执行器参数配置 -->
        <el-divider v-if="currentExecutorSchema" content-position="left">执行器参数</el-divider>
        <ExecutorConfigForm
          v-if="currentExecutorSchema"
          :config-schema="currentExecutorSchema"
          v-model="executorConfig"
        />
      </el-form>

      <!-- 执行进度组件 -->
      <TestExecutionProgress
        v-if="executionId"
        ref="progressRef"
        :execution-id="executionId"
        :show-logs="showProgressLogs"
        @status-change="handleStatusChange"
        @completed="handleCompleted"
        @error="handleError"
      />

      <!-- 提示信息 -->
      <el-empty
        v-if="!executionId"
        description="请配置测试参数并点击开始测试按钮"
      />
    </el-card>

    <!-- 实时日志（独立面板） -->
    <el-card v-if="executionId && showSeparateLog" class="log-card">
      <RealtimeLog
        ref="logRef"
        :execution-id="executionId"
        title="详细执行日志"
        :max-lines="2000"
      />
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { VideoPlay, VideoPause } from '@element-plus/icons-vue'
import TestExecutionProgress from '@/components/TestExecutionProgress.vue'
import RealtimeLog from '@/components/RealtimeLog.vue'
import ExecutorConfigForm from '@/components/ExecutorConfigForm.vue'
import { executeCase } from '@/views/apitest/apiinfocase/apiInfoCase.js'
import { executePlan } from '@/views/apitest/testplan/testPlan.js'
import { listExecutors } from '@/views/apitest/task/apiTask.js'

// 状态
const executionId = ref('')
const isExecuting = ref(false)
const showProgressLogs = ref(true)
const showSeparateLog = ref(false)

// 组件引用
const progressRef = ref(null)
const logRef = ref(null)

// 测试配置
const testConfig = ref({
  type: 'case',
  id: ''
})

// 执行器列表
const executorList = ref([])
const currentExecutorCode = ref('')
const executorConfig = ref({})

// 当前执行器的配置 schema
const currentExecutorSchema = computed(() => {
  const executor = executorList.value.find(e => e.plugin_code === currentExecutorCode.value)
  if (!executor) return null
  // config_schema 可能是字符串或对象
  if (typeof executor.config_schema === 'string') {
    try {
      return JSON.parse(executor.config_schema)
    } catch {
      return null
    }
  }
  return executor.config_schema
})

// 当执行器变化时，重置配置
watch(currentExecutorCode, () => {
  executorConfig.value = {}
})

// 加载执行器
const loadExecutors = async () => {
  try {
    const res = await listExecutors()
    if (res.data.code === 200) {
      executorList.value = res.data.data || []
      if (executorList.value.length > 0) {
        currentExecutorCode.value = executorList.value[0].plugin_code
      }
    }
  } catch (error) {
    console.error('加载执行器失败:', error)
  }
}

// 初始化
loadExecutors()

// 开始测试（调用后端统一接口，后端负责 YAML 构建）
const startNewTest = async () => {
  if (!testConfig.value.id) {
    ElMessage.warning('请输入测试ID')
    return
  }

  if (!currentExecutorCode.value) {
    ElMessage.warning('没有可用的执行器')
    return
  }

  try {
    let response
    
    // 根据类型调用不同的后端统一接口
    if (testConfig.value.type === 'case') {
      // 调用后端统一执行接口，只传 case_id
      response = await executeCase({
        case_id: Number(testConfig.value.id),
        executor_code: currentExecutorCode.value,
        test_name: `用例执行-${Date.now()}`
      })
    } else if (testConfig.value.type === 'collection') {
      response = await executePlan({
        plan_id: Number(testConfig.value.id),
        executor_code: currentExecutorCode.value,
        test_name: `集合执行-${Date.now()}`
      })
    }

    if (response.data.code === 200) {
      // 获取执行ID
      const result = response.data.data || {}
      executionId.value = result.test_id || result.task_id || result.execution_uuid || result.execution_id
      isExecuting.value = true
      
      ElMessage.success('测试已启动')
    } else {
      ElMessage.error(response.data.msg || '启动测试失败')
    }
  } catch (error) {
    console.error('启动测试失败:', error)
    ElMessage.error('启动测试失败，请稍后重试')
  }
}

// 停止测试
const stopTest = () => {
  ElMessageBox.confirm('确定要停止当前测试吗？', '提示', {
    type: 'warning'
  }).then(() => {
    if (progressRef.value) {
      progressRef.value.disconnect()
    }
    if (logRef.value) {
      logRef.value.disconnect()
    }
    
    isExecuting.value = false
    ElMessage.info('已停止监控')
  }).catch(() => {
    // 取消
  })
}

// 状态变化
const handleStatusChange = (status) => {
  console.log('状态变化:', status)
  
  if (status.status === 'running') {
    isExecuting.value = true
  }
}

// 执行完成
const handleCompleted = (result) => {
  console.log('执行完成:', result)
  isExecuting.value = false
  
  const success = result.passed === result.total
  const message = `测试执行完成！\n总计: ${result.total}\n成功: ${result.passed}\n失败: ${result.failed}`
  
  if (success) {
    ElMessage.success(message)
  } else {
    ElMessage.warning(message)
  }
}

// 错误处理
const handleError = (error) => {
  console.error('执行错误:', error)
  ElMessage.error(error.message || '执行过程中发生错误')
}
</script>

<style scoped>
.test-execution-view {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.page-card {
  border-radius: 8px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.card-header .actions {
  display: flex;
  gap: 12px;
}

.test-config {
  margin-bottom: 20px;
  padding: 16px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.log-card {
  border-radius: 8px;
  min-height: 400px;
}
</style>
