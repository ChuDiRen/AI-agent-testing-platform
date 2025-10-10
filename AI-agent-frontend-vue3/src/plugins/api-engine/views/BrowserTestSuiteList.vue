<template>
  <div class="browser-test-suite-list">
    <div class="page-header">
      <h2>浏览器测试套件</h2>
      <el-button type="primary" @click="showCreateDialog = true">
        <el-icon><Plus /></el-icon>
        新建套件
      </el-button>
    </div>

    <!-- 搜索栏 -->
    <div class="search-bar">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-input
            v-model="searchForm.keyword"
            placeholder="搜索套件名称或描述"
            clearable
            @clear="handleSearch"
            @keyup.enter="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-col>
        <el-col :span="4">
          <el-select v-model="searchForm.status" placeholder="状态" clearable @change="handleSearch">
            <el-option label="全部" value="" />
            <el-option label="活跃" value="active" />
            <el-option label="非活跃" value="inactive" />
          </el-select>
        </el-col>
        <el-col :span="6">
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-col>
      </el-row>
    </div>

    <!-- 套件列表 -->
    <div class="suite-list">
      <el-table
        v-loading="loading"
        :data="suiteList"
        style="width: 100%"
        @row-click="handleRowClick"
      >
        <el-table-column prop="name" label="套件名称" min-width="200">
          <template #default="{ row }">
            <div class="suite-name">
              <el-icon class="browser-icon">
                <Monitor />
              </el-icon>
              <span>{{ row.name }}</span>
              <el-tag v-if="row.tags" size="small" type="info">{{ row.tags }}</el-tag>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" min-width="300" show-overflow-tooltip />
        <el-table-column prop="browser_type" label="浏览器" width="120">
          <template #default="{ row }">
            <el-tag :type="getBrowserTagType(row.browser_type)">
              {{ getBrowserLabel(row.browser_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'info'">
              {{ row.status === 'active' ? '活跃' : '非活跃' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click.stop="viewSuite(row)">查看</el-button>
            <el-button link type="primary" @click.stop="editSuite(row)">编辑</el-button>
            <el-button link type="danger" @click.stop="deleteSuite(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :total="pagination.total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </div>

    <!-- 创建套件对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      title="创建浏览器测试套件"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="createFormRef"
        :model="createForm"
        :rules="createRules"
        label-width="120px"
      >
        <el-form-item label="套件名称" prop="name">
          <el-input v-model="createForm.name" placeholder="请输入套件名称" />
        </el-form-item>
        <el-form-item label="套件描述" prop="description">
          <el-input
            v-model="createForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入套件描述"
          />
        </el-form-item>
        <el-form-item label="浏览器类型" prop="browser_type">
          <el-select v-model="createForm.browser_type" placeholder="选择浏览器">
            <el-option label="Chrome" value="chrome" />
            <el-option label="Firefox" value="firefox" />
            <el-option label="Edge" value="edge" />
            <el-option label="Safari" value="safari" />
          </el-select>
        </el-form-item>
        <el-form-item label="无头模式" prop="headless">
          <el-switch v-model="createForm.headless" />
        </el-form-item>
        <el-form-item label="窗口大小" prop="window_size">
          <el-select v-model="createForm.window_size" placeholder="选择窗口大小">
            <el-option label="1920x1080" value="1920x1080" />
            <el-option label="1366x768" value="1366x768" />
            <el-option label="1280x720" value="1280x720" />
            <el-option label="1440x900" value="1440x900" />
          </el-select>
        </el-form-item>
        <el-form-item label="超时时间(秒)" prop="timeout">
          <el-input-number
            v-model="createForm.timeout"
            :min="1"
            :max="300"
            placeholder="超时时间"
          />
        </el-form-item>
        <el-form-item label="重试次数" prop="retry_count">
          <el-input-number
            v-model="createForm.retry_count"
            :min="0"
            :max="10"
            placeholder="重试次数"
          />
        </el-form-item>
        <el-form-item label="标签" prop="tags">
          <el-input v-model="createForm.tags" placeholder="多个标签用逗号分隔" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="handleCreateSuite" :loading="createLoading">
          创建
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, Monitor } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()

// 数据
const loading = ref(false)
const createLoading = ref(false)
const suiteList = ref([])
const showCreateDialog = ref(false)

// 搜索表单
const searchForm = reactive({
  keyword: '',
  status: ''
})

// 分页
const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

// 创建表单
const createFormRef = ref()
const createForm = reactive({
  name: '',
  description: '',
  browser_type: 'chrome',
  headless: true,
  window_size: '1920x1080',
  timeout: 30,
  retry_count: 0,
  tags: ''
})

// 表单验证规则
const createRules = {
  name: [
    { required: true, message: '请输入套件名称', trigger: 'blur' },
    { min: 1, max: 200, message: '长度在 1 到 200 个字符', trigger: 'blur' }
  ],
  browser_type: [
    { required: true, message: '请选择浏览器类型', trigger: 'change' }
  ],
  timeout: [
    { required: true, message: '请输入超时时间', trigger: 'blur' }
  ]
}

// 获取浏览器标签类型
const getBrowserTagType = (browserType) => {
  const typeMap = {
    chrome: 'success',
    firefox: 'warning',
    edge: 'info',
    safari: 'primary'
  }
  return typeMap[browserType] || 'info'
}

// 获取浏览器标签
const getBrowserLabel = (browserType) => {
  const labelMap = {
    chrome: 'Chrome',
    firefox: 'Firefox',
    edge: 'Edge',
    safari: 'Safari'
  }
  return labelMap[browserType] || browserType
}

// 格式化日期时间
const formatDateTime = (dateTime) => {
  if (!dateTime) return '-'
  return new Date(dateTime).toLocaleString('zh-CN')
}

// 获取套件列表
const getSuiteList = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize,
      keyword: searchForm.keyword || undefined,
      status: searchForm.status || undefined
    }

    const response = await axios.get('/api/plugins/api-engine/browser/suites', { params })

    if (response.data.success) {
      suiteList.value = response.data.data.items
      pagination.total = response.data.data.total
    } else {
      ElMessage.error(response.data.message || '获取套件列表失败')
    }
  } catch (error) {
    console.error('获取套件列表失败:', error)
    ElMessage.error('获取套件列表失败')
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  pagination.page = 1
  getSuiteList()
}

// 重置
const handleReset = () => {
  searchForm.keyword = ''
  searchForm.status = ''
  pagination.page = 1
  getSuiteList()
}

// 分页相关
const handleSizeChange = (size) => {
  pagination.pageSize = size
  pagination.page = 1
  getSuiteList()
}

const handleCurrentChange = (page) => {
  pagination.page = page
  getSuiteList()
}

// 行点击
const handleRowClick = (row) => {
  viewSuite(row)
}

// 查看套件
const viewSuite = (suite) => {
  router.push({
    name: 'BrowserTestSuiteDetail',
    params: { suiteId: suite.suite_id }
  })
}

// 编辑套件
const editSuite = (suite) => {
  // TODO: 实现编辑功能
  ElMessage.info('编辑功能开发中')
}

// 删除套件
const deleteSuite = async (suite) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除套件"${suite.name}"吗？此操作不可恢复。`,
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    const response = await axios.delete(`/api/plugins/api-engine/browser/suites/${suite.suite_id}`)

    if (response.data.success) {
      ElMessage.success('删除成功')
      getSuiteList()
    } else {
      ElMessage.error(response.data.message || '删除失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除套件失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

// 创建套件
const handleCreateSuite = async () => {
  if (!createFormRef.value) return

  try {
    await createFormRef.value.validate()
    createLoading.value = true

    const response = await axios.post('/api/plugins/api-engine/browser/suites', createForm)

    if (response.data.success) {
      ElMessage.success('创建成功')
      showCreateDialog.value = false
      // 重置表单
      Object.assign(createForm, {
        name: '',
        description: '',
        browser_type: 'chrome',
        headless: true,
        window_size: '1920x1080',
        timeout: 30,
        retry_count: 0,
        tags: ''
      })
      getSuiteList()
    } else {
      ElMessage.error(response.data.message || '创建失败')
    }
  } catch (error) {
    if (error && error.response) {
      ElMessage.error(error.response.data?.message || '创建失败')
    }
  } finally {
    createLoading.value = false
  }
}

// 初始化
onMounted(() => {
  getSuiteList()
})
</script>

<style scoped>
.browser-test-suite-list {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0;
  color: #303133;
}

.search-bar {
  background: #f5f7fa;
  padding: 20px;
  border-radius: 4px;
  margin-bottom: 20px;
}

.suite-list {
  background: white;
  border-radius: 4px;
  padding: 20px;
}

.suite-name {
  display: flex;
  align-items: center;
  gap: 8px;
}

.browser-icon {
  color: #409eff;
}

.pagination-wrapper {
  margin-top: 20px;
  text-align: right;
}
</style>