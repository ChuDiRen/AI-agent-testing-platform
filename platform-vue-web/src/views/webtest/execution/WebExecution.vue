<template>
  <div class="page-container p-4">
    <el-row :gutter="16">
      <!-- 执行配置 -->
      <el-col :span="executing || lastResult ? 16 : 24">
        <el-card shadow="never" class="config-card">
          <template #header>
            <div class="card-header">
              <span class="card-title">Web 测试执行配置</span>
              <el-tag type="info" size="small">Playwright 引擎</el-tag>
            </div>
          </template>
          
          <el-form :model="form" :rules="formRules" ref="formRef" label-width="120px">
            <el-row :gutter="20">
              <el-col :span="executing || lastResult ? 12 : 8">
                <el-form-item label="测试项目" prop="project_id">
                  <el-select 
                    v-model="form.project_id" 
                    placeholder="选择项目" 
                    class="w-full"
                    @change="handleProjectChange"
                  >
                    <el-option v-for="p in projects" :key="p.id" :label="p.project_name" :value="p.id" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="executing || lastResult ? 12 : 8">
                <el-form-item label="执行环境" prop="env">
                  <el-radio-group v-model="form.env">
                    <el-radio-button value="dev">开发环境</el-radio-button>
                    <el-radio-button value="test">测试环境</el-radio-button>
                    <el-radio-button value="prod">线上环境</el-radio-button>
                  </el-radio-group>
                </el-form-item>
              </el-col>
              <el-col :span="8" v-if="!executing && !lastResult">
                <el-form-item label="浏览器引擎">
                  <el-checkbox-group v-model="form.browsers">
                    <el-checkbox value="chromium">Chromium</el-checkbox>
                    <el-checkbox value="firefox">Firefox</el-checkbox>
                    <el-checkbox value="webkit">WebKit</el-checkbox>
                  </el-checkbox-group>
                </el-form-item>
              </el-col>
            </el-row>

            <el-form-item label="选择用例" prop="case_ids">
              <div class="case-selector">
                <div class="case-selector-header">
                  <el-input 
                    v-model="caseSearchText" 
                    placeholder="搜索用例" 
                    clearable 
                    style="width: 200px"
                  />
                  <el-button type="primary" link @click="selectAllCases">全选</el-button>
                  <el-button type="primary" link @click="clearAllCases">清空</el-button>
                </div>
                <el-checkbox-group v-model="form.case_ids" class="case-list">
                  <el-checkbox 
                    v-for="c in filteredCases" 
                    :key="c.id" 
                    :value="c.id"
                    class="case-item"
                  >
                    <span class="case-name">{{ c.name }}</span>
                    <el-tag size="small" type="info">{{ c.step_count || 0 }} 步骤</el-tag>
                  </el-checkbox>
                </el-checkbox-group>
                <div class="case-selector-footer">
                  已选择 <strong>{{ form.case_ids.length }}</strong> 个用例
                </div>
              </div>
            </el-form-item>

            <el-divider content-position="left">浏览器配置</el-divider>

            <el-row :gutter="20">
              <el-col :span="executing || lastResult ? 12 : 6" v-if="executing || lastResult">
                <el-form-item label="浏览器引擎">
                  <el-checkbox-group v-model="form.browsers">
                    <el-checkbox value="chromium">Chromium</el-checkbox>
                    <el-checkbox value="firefox">Firefox</el-checkbox>
                    <el-checkbox value="webkit">WebKit</el-checkbox>
                  </el-checkbox-group>
                </el-form-item>
              </el-col>
              <el-col :span="executing || lastResult ? 12 : 6">
                <el-form-item label="无头模式">
                  <el-switch v-model="form.headless" active-text="是" inactive-text="否" />
                  <span class="form-tip">无头模式下不显示浏览器窗口</span>
                </el-form-item>
              </el-col>
              <el-col :span="6" v-if="!executing && !lastResult">
                <el-form-item label="并发线程数">
                  <el-input-number v-model="form.threads" :min="1" :max="10" />
                </el-form-item>
              </el-col>
              <el-col :span="6" v-if="!executing && !lastResult">
                <el-form-item label="超时时间(秒)">
                  <el-input-number v-model="form.timeout" :min="10" :max="300" :step="10" />
                </el-form-item>
              </el-col>
              <el-col :span="6" v-if="!executing && !lastResult">
                <el-form-item label="失败重试">
                  <el-input-number v-model="form.retry" :min="0" :max="3" />
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="20" v-if="executing || lastResult">
              <el-col :span="8">
                <el-form-item label="并发线程数">
                  <el-input-number v-model="form.threads" :min="1" :max="10" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="超时时间(秒)">
                  <el-input-number v-model="form.timeout" :min="10" :max="300" :step="10" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="失败重试">
                  <el-input-number v-model="form.retry" :min="0" :max="3" />
                </el-form-item>
              </el-col>
            </el-row>

            <el-divider content-position="left">高级选项</el-divider>

            <el-row :gutter="20">
              <el-col :span="executing || lastResult ? 12 : 6">
                <el-form-item label="截图策略">
                  <el-select v-model="form.screenshot" class="w-full">
                    <el-option label="仅失败时截图" value="on_failure" />
                    <el-option label="每步都截图" value="always" />
                    <el-option label="不截图" value="never" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="executing || lastResult ? 12 : 6">
                <el-form-item label="录制视频">
                  <el-switch v-model="form.video" active-text="是" inactive-text="否" />
                </el-form-item>
              </el-col>
              <el-col :span="12" v-if="!executing && !lastResult">
                <el-form-item label="执行通知">
                  <el-checkbox-group v-model="form.notify">
                    <el-checkbox value="email">邮件通知</el-checkbox>
                    <el-checkbox value="wechat">企业微信</el-checkbox>
                    <el-checkbox value="dingtalk">钉钉</el-checkbox>
                  </el-checkbox-group>
                </el-form-item>
              </el-col>
            </el-row>

            <el-form-item label="执行通知" v-if="executing || lastResult">
              <el-checkbox-group v-model="form.notify">
                <el-checkbox value="email">邮件通知</el-checkbox>
                <el-checkbox value="wechat">企业微信</el-checkbox>
                <el-checkbox value="dingtalk">钉钉</el-checkbox>
              </el-checkbox-group>
            </el-form-item>

            <el-form-item>
              <el-button type="primary" size="large" :loading="executing" @click="handleRun">
                <el-icon class="mr-1"><VideoPlay /></el-icon>
                立即执行
              </el-button>
              <el-button size="large" @click="handleSaveConfig">
                <el-icon class="mr-1"><Document /></el-icon>
                保存配置
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>

      <!-- 执行状态（仅在执行时或有结果时显示） -->
      <el-col :span="8" v-if="executing || lastResult">
        <el-card shadow="never" class="status-card">
          <template #header>
            <span class="card-title">执行状态</span>
          </template>
          
          <div v-if="executing" class="executing-status">
            <el-progress type="circle" :percentage="progress" :status="progressStatus" :width="120" />
            <p class="status-text">{{ statusText }}</p>
            <div class="running-info">
              <div class="info-item">
                <span class="label">已执行:</span>
                <span class="value">{{ runningStats.executed }} / {{ runningStats.total }}</span>
              </div>
              <div class="info-item">
                <span class="label">通过:</span>
                <span class="value success">{{ runningStats.passed }}</span>
              </div>
              <div class="info-item">
                <span class="label">失败:</span>
                <span class="value danger">{{ runningStats.failed }}</span>
              </div>
            </div>
            <el-button type="danger" @click="handleStop" :loading="stopping">停止执行</el-button>
          </div>

          <div v-else-if="lastResult" class="result-status">
            <el-result
              :icon="lastResult.status === 'success' ? 'success' : 'error'"
              :title="lastResult.status === 'success' ? '执行成功' : '执行失败'"
            >
              <template #sub-title>
                <div class="result-stats">
                  <div class="stat-item">
                    <span class="stat-label">总用例</span>
                    <span class="stat-value">{{ lastResult.total }}</span>
                  </div>
                  <div class="stat-item success">
                    <span class="stat-label">通过</span>
                    <span class="stat-value">{{ lastResult.pass }}</span>
                  </div>
                  <div class="stat-item danger">
                    <span class="stat-label">失败</span>
                    <span class="stat-value">{{ lastResult.fail }}</span>
                  </div>
                  <div class="stat-item">
                    <span class="stat-label">通过率</span>
                    <span class="stat-value">{{ lastResult.pass_rate }}%</span>
                  </div>
                </div>
              </template>
              <template #extra>
                <el-button type="primary" @click="viewReport(lastResult.id)">
                  <el-icon><DataAnalysis /></el-icon>
                  查看报告
                </el-button>
                <el-button @click="viewHistory">
                  <el-icon><Clock /></el-icon>
                  执行历史
                </el-button>
              </template>
            </el-result>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { VideoPlay, Document, DataAnalysis, Clock } from '@element-plus/icons-vue'
