<!-- Copyright (c) 2025 左岚. All rights reserved. -->
<template>
  <div class="unified-execute-container">
    <!-- 页面标题 -->
    <el-page-header :content="pageTitle" class="page-header" />

    <!-- 选择测试用例 -->
    <el-card class="select-card">
      <template #header>
        <span>选择测试用例</span>
      </template>
      <el-select
        v-model="selectedTestCaseId"
        placeholder="请选择要执行的测试用例"
        filterable
        style="width: 100%"
        @change="handleTestCaseChange"
      >
        <el-option
          v-for="testCase in testCases"
          :key="testCase.testcase_id"
          :label="`${testCase.name} (${testCase.module || '默认模块'})`"
          :value="testCase.testcase_id"
        />
      </el-select>
    </el-card>

    <!-- 测试用例详情 -->
    <el-card v-if="currentTestCase" class="detail-card">
      <template #header>
        <span>测试用例详情</span>
      </template>
      <el-descriptions :column="2" border>
        <el-descriptions-item label="用例名称">{{ currentTestCase.name }}</el-descriptions-item>
        <el-descriptions-item label="所属模块">{{ currentTestCase.module || '-' }}</el-descriptions-item>
        <el-descriptions-item label="优先级">
          <el-tag>{{ currentTestCase.priority }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusType(currentTestCase.status)">
            {{ statusMap[currentTestCase.status] }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="用例描述" :span="2">
          {{ currentTestCase.description || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="前置条件" :span="2">
          <pre class="pre-content">{{ currentTestCase.preconditions || '-' }}</pre>
        </el-descriptions-item>
        <el-descriptions-item label="测试步骤" :span="2">
          <pre class="pre-content">{{ currentTestCase.test_steps || '-' }}</pre>
        </el-descriptions-item>
        <el-descriptions-item label="预期结果" :span="2">
          <pre class="pre-content">{{ currentTestCase.expected_result || '-' }}</pre>
        </el-descriptions-item>
      </el-descriptions>
    </el-card>

    <!-- 执行配置 -->
    <el-card v-if="currentTestCase" class="config-card">
      <template #header>
        <div class="card-header-with-action">
          <span>执行配置</span>
          <div class="header-actions">
            <el-button size="small" @click="handleLoadConfig">加载配置</el-button>
            <el-button size="small" type="primary" @click="handleSaveConfig">保存配置</el-button>
          </div>
        </div>
      </template>
      <el-form :model="executeConfig" label-width="140px">
        <!-- API配置 -->
        <template v-if="testType === 'api'">
          <el-form-item label="基础URL">
            <el-input 
              v-model="executeConfig.base_url" 
              placeholder="http://localhost:8000 或 https://api.example.com"
              clearable
            >
              <template #prepend>
                <el-icon><Link /></el-icon>
              </template>
            </el-input>
          </el-form-item>
          <el-form-item label="请求头">
            <el-input
              v-model="executeConfig.default_headers_str"
              type="textarea"
              :rows="3"
              placeholder='{"Content-Type": "application/json", "Authorization": "Bearer token"}'
            />
            <el-text type="info" size="small">JSON格式，例如：{"Key": "Value"}</el-text>
          </el-form-item>
          <el-form-item label="超时时间(秒)">
            <el-input-number v-model="executeConfig.timeout" :min="1" :max="300" />
            <el-text type="info" size="small" style="margin-left: 12px">
              默认30秒
            </el-text>
          </el-form-item>
          <el-form-item label="SSL证书验证">
            <el-switch v-model="executeConfig.verify_ssl" />
            <el-text type="warning" size="small" style="margin-left: 12px">
              关闭后可以访问自签名证书的HTTPS接口
            </el-text>
          </el-form-item>
          <el-form-item label="环境">
            <el-radio-group v-model="executeConfig.environment">
              <el-radio label="dev">开发环境</el-radio>
              <el-radio label="test">测试环境</el-radio>
              <el-radio label="staging">预发布环境</el-radio>
              <el-radio label="prod">生产环境</el-radio>
            </el-radio-group>
          </el-form-item>
        </template>

        <!-- Web配置 -->
        <template v-if="testType === 'web'">
          <el-form-item label="浏览器">
            <el-select v-model="executeConfig.browser">
              <el-option label="Chrome" value="chrome" />
              <el-option label="Firefox" value="firefox" />
              <el-option label="Edge" value="edge" />
            </el-select>
          </el-form-item>
          <el-form-item label="无头模式">
            <el-switch v-model="executeConfig.headless" />
          </el-form-item>
        </template>

        <!-- App配置 -->
        <template v-if="testType === 'app'">
          <el-form-item label="平台">
            <el-select v-model="executeConfig.platform">
              <el-option label="Android" value="android" />
              <el-option label="iOS" value="ios" />
            </el-select>
          </el-form-item>
          <el-form-item label="设备名称">
            <el-input v-model="executeConfig.device" placeholder="请输入设备名称或模拟器" />
          </el-form-item>
        </template>
      </el-form>
    </el-card>

    <!-- 执行按钮 -->
    <el-card v-if="currentTestCase" class="action-card">
      <el-button
        type="primary"
        size="large"
        :loading="executing"
        :disabled="!selectedTestCaseId"
        @click="handleExecute"
        :icon="VideoPlay"
      >
        {{ executing ? '执行中...' : '开始执行' }}
      </el-button>
      <el-button
        v-if="executing"
        type="danger"
        size="large"
        @click="handleStop"
        :icon="VideoPause"
      >
        停止执行
      </el-button>
    </el-card>

    <!-- 执行结果 -->
    <el-card v-if="executeResult" class="result-card">
      <template #header>
        <div class="result-header">
          <span>执行结果</span>
          <el-tag
            :type="executeResult.status === 'passed' ? 'success' : 'danger'"
            size="large"
          >
            {{ statusTextMap[executeResult.status] || executeResult.status }}
          </el-tag>
        </div>
      </template>

      <el-descriptions :column="2" border>
        <el-descriptions-item label="执行状态">
          <el-tag :type="getResultType(executeResult.status)">
            {{ statusTextMap[executeResult.status] }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="执行时长">
          {{ executeResult.duration }}秒
        </el-descriptions-item>
        <el-descriptions-item label="开始时间">
          {{ executeResult.start_time }}
        </el-descriptions-item>
        <el-descriptions-item label="结束时间">
          {{ executeResult.end_time }}
        </el-descriptions-item>
        <el-descriptions-item label="执行器">
          {{ executeResult.executor }}
        </el-descriptions-item>
        <el-descriptions-item label="用例名称">
          {{ executeResult.testcase_name }}
        </el-descriptions-item>
        <el-descriptions-item v-if="executeResult.actual_result" label="实际结果" :span="2">
          <pre class="result-content">{{ executeResult.actual_result }}</pre>
        </el-descriptions-item>
        <el-descriptions-item v-if="executeResult.error_message" label="错误信息" :span="2">
          <el-alert
            :title="executeResult.error_message"
            type="error"
            :closable="false"
          />
        </el-descriptions-item>
        <el-descriptions-item v-if="executeResult.details" label="详细信息" :span="2">
          <pre class="result-content">{{ JSON.stringify(executeResult.details, null, 2) }}</pre>
        </el-descriptions-item>
      </el-descriptions>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { VideoPlay, VideoPause, Link } from '@element-plus/icons-vue'
import request from '@/api/request'

// Props
const props = defineProps<{
  testType: 'api' | 'web' | 'app'
}>()

// 页面标题
const testTypeMap: Record<string, string> = {
  api: 'API',
  web: 'WEB',
  app: 'APP'
}

const pageTitle = computed(() => `${testTypeMap[props.testType]}测试执行`)

// 状态映射
const statusMap: Record<string, string> = {
  draft: '草稿',
  active: '活跃',
  archived: '已归档'
}

const statusTextMap: Record<string, string> = {
  passed: '通过',
  failed: '失败',
  error: '错误',
  skipped: '跳过'
}

// 状态
const testCases = ref<any[]>([])
const selectedTestCaseId = ref<number>()
const currentTestCase = ref<any>(null)
const executing = ref(false)
const executeResult = ref<any>(null)

// 执行配置
const executeConfig = reactive<any>({
  // API配置
  base_url: 'http://localhost:8000',
  default_headers_str: '',
  timeout: 30,
  verify_ssl: true,
  environment: 'dev',
  // Web配置
  browser: 'chrome',
  headless: false,
  // App配置
  platform: 'android',
  device: '模拟器'
})

// 配置存储key
const CONFIG_STORAGE_KEY = 'test_execute_config'

// 获取状态类型
const getStatusType = (status: string) => {
  const types: Record<string, any> = {
    draft: 'info',
    active: 'success',
    archived: 'warning'
  }
  return types[status] || ''
}

// 获取结果类型
const getResultType = (status: string) => {
  const types: Record<string, any> = {
    passed: 'success',
    failed: 'danger',
    error: 'danger',
    skipped: 'info'
  }
  return types[status] || 'info'
}

// 加载测试用例
const loadTestCases = async () => {
  try {
    const response = await request({
      url: '/testcases',
      method: 'get',
      params: {
        test_type: props.testType,
        status: 'active',
        page: 1,
        page_size: 100
      }
    })

    if (response.data) {
      testCases.value = response.data.items || []
    }
  } catch (error: any) {
    ElMessage.error(error.message || '加载测试用例失败')
  }
}

// 测试用例变化
const handleTestCaseChange = (testcaseId: number) => {
  currentTestCase.value = testCases.value.find(tc => tc.testcase_id === testcaseId)
  executeResult.value = null
}

// 执行测试
const handleExecute = async () => {
  if (!selectedTestCaseId.value) {
    ElMessage.warning('请先选择测试用例')
    return
  }

  executing.value = true
  executeResult.value = null

  try {
    // 准备配置参数
    const config: any = {}
    
    if (props.testType === 'api') {
      config.base_url = executeConfig.base_url
      config.timeout = executeConfig.timeout
      config.verify_ssl = executeConfig.verify_ssl
      
      // 解析请求头
      if (executeConfig.default_headers_str) {
        try {
          config.default_headers = JSON.parse(executeConfig.default_headers_str)
        } catch (e) {
          ElMessage.warning('请求头JSON格式错误，将忽略')
        }
      }
    } else if (props.testType === 'web') {
      config.browser = executeConfig.browser
      config.headless = executeConfig.headless
    } else if (props.testType === 'app') {
      config.platform = executeConfig.platform
      config.device = executeConfig.device
    }

    const response = await request({
      url: `/testcases/${selectedTestCaseId.value}/execute`,
      method: 'post',
      data: {
        config
      }
    })

    if (response.data) {
      executeResult.value = response.data
      ElMessage.success('执行完成')
    }
  } catch (error: any) {
    ElMessage.error(error.message || '执行失败')
    executeResult.value = {
      status: 'error',
      error_message: error.message || '执行失败',
      duration: 0,
      testcase_name: currentTestCase.value?.name || '',
      start_time: new Date().toISOString(),
      end_time: new Date().toISOString(),
      executor: 'Unknown'
    }
  } finally {
    executing.value = false
  }
}

// 停止执行
const handleStop = () => {
  executing.value = false
  ElMessage.info('已停止执行')
}

// 保存配置
const handleSaveConfig = () => {
  try {
    // 构建配置对象
    const configToSave: any = {
      testType: props.testType,
      timestamp: new Date().toISOString()
    }
    
    if (props.testType === 'api') {
      configToSave.base_url = executeConfig.base_url
      configToSave.default_headers_str = executeConfig.default_headers_str
      configToSave.timeout = executeConfig.timeout
      configToSave.verify_ssl = executeConfig.verify_ssl
      configToSave.environment = executeConfig.environment
    } else if (props.testType === 'web') {
      configToSave.browser = executeConfig.browser
      configToSave.headless = executeConfig.headless
    } else if (props.testType === 'app') {
      configToSave.platform = executeConfig.platform
      configToSave.device = executeConfig.device
    }
    
    // 保存到localStorage
    const storageKey = `${CONFIG_STORAGE_KEY}_${props.testType}`
    localStorage.setItem(storageKey, JSON.stringify(configToSave))
    
    ElMessage.success('配置已保存')
  } catch (error: any) {
    console.error('保存配置失败:', error)
    ElMessage.error('保存配置失败')
  }
}

// 加载配置
const handleLoadConfig = () => {
  try {
    const storageKey = `${CONFIG_STORAGE_KEY}_${props.testType}`
    const savedConfig = localStorage.getItem(storageKey)
    
    if (!savedConfig) {
      ElMessage.info('暂无保存的配置')
      return
    }
    
    const config = JSON.parse(savedConfig)
    
    // 应用配置
    if (props.testType === 'api' && config.testType === 'api') {
      executeConfig.base_url = config.base_url || 'http://localhost:8000'
      executeConfig.default_headers_str = config.default_headers_str || ''
      executeConfig.timeout = config.timeout || 30
      executeConfig.verify_ssl = config.verify_ssl !== undefined ? config.verify_ssl : true
      executeConfig.environment = config.environment || 'dev'
    } else if (props.testType === 'web' && config.testType === 'web') {
      executeConfig.browser = config.browser || 'chrome'
      executeConfig.headless = config.headless || false
    } else if (props.testType === 'app' && config.testType === 'app') {
      executeConfig.platform = config.platform || 'android'
      executeConfig.device = config.device || '模拟器'
    }
    
    ElMessage.success('配置已加载')
  } catch (error: any) {
    console.error('加载配置失败:', error)
    ElMessage.error('加载配置失败')
  }
}

// 初始化时自动加载配置
const initializeConfig = () => {
  try {
    const storageKey = `${CONFIG_STORAGE_KEY}_${props.testType}`
    const savedConfig = localStorage.getItem(storageKey)
    
    if (savedConfig) {
      const config = JSON.parse(savedConfig)
      
      // 静默应用配置
      if (props.testType === 'api' && config.testType === 'api') {
        executeConfig.base_url = config.base_url || 'http://localhost:8000'
        executeConfig.default_headers_str = config.default_headers_str || ''
        executeConfig.timeout = config.timeout || 30
        executeConfig.verify_ssl = config.verify_ssl !== undefined ? config.verify_ssl : true
        executeConfig.environment = config.environment || 'dev'
      } else if (props.testType === 'web' && config.testType === 'web') {
        executeConfig.browser = config.browser || 'chrome'
        executeConfig.headless = config.headless || false
      } else if (props.testType === 'app' && config.testType === 'app') {
        executeConfig.platform = config.platform || 'android'
        executeConfig.device = config.device || '模拟器'
      }
    }
  } catch (error) {
    // 初始化失败不影响使用
    console.warn('初始化配置失败:', error)
  }
}

// 初始化
onMounted(() => {
  initializeConfig()
  loadTestCases()
})
</script>

<style scoped lang="scss">
.unified-execute-container {
  padding: 20px;

  .page-header {
    margin-bottom: 20px;
  }

  .select-card,
  .detail-card,
  .config-card,
  .action-card,
  .result-card {
    margin-bottom: 20px;
  }

  .pre-content {
    white-space: pre-wrap;
    word-wrap: break-word;
    margin: 0;
    font-family: monospace;
    font-size: 13px;
    line-height: 1.5;
  }

  .result-content {
    white-space: pre-wrap;
    word-wrap: break-word;
    margin: 0;
    padding: 10px;
    background: #f5f7fa;
    border-radius: 4px;
    font-family: monospace;
    font-size: 13px;
    line-height: 1.5;
    max-height: 400px;
    overflow-y: auto;
  }

  .result-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .action-card {
    text-align: center;

    .el-button {
      min-width: 150px;
      margin: 0 10px;
    }
  }

  .card-header-with-action {
    display: flex;
    justify-content: space-between;
    align-items: center;

    .header-actions {
      display: flex;
      gap: 8px;
    }
  }
}
</style>

