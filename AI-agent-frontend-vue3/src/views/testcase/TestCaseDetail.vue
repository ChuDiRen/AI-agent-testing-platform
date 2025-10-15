<!-- Copyright (c) 2025 左岚. All rights reserved. -->
<template>
  <div class="testcase-detail-container">
    <el-card v-loading="loading">
      <template #header>
        <div class="card-header">
          <span class="title">
            <el-icon><View /></el-icon>
            用例详情
          </span>
          <div class="actions">
            <el-button @click="handleBack">
              <el-icon><Back /></el-icon>
              返回
            </el-button>
            <el-button type="primary" @click="handleEdit">
              <el-icon><Edit /></el-icon>
              编辑
            </el-button>
            <el-button
              type="success"
              @click="handleExecute"
              :loading="executing"
            >
              <el-icon><VideoPlay /></el-icon>
              执行
            </el-button>
            <el-button type="danger" @click="handleDelete">
              <el-icon><Delete /></el-icon>
              删除
            </el-button>
          </div>
        </div>
      </template>

      <div v-if="testcase" class="detail-content">
        <!-- 基本信息 -->
        <el-descriptions title="基本信息" :column="2" border>
          <el-descriptions-item label="用例ID">
            {{ testcase.testcase_id }}
          </el-descriptions-item>
          <el-descriptions-item label="用例名称">
            {{ testcase.name }}
          </el-descriptions-item>
          <el-descriptions-item label="测试类型">
            <el-tag :type="getTypeTagType(testcase.test_type)">
              {{ testcase.test_type }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="优先级">
            <el-tag :type="getPriorityTagType(testcase.priority)">
              {{ testcase.priority }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusTagType(testcase.status)">
              {{ getStatusText(testcase.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="所属模块">
            {{ testcase.module || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="创建时间" :span="2">
            {{ formatDate(testcase.create_time) }}
          </el-descriptions-item>
          <el-descriptions-item label="更新时间" :span="2">
            {{ formatDate(testcase.modify_time) }}
          </el-descriptions-item>
        </el-descriptions>

        <!-- 用例描述 -->
        <div class="section" v-if="testcase.description">
          <h3>用例描述</h3>
          <div class="content-box">
            {{ testcase.description }}
          </div>
        </div>

        <!-- 前置条件 -->
        <div class="section" v-if="testcase.preconditions">
          <h3>前置条件</h3>
          <div class="content-box">
            {{ testcase.preconditions }}
          </div>
        </div>

        <!-- 测试步骤 -->
        <div class="section" v-if="testcase.test_steps">
          <h3>测试步骤</h3>
          <div class="content-box">
            {{ testcase.test_steps }}
          </div>
        </div>

        <!-- 预期结果 -->
        <div class="section" v-if="testcase.expected_result">
          <h3>预期结果</h3>
          <div class="content-box">
            {{ testcase.expected_result }}
          </div>
        </div>

        <!-- 标签 -->
        <div class="section" v-if="testcase.tags">
          <h3>标签</h3>
          <div class="content-box">
            {{ testcase.tags }}
          </div>
        </div>
      </div>
    </el-card>

    <!-- 执行结果对话框 -->
    <el-dialog
      v-model="executionDialogVisible"
      title="执行结果"
      width="700px"
    >
      <div v-if="executionResult">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="执行状态">
            <el-tag :type="getExecutionStatusType(executionResult.status)">
              {{ executionResult.status }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="执行时长">
            {{ executionResult.duration }}ms
          </el-descriptions-item>
        </el-descriptions>

        <div v-if="executionResult.error_message" class="error-section">
          <h4>错误信息</h4>
          <el-alert
            :title="executionResult.error_message"
            type="error"
            :closable="false"
            show-icon
          />
        </div>

        <div v-if="executionResult.actual_result" class="result-section">
          <h4>实际结果</h4>
          <el-input
            :value="formatJSON(executionResult.actual_result)"
            type="textarea"
            :rows="6"
            readonly
          />
        </div>

        <div v-if="executionResult.expected_result" class="result-section">
          <h4>预期结果</h4>
          <el-input
            :value="formatJSON(executionResult.expected_result)"
            type="textarea"
            :rows="6"
            readonly
          />
        </div>
      </div>

      <template #footer>
        <el-button @click="executionDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  View,
  Back,
  Edit,
  Delete,
  VideoPlay
} from '@element-plus/icons-vue'
import {
  getTestCaseAPI,
  deleteTestCaseAPI,
  executeTestCaseAPI,
  type TestCase,
  type TestCaseExecutionResult
} from '@/api/testcase'

const route = useRoute()
const router = useRouter()

// 状态
const loading = ref(false)
const executing = ref(false)
const testcase = ref<TestCase | null>(null)
const executionDialogVisible = ref(false)
const executionResult = ref<TestCaseExecutionResult | null>(null)

// 加载用例详情
const loadTestCase = async () => {
  loading.value = true
  try {
    const response = await getTestCaseAPI(Number(route.params.id))
    if (response.data) {
      testcase.value = response.data
    }
  } catch (error: any) {
    ElMessage.error(error.message || '加载失败')
    router.back()
  } finally {
    loading.value = false
  }
}

// 返回
const handleBack = () => {
  router.push('/testcase/list')
}

// 编辑
const handleEdit = () => {
  router.push(`/testcase/${route.params.id}?mode=edit`)
}

// 执行
const handleExecute = async () => {
  executing.value = true
  try {
    const response = await executeTestCaseAPI(Number(route.params.id))
    if (response.data) {
      executionResult.value = response.data
      executionDialogVisible.value = true

      if (response.data.status === 'passed') {
        ElMessage.success('用例执行通过')
      } else {
        ElMessage.warning('用例执行失败')
      }
    }
  } catch (error: any) {
    ElMessage.error(error.message || '执行失败')
  } finally {
    executing.value = false
  }
}

// 删除
const handleDelete = async () => {
  await ElMessageBox.confirm(
    '确认删除此用例吗？此操作不可恢复。',
    '删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  )

  try {
    await deleteTestCaseAPI(Number(route.params.id))
    ElMessage.success('删除成功')
    router.push('/testcase/list')
  } catch (error: any) {
    ElMessage.error(error.message || '删除失败')
  }
}

// 辅助函数
const getTypeTagType = (type: string) => {
  const typeMap: Record<string, any> = {
    API: 'success',
    Web: 'primary',
    App: 'warning'
  }
  return typeMap[type] || ''
}

const getPriorityTagType = (priority: string) => {
  const priorityMap: Record<string, any> = {
    P0: 'danger',
    P1: 'warning',
    P2: '',
    P3: 'info'
  }
  return priorityMap[priority] || ''
}

const getStatusTagType = (status: string) => {
  const statusMap: Record<string, any> = {
    draft: 'info',
    active: 'success',
    deprecated: 'danger'
  }
  return statusMap[status] || ''
}

const getStatusText = (status: string) => {
  const statusMap: Record<string, string> = {
    draft: '草稿',
    active: '启用',
    deprecated: '废弃'
  }
  return statusMap[status] || status
}

const getExecutionStatusType = (status: string) => {
  const statusMap: Record<string, any> = {
    passed: 'success',
    failed: 'warning',
    error: 'danger'
  }
  return statusMap[status] || ''
}

const formatDate = (dateStr?: string) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

const formatJSON = (data: any) => {
  try {
    return JSON.stringify(data, null, 2)
  } catch {
    return String(data)
  }
}

// 初始化
onMounted(() => {
  loadTestCase()
})
</script>

<style scoped lang="scss">
.testcase-detail-container {
  padding: 20px;

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;

    .title {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 16px;
      font-weight: 500;
    }

    .actions {
      display: flex;
      gap: 10px;
    }
  }

  .detail-content {
    .section {
      margin-top: 30px;

      h3 {
        margin-bottom: 15px;
        padding-bottom: 10px;
        border-bottom: 2px solid #409eff;
        font-size: 16px;
        color: #303133;
      }

      .content-box {
        padding: 15px;
        background-color: #f5f7fa;
        border-radius: 4px;
        line-height: 1.8;
        white-space: pre-wrap;
      }
    }

    .error-section,
    .result-section {
      margin-top: 20px;

      h4 {
        margin-bottom: 10px;
        font-size: 14px;
        color: #606266;
      }
    }
  }
}
</style>