import { executeWebTest, stopWebTest, getWebProjects, getWebCasesByProject } from './webExecution'

const route = useRoute()
const router = useRouter()

const formRef = ref(null)
const executing = ref(false)
const stopping = ref(false)
const progress = ref(0)
const progressStatus = ref('')
const statusText = ref('准备执行...')

const runningStats = reactive({
  total: 0,
  executed: 0,
  passed: 0,
  failed: 0
})

const lastResult = ref(null)

// 项目列表
const projects = ref([])

// 用例列表
const caseList = ref([])
const caseSearchText = ref('')

const filteredCases = computed(() => {
  if (!caseSearchText.value) return caseList.value
  return caseList.value.filter(c => 
    c.name.toLowerCase().includes(caseSearchText.value.toLowerCase())
  )
})

// 表单数据
const form = reactive({
  project_id: route.query.project_id ? Number(route.query.project_id) : null,
  case_ids: route.query.case_id ? [Number(route.query.case_id)] : [],
  env: 'test',
  browsers: ['chromium'],
  headless: true,
  threads: 1,
  timeout: 60,
  retry: 1,
  screenshot: 'on_failure',
  video: false,
  notify: []
})

const formRules = {
  project_id: [{ required: true, message: '请选择项目', trigger: 'change' }],
  case_ids: [{ required: true, message: '请选择用例', trigger: 'change', type: 'array', min: 1 }]
}

