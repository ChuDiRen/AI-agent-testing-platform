<template>
  <div class="page-container">
    <!-- 搜索区域 -->
    <BaseSearch :model="queryForm" :loading="loading" @search="loadData" @reset="resetQuery">
      <el-form-item label="项目" prop="project_id">
        <el-select v-model="queryForm.project_id" clearable placeholder="选择项目" style="width: 180px">
          <el-option v-for="project in projectList" :key="project.id" :label="project.project_name" :value="project.id"/>
        </el-select>
      </el-form-item>
      <el-form-item label="计划名称" prop="plan_name">
        <el-input v-model="queryForm.plan_name" clearable placeholder="请输入计划名称" style="width: 180px" />
      </el-form-item>
      <template #actions>
        <el-button type="primary" @click="handleAdd">
          <el-icon><Plus /></el-icon>
          新增计划
        </el-button>
      </template>
    </BaseSearch>

    <!-- 表格区域 -->
    <BaseTable 
      title="测试计划管理"
      :data="tableData" 
      :total="total" 
      :loading="loading"
      v-model:pagination="pagination"
      @refresh="loadData"
    >
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="plan_name" label="计划名称" min-width="150" show-overflow-tooltip />
      <el-table-column prop="plan_desc" label="计划描述" min-width="200" show-overflow-tooltip />
      <el-table-column prop="case_count" label="用例数量" width="100" align="center" />
      <el-table-column prop="create_time" label="创建时间" width="160" />
      <el-table-column label="操作" width="350" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="handleEdit(row)">编辑</el-button>
          <el-button link type="success" @click="handleExecute(row)">执行</el-button>
          <el-button link type="warning" @click="handleCopy(row)">复制</el-button>
          <el-button link type="info" @click="handleJenkins(row)">Jenkins</el-button>
          <el-button link type="info" @click="handleViewHistory(row)">历史</el-button>
          <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </BaseTable>

    <!-- Jenkins配置对话框 -->
    <el-dialog v-model="jenkinsDialogVisible" title="Jenkins CI/CD 配置" width="800px">
      <div v-if="jenkinsConfig" class="jenkins-config">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="计划名称">{{ jenkinsConfig.plan_name }}</el-descriptions-item>
          <el-descriptions-item label="用例数量">{{ jenkinsConfig.case_count }}</el-descriptions-item>
          <el-descriptions-item label="API端点" :span="2">{{ jenkinsConfig.api_endpoint }}</el-descriptions-item>
          <el-descriptions-item label="请求方法">{{ jenkinsConfig.request_method }}</el-descriptions-item>
        </el-descriptions>
        
        <el-divider content-position="left">cURL 命令</el-divider>
        <div class="code-block">
          <pre>{{ jenkinsConfig.curl_command }}</pre>
          <el-button size="small" type="primary" @click="copyToClipboard(jenkinsConfig.curl_command)">复制</el-button>
        </div>
        
        <el-divider content-position="left">Jenkins Pipeline 脚本</el-divider>
        <div class="code-block">
          <pre>{{ jenkinsConfig.pipeline_script }}</pre>
          <el-button size="small" type="primary" @click="copyToClipboard(jenkinsConfig.pipeline_script)">复制</el-button>
        </div>
        
        <el-alert type="info" :closable="false" style="margin-top: 16px">
          <template #title>
            <strong>使用说明</strong>
          </template>
          <p>1. 将 <code>{BASE_URL}</code> 替换为实际的服务器地址</p>
          <p>2. 将 <code>{TOKEN}</code> 替换为有效的认证Token</p>
          <p>3. 在Jenkins中配置凭据 <code>api-test-token</code></p>
        </el-alert>
      </div>
      <template #footer>
        <el-button @click="jenkinsDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { queryByPage, deleteData, executePlan, copyPlan, getJenkinsConfig } from './testPlan'
import { queryAllProject } from '~/views/apitest/project/apiProject.js'
import BaseSearch from '~/components/BaseSearch/index.vue'
import BaseTable from '~/components/BaseTable/index.vue'

const router = useRouter()

// 分页参数
const pagination = ref({ page: 1, limit: 10 })
const total = ref(0)
const loading = ref(false)

// 查询表单
const queryForm = reactive({
  project_id: null,
  plan_name: ''
})

// 表格数据
const tableData = ref([])

