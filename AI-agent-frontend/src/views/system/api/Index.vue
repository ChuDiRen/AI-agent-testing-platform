<template>
  <div class="api-management">
    <div class="page-header">
      <h2>API管理</h2>
      <NSpace>
        <NButton
          v-permission="['post/api/refresh']"
          type="info"
          @click="handleRefresh"
        >
          <template #icon>
            <Icon name="mdi:refresh" />
          </template>
          刷新API
        </NButton>
        <NButton
          v-permission="['post/api/create']"
          type="primary"
          @click="handleAdd"
        >
          <template #icon>
            <Icon name="mdi:plus" />
          </template>
          新建API
        </NButton>
      </NSpace>
    </div>

    <!-- 查询栏 -->
    <NCard class="search-card">
      <NForm inline :model="queryForm" label-placement="left">
        <NFormItem label="API路径">
          <NInput
            v-model:value="queryForm.path"
            placeholder="请输入API路径"
            clearable
            @keydown.enter="handleSearch"
          />
        </NFormItem>
        <NFormItem label="请求方法">
          <NSelect
            v-model:value="queryForm.method"
            placeholder="请选择请求方法"
            clearable
            :options="methodOptions"
          />
        </NFormItem>
        <NFormItem label="标签">
          <NInput
            v-model:value="queryForm.tags"
            placeholder="请输入标签"
            clearable
            @keydown.enter="handleSearch"
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

    <!-- 新增/编辑弹窗 -->
    <NModal v-model:show="modalVisible" preset="dialog" :title="modalTitle" style="width: 600px">
      <NForm
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-placement="left"
        label-width="100px"
      >
        <NFormItem label="API路径" path="path">
          <NInput v-model:value="formData.path" placeholder="请输入API路径" />
        </NFormItem>
        <NFormItem label="请求方法" path="method">
          <NSelect
            v-model:value="formData.method"
            placeholder="请选择请求方法"
            :options="methodOptions"
          />
        </NFormItem>
        <NFormItem label="API描述" path="summary">
          <NInput v-model:value="formData.summary" placeholder="请输入API描述" />
        </NFormItem>
        <NFormItem label="标签" path="tags">
          <NInput v-model:value="formData.tags" placeholder="请输入标签" />
        </NFormItem>
      </NForm>
      <template #action>
        <NSpace>
          <NButton @click="modalVisible = false">取消</NButton>
          <NButton type="primary" :loading="submitLoading" @click="handleSubmit">
            确定
          </NButton>
        </NSpace>
      </template>
    </NModal>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, h } from 'vue'
import { Icon } from '@iconify/vue'
import api from '@/api'

defineOptions({ name: 'API管理' })

// 响应式数据
const loading = ref(false)
const tableData = ref([])
const modalVisible = ref(false)
const modalTitle = ref('')
const modalAction = ref('add')
const submitLoading = ref(false)
const formRef = ref()

// 请求方法选项
const methodOptions = [
  { label: 'GET', value: 'GET' },
  { label: 'POST', value: 'POST' },
  { label: 'PUT', value: 'PUT' },
  { label: 'DELETE', value: 'DELETE' },
  { label: 'PATCH', value: 'PATCH' },
]

// 查询表单
const queryForm = reactive({
  path: '',
  method: '',
  tags: '',
})

// 分页配置
const pagination = reactive({
  page: 1,
  pageSize: 20,
  itemCount: 0,
  showSizePicker: true,
  pageSizes: [10, 20, 50, 100],
})

// 表单数据
const formData = reactive({
  id: null,
  path: '',
  method: 'GET',
  summary: '',
  tags: '',
})

// 表单验证规则
const formRules = {
  path: [
    { required: true, message: '请输入API路径', trigger: 'blur' },
  ],
  method: [
    { required: true, message: '请选择请求方法', trigger: 'change' },
  ],
  summary: [
    { required: true, message: '请输入API描述', trigger: 'blur' },
  ],
}

// 表格列配置
const columns = [
  { title: 'API路径', key: 'path', width: 300, ellipsis: { tooltip: true } },
  {
    title: '请求方法',
    key: 'method',
    width: 100,
    align: 'center',
    render: (row) => {
      const colorMap = {
        GET: 'success',
        POST: 'info',
        PUT: 'warning',
        DELETE: 'error',
        PATCH: 'default',
      }
      return h(NTag, 
        { type: colorMap[row.method] || 'default', size: 'small' },
        { default: () => row.method }
      )
    },
  },
  { title: 'API描述', key: 'summary', ellipsis: { tooltip: true } },
  { title: '标签', key: 'tags', width: 120 },
  {
    title: '操作',
    key: 'actions',
    width: 150,
    fixed: 'right',
    render: (row) => {
      return h('div', [
        h(NButton, 
          { 
            size: 'small', 
            type: 'primary', 
            style: 'margin-right: 8px',
            onClick: () => handleEdit(row) 
          },
          { default: () => '编辑' }
        ),
        h(NPopconfirm, 
          {
            onPositiveClick: () => handleDelete(row),
          },
          {
            trigger: () => h(NButton, 
              { size: 'small', type: 'error' },
              { default: () => '删除' }
            ),
            default: () => '确定删除该API吗？',
          }
        ),
      ])
    },
  },
]

// 获取API列表
const getApiList = async () => {
  try {
    loading.value = true
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize,
      ...queryForm,
    }
    const res = await api.getApis(params)
    tableData.value = res.data.items || res.data
    pagination.itemCount = res.data.total || res.data.length
  } catch (error) {
    window.$message?.error('获取API列表失败')
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  pagination.page = 1
  getApiList()
}

// 重置
const handleReset = () => {
  Object.assign(queryForm, {
    path: '',
    method: '',
    tags: '',
  })
  handleSearch()
}

// 分页变化
const handlePageChange = (page) => {
  pagination.page = page
  getApiList()
}

const handlePageSizeChange = (pageSize) => {
  pagination.pageSize = pageSize
  pagination.page = 1
  getApiList()
}

// 刷新API
const handleRefresh = async () => {
  try {
    loading.value = true
    await api.refreshApi()
    window.$message?.success('API刷新成功')
    getApiList()
  } catch (error) {
    window.$message?.error('API刷新失败')
  } finally {
    loading.value = false
  }
}

// 新增
const handleAdd = () => {
  modalAction.value = 'add'
  modalTitle.value = '新增API'
  Object.assign(formData, {
    id: null,
    path: '',
    method: 'GET',
    summary: '',
    tags: '',
  })
  modalVisible.value = true
}

// 编辑
const handleEdit = (row) => {
  modalAction.value = 'edit'
  modalTitle.value = '编辑API'
  Object.assign(formData, {
    id: row.id,
    path: row.path,
    method: row.method,
    summary: row.summary,
    tags: row.tags,
  })
  modalVisible.value = true
}

// 提交表单
const handleSubmit = async () => {
  try {
    await formRef.value?.validate()
    submitLoading.value = true
    
    if (modalAction.value === 'add') {
      await api.createApi(formData)
      window.$message?.success('创建成功')
    } else {
      await api.updateApi(formData)
      window.$message?.success('更新成功')
    }
    
    modalVisible.value = false
    getApiList()
  } catch (error) {
    console.error('提交失败:', error)
  } finally {
    submitLoading.value = false
  }
}

// 删除
const handleDelete = async (row) => {
  try {
    await api.deleteApi({ api_id: row.id })
    window.$message?.success('删除成功')
    getApiList()
  } catch (error) {
    window.$message?.error('删除失败')
  }
}

// 初始化
onMounted(() => {
  getApiList()
})
</script>

<style scoped>
.api-management {
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
</style>