// 加载项目列表
const loadProjects = async () => {
  try {
    const res = await getWebProjects()
    if (res?.data?.code === 200) {
      projects.value = res.data.data || []
    } else {
      mockProjects()
    }
  } catch (e) {
    mockProjects()
  }
}

const mockProjects = () => {
  projects.value = [
    { id: 1, project_name: '商城系统 Web 测试' },
    { id: 2, project_name: '用户中心 UI 校验' },
    { id: 3, project_name: '后台管理系统自动化' }
  ]
}

// 项目变化时加载用例
const handleProjectChange = async (projectId) => {
  form.case_ids = []
  if (!projectId) {
    caseList.value = []
    return
  }
  try {
    const res = await getWebCasesByProject(projectId)
    if (res?.data?.code === 200) {
      caseList.value = res.data.data || []
    } else {
      mockCases()
    }
  } catch (e) {
    mockCases()
  }
}

const mockCases = () => {
  caseList.value = [
    { id: 1, name: '登录页面测试.yaml', step_count: 5 },
    { id: 2, name: '首页基础跳转.yaml', step_count: 3 },
    { id: 3, name: '下单流程.yaml', step_count: 12 },
    { id: 4, name: '支付流程.yaml', step_count: 8 },
    { id: 5, name: '用户中心.yaml', step_count: 6 }
  ]
}

// 全选/清空用例
const selectAllCases = () => {
  form.case_ids = filteredCases.value.map(c => c.id)
}

const clearAllCases = () => {
  form.case_ids = []
}