// 项目列表
const projectList = ref([])

// 加载项目列表
const loadProjectList = async () => {
  try {
    const res = await queryAllProject()
    if (res.data.code === 200) {
      projectList.value = res.data.data || []
    }
  } catch (error) {
    console.error('加载项目列表失败:', error)
  }
}

// 加载数据
const loadData = async () => {
  loading.value = true
  try {
    const res = await queryByPage({
      ...queryForm,
      page: pagination.value.page,
      pageSize: pagination.value.limit
    })
    if (res.data.code === 200) {
      tableData.value = res.data.data || []
      total.value = res.data.total || 0
    }
  } catch (error) {
    ElMessage.error('加载数据失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

// 重置查询
const resetQuery = () => {
  queryForm.project_id = null
  queryForm.plan_name = ''
  pagination.value.page = 1
  loadData()
}

// 新增
const handleAdd = () => {
  router.push('/TestPlanForm')
}

// 编辑
const handleEdit = (row) => {
  router.push({ path: '/TestPlanForm', query: { id: row.id } })
}

// 执行测试计划
const handleExecute = async (row) => {
  try {
    await ElMessageBox.confirm(`确定执行测试计划【${row.plan_name}】吗？`, '提示', {
      type: 'warning'
    })
    
    const res = await executePlan({ 
      plan_id: row.id,
      executor_code: 'api_engine'  // 默认使用 api_engine 执行器
    })
    if (res.data.code === 200) {
      const data = res.data.data || {}
      ElMessage.success(`测试计划已提交执行，共 ${data.total_cases || 0} 个用例`)
      setTimeout(() => {
        router.push('/ApiHistoryList')
      }, 1000)
    } else {
      ElMessage.error(res.data.msg || '执行失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('执行失败: ' + error.message)
    }
  }
}

// 查看执行历史
const handleViewHistory = (row) => {
  // 跳转到测试历史页面，可以带上计划ID作为筛选条件
  router.push({ path: '/ApiHistoryList', query: { plan_id: row.id } })
}

// 复制测试计划
const handleCopy = async (row) => {
  try {
    await ElMessageBox.confirm(`确定复制测试计划【${row.plan_name}】吗？`, '提示', {
      type: 'info'
    })
    
    const res = await copyPlan(row.id)
    if (res.data.code === 200) {
      const data = res.data.data || {}
      ElMessage.success(`复制成功，新计划ID: ${data.new_plan_id}，复制了${data.copied_cases}个用例`)
      loadData()
    } else {
      ElMessage.error(res.data.msg || '复制失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('复制失败: ' + error.message)
    }
  }
}

// Jenkins配置
const jenkinsDialogVisible = ref(false)
const jenkinsConfig = ref(null)

const handleJenkins = async (row) => {
  try {
    const res = await getJenkinsConfig(row.id)
    if (res.data.code === 200) {
      jenkinsConfig.value = res.data.data
      jenkinsDialogVisible.value = true
    } else {
      ElMessage.error(res.data.msg || '获取Jenkins配置失败')
    }
  } catch (error) {
    ElMessage.error('获取Jenkins配置失败: ' + error.message)
  }
}

// 复制文本到剪贴板
const copyToClipboard = (text) => {
  navigator.clipboard.writeText(text).then(() => {
    ElMessage.success('已复制到剪贴板')
  }).catch(() => {
    ElMessage.error('复制失败')
  })
}

// 删除
const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(`确定删除测试计划【${row.plan_name}】吗？`, '警告', {
      type: 'warning'
    })
    
    const res = await deleteData(row.id)
    if (res.data.code === 200) {
      ElMessage.success('删除成功')
      loadData()
    } else {
      ElMessage.error(res.data.msg || '删除失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败: ' + error.message)
    }
  }
}

onMounted(() => {
  loadProjectList()
  loadData()
})
</script>

<style scoped>
@import '~/styles/common-list.css';

.jenkins-config {
  padding: 10px;
}

.code-block {
  position: relative;
  background: #f5f7fa;
  border-radius: 4px;
  padding: 16px;
  margin: 10px 0;
}

.code-block pre {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-all;
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 13px;
  line-height: 1.5;
  max-height: 300px;
  overflow-y: auto;
}

.code-block .el-button {
  position: absolute;
  top: 8px;
  right: 8px;
}
</style>

