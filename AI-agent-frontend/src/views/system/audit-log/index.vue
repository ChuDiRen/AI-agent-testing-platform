<template>
  <div class="audit-log">
    <div class="page-header">
      <h2>审计日志</h2>
    </div>

    <!-- 查询栏 -->
    <NCard class="search-card">
      <NForm inline :model="queryForm" label-placement="left">
        <NFormItem label="用户名">
          <NInput
            v-model:value="queryForm.username"
            placeholder="请输入用户名"
            clearable
            @keydown.enter="handleSearch"
          />
        </NFormItem>
        <NFormItem label="操作类型">
          <NSelect
            v-model:value="queryForm.action"
            placeholder="请选择操作类型"
            clearable
            :options="actionOptions"
          />
        </NFormItem>
        <NFormItem label="IP地址">
          <NInput
            v-model:value="queryForm.ip_address"
            placeholder="请输入IP地址"
            clearable
            @keydown.enter="handleSearch"
          />
        </NFormItem>
        <NFormItem label="时间范围">
          <NDatePicker
            v-model:value="queryForm.date_range"
            type="datetimerange"
            clearable
            format="yyyy-MM-dd HH:mm:ss"
            value-format="yyyy-MM-dd HH:mm:ss"
          />
        </NFormItem>
        <NFormItem>
          <NSpace>
            <NButton type="primary" @click="handleSearch">
              <template #icon>
                <Icon name="mdi:magnify" />
              </template>
              搜索
            </NButton>
            <NButton @click="handleReset">
              <template #icon>
                <Icon name="mdi:refresh" />
              </template>
              重置
            </NButton>
          </NSpace>
        </NFormItem>
      </NForm>
    </NCard>

    <!-- 数据表格 -->
    <NCard>
      <NDataTable
        :columns="columns"
        :data="tableData"
        :loading="loading"
        :pagination="pagination"
        :row-key="(row) => row.id"
        @update:page="handlePageChange"
        @update:page-size="handlePageSizeChange"
      />
    </NCard>

    <!-- 详情弹窗 -->
    <NModal v-model:show="detailVisible" preset="dialog" title="日志详情" style="width: 600px">
      <div v-if="currentLog" class="log-detail">
        <NDescriptions :column="1" bordered>
          <NDescriptionsItem label="用户名">
            {{ currentLog.username }}
          </NDescriptionsItem>
          <NDescriptionsItem label="操作类型">
            <NTag :type="getActionType(currentLog.action)">
              {{ currentLog.action }}
            </NTag>
          </NDescriptionsItem>
          <NDescriptionsItem label="操作描述">
            {{ currentLog.description }}
          </NDescriptionsItem>
          <NDescriptionsItem label="IP地址">
            {{ currentLog.ip_address }}
          </NDescriptionsItem>
          <NDescriptionsItem label="用户代理">
            {{ currentLog.user_agent }}
          </NDescriptionsItem>
          <NDescriptionsItem label="操作时间">
            {{ formatDate(currentLog.created_at) }}
          </NDescriptionsItem>
          <NDescriptionsItem v-if="currentLog.request_data" label="请求数据">
            <NCode :code="JSON.stringify(currentLog.request_data, null, 2)" language="json" />
          </NDescriptionsItem>
          <NDescriptionsItem v-if="currentLog.response_data" label="响应数据">
            <NCode :code="JSON.stringify(currentLog.response_data, null, 2)" language="json" />
          </NDescriptionsItem>
        </NDescriptions>
      </div>
    </NModal>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, h } from 'vue'
import { NTag, NButton } from 'naive-ui'
import { Icon } from '@iconify/vue'
import { formatDate } from '@/utils'
import api from '@/api'

defineOptions({ name: '审计日志' })

// 响应式数据
const loading = ref(false)
const tableData = ref([])
const detailVisible = ref(false)
const currentLog = ref(null)

// 操作类型选项
const actionOptions = [
  { label: '登录', value: 'LOGIN' },
  { label: '登出', value: 'LOGOUT' },
  { label: '创建', value: 'CREATE' },
  { label: '更新', value: 'UPDATE' },
  { label: '删除', value: 'DELETE' },
  { label: '查询', value: 'SELECT' },
]

// 查询表单
const queryForm = reactive({
  username: '',
  action: '',
  ip_address: '',
  date_range: null,
})

// 分页配置
const pagination = reactive({
  page: 1,
  pageSize: 20,
  itemCount: 0,
  showSizePicker: true,
  pageSizes: [10, 20, 50, 100],
})

// 获取操作类型样式
const getActionType = (action) => {
  const typeMap = {
    LOGIN: 'success',
    LOGOUT: 'info',
    CREATE: 'success',
    UPDATE: 'warning',
    DELETE: 'error',
    SELECT: 'default',
  }
  return typeMap[action] || 'default'
}

// 表格列配置
const columns = [
  { title: '用户名', key: 'username', width: 120 },
  {
    title: '操作类型',
    key: 'action',
    width: 100,
    render: (row) => h(NTag, 
      { type: getActionType(row.action), size: 'small' },
      { default: () => row.action }
    ),
  },
  { title: '操作描述', key: 'description', ellipsis: { tooltip: true } },
  { title: 'IP地址', key: 'ip_address', width: 140 },
  {
    title: '操作时间',
    key: 'created_at',
    width: 180,
    render: (row) => formatDate(row.created_at),
  },
  {
    title: '操作',
    key: 'actions',
    width: 100,
    fixed: 'right',
    render: (row) => {
      return h(NButton, 
        { 
          size: 'small', 
          type: 'primary',
          onClick: () => handleViewDetail(row) 
        },
        { default: () => '详情' }
      )
    },
  },
]

// 获取审计日志列表
const getAuditLogList = async () => {
  try {
    loading.value = true
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize,
      ...queryForm,
    }
    
    // 处理时间范围
    if (queryForm.date_range && queryForm.date_range.length === 2) {
      params.start_time = queryForm.date_range[0]
      params.end_time = queryForm.date_range[1]
    }
    delete params.date_range
    
    const res = await api.getAuditLogList(params)
    tableData.value = res.data.items || res.data
    pagination.itemCount = res.data.total || res.data.length
  } catch (error) {
    window.$message?.error('获取审计日志失败')
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  pagination.page = 1
  getAuditLogList()
}

// 重置
const handleReset = () => {
  Object.assign(queryForm, {
    username: '',
    action: '',
    ip_address: '',
    date_range: null,
  })
  handleSearch()
}

// 分页变化
const handlePageChange = (page) => {
  pagination.page = page
  getAuditLogList()
}

const handlePageSizeChange = (pageSize) => {
  pagination.pageSize = pageSize
  pagination.page = 1
  getAuditLogList()
}

// 查看详情
const handleViewDetail = (row) => {
  currentLog.value = row
  detailVisible.value = true
}

// 初始化
onMounted(() => {
  getAuditLogList()
})
</script>

<style scoped>
.audit-log {
  padding: 16px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.page-header h2 {
  margin: 0;
}

.search-card {
  margin-bottom: 16px;
}

.log-detail {
  max-height: 500px;
  overflow-y: auto;
}
</style>