// 执行测试
const handleRun = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    
    executing.value = true
    progress.value = 0
    progressStatus.value = ''
    statusText.value = '正在初始化...'
    
    runningStats.total = form.case_ids.length
    runningStats.executed = 0
    runningStats.passed = 0
    runningStats.failed = 0
    
    // 模拟执行进度
    const timer = setInterval(() => {
      if (progress.value < 100) {
        progress.value += Math.random() * 8
        if (progress.value > 100) progress.value = 100
        
        runningStats.executed = Math.floor((progress.value / 100) * runningStats.total)
        runningStats.passed = Math.floor(runningStats.executed * 0.9)
        runningStats.failed = runningStats.executed - runningStats.passed
        
        if (progress.value < 30) {
          statusText.value = '正在启动浏览器...'
        } else if (progress.value < 60) {
          statusText.value = '正在执行测试用例...'
        } else if (progress.value < 90) {
          statusText.value = '正在生成报告...'
        } else {
          statusText.value = '即将完成...'
        }
      } else {
        clearInterval(timer)
        executing.value = false
        
        const passRate = ((runningStats.passed / runningStats.total) * 100).toFixed(1)
        lastResult.value = {
          id: 'rec_' + Date.now(),
          status: runningStats.failed === 0 ? 'success' : 'error',
          total: runningStats.total,
          pass: runningStats.passed,
          fail: runningStats.failed,
          pass_rate: passRate
        }
        ElMessage.success('执行完成')
      }
    }, 300)

    try {
      await executeWebTest(form)
    } catch (e) {
      // Mock 模式继续执行
    }
  })
}

// 停止执行
const handleStop = async () => {
  stopping.value = true
  try {
    await stopWebTest()
    ElMessage.warning('已停止执行')
  } catch (e) {
    ElMessage.warning('已停止执行 (Mock)')
  } finally {
    stopping.value = false
    executing.value = false
  }
}

// 保存配置
const handleSaveConfig = () => {
  ElMessage.success('配置已保存')
}

// 查看报告
const viewReport = (id) => {
  router.push({ path: '/WebReportViewer', query: { id: id || 'latest' } })
}

// 查看历史
const viewHistory = () => {
  router.push({ path: '/WebHistoryList', query: { project_id: form.project_id } })
}

onMounted(() => {
  loadProjects()
  if (form.project_id) {
    handleProjectChange(form.project_id)
  }
})
</script>

<style scoped>
@import '~/styles/common-form.css';

.page-container {
  background: #f5f7fa;
  min-height: calc(100vh - 120px);
}

.config-card, .status-card {
  border-radius: 8px;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.case-selector {
  border: 1px solid #dcdfe6;
  border-radius: 6px;
  overflow: hidden;
}

.case-selector-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: #f5f7fa;
  border-bottom: 1px solid #ebeef5;
}

.case-list {
  display: flex;
  flex-direction: column;
  max-height: 200px;
  overflow-y: auto;
  padding: 8px 12px;
}

.case-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}

.case-item:last-child {
  border-bottom: none;
}

.case-item :deep(.el-checkbox__label) {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
}

.case-name {
  flex: 1;
}

.case-selector-footer {
  padding: 8px 12px;
  background: #f5f7fa;
  border-top: 1px solid #ebeef5;
  font-size: 13px;
  color: #606266;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-left: 12px;
}

.executing-status {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px;
}

.status-text {
  margin: 16px 0;
  color: #606266;
}

.running-info {
  display: flex;
  gap: 24px;
  margin-bottom: 20px;
}

.info-item {
  text-align: center;
}

.info-item .label {
  font-size: 12px;
  color: #909399;
  display: block;
}

.info-item .value {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.info-item .value.success {
  color: #67c23a;
}

.info-item .value.danger {
  color: #f56c6c;
}

.result-status {
  padding: 10px;
}

.result-stats {
  display: flex;
  justify-content: center;
  gap: 24px;
  margin-top: 16px;
}

.stat-item {
  text-align: center;
}

.stat-item .stat-label {
  font-size: 12px;
  color: #909399;
  display: block;
}

.stat-item .stat-value {
  font-size: 20px;
  font-weight: 600;
  color: #303133;
}

.stat-item.success .stat-value {
  color: #67c23a;
}

.stat-item.danger .stat-value {
  color: #f56c6c;
}
</style>
