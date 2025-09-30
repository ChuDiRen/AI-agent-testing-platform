<template>
  <div class="role-management">
    <div class="page-header">
      <h2>角色管理</h2>
      <NButton
        v-permission="['post/role/create']"
        type="primary"
        @click="handleAdd"
      >
        <template #icon>
          <Icon name="mdi:plus" />
        </template>
        新建角色
      </NButton>
    </div>

    <!-- 查询栏 -->
    <NCard class="search-card">
      <NForm inline :model="queryForm" label-placement="left">
        <NFormItem label="角色名">
          <NInput
            v-model:value="queryForm.role_name"
            placeholder="请输入角色名"
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
        :row-key="(row) => row.role_id"
        @update:page="handlePageChange"
        @update:page-size="handlePageSizeChange"
      />
    </NCard>

    <!-- 新增/编辑弹窗 -->
    <NModal v-model:show="modalVisible" preset="dialog" :title="modalTitle">
      <NForm
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-placement="left"
        label-width="80px"
      >
        <NFormItem label="角色名" path="role_name">
          <NInput v-model:value="formData.role_name" placeholder="请输入角色名" />
        </NFormItem>
        <NFormItem label="角色描述" path="remark">
          <NInput
            v-model:value="formData.remark"
            type="textarea"
            placeholder="请输入角色描述"
            :rows="3"
          />
        </NFormItem>
        <NFormItem label="状态">
          <NSwitch
            v-model:value="formData.is_active"
            :checked-value="true"
            :unchecked-value="false"
          />
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

    <!-- 权限设置抽屉 -->
    <NDrawer v-model:show="permissionDrawerVisible" :width="500" placement="right">
      <NDrawerContent title="设置权限">
        <div class="permission-header">
          <NInput
            v-model:value="filterPattern"
            placeholder="筛选权限"
            clearable
          />
          <NButton
            type="primary"
            style="margin-left: 12px"
            @click="handleSavePermission"
          >
            保存
          </NButton>
        </div>

        <NTabs default-value="menu" style="margin-top: 16px">
          <NTabPane name="menu" tab="菜单权限">
            <NTree
              :data="menuOptions"
              :checked-keys="checkedMenuKeys"
              :pattern="filterPattern"
              key-field="menu_id"
              label-field="menu_name"
              checkable
              cascade
              default-expand-all
              @update:checked-keys="handleMenuCheck"
            />
          </NTabPane>
          <NTabPane name="api" tab="接口权限">
            <NTree
              :data="apiOptions"
              :checked-keys="checkedApiKeys"
              :pattern="filterPattern"
              key-field="unique_id"
              label-field="summary"
              checkable
              cascade
              default-expand-all
              @update:checked-keys="handleApiCheck"
            />
          </NTabPane>
        </NTabs>
      </NDrawerContent>
    </NDrawer>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, h } from 'vue'
import { Icon } from '@iconify/vue'
import { formatDate } from '@/utils'
import api from '@/api'

defineOptions({ name: '角色管理' })

// 响应式数据
const loading = ref(false)
const tableData = ref([])
const modalVisible = ref(false)
const modalTitle = ref('')
const modalAction = ref('add')
const submitLoading = ref(false)
const formRef = ref()
const permissionDrawerVisible = ref(false)
const currentRoleId = ref(null)
const filterPattern = ref('')

// 权限相关
const menuOptions = ref([])
const apiOptions = ref([])
const checkedMenuKeys = ref([])
const checkedApiKeys = ref([])

// 查询表单
const queryForm = reactive({
  role_name: '',
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
  role_id: null,
  role_name: '',
  remark: '',
  is_active: true,
})

// 表单验证规则
const formRules = {
  role_name: [
    { required: true, message: '请输入角色名', trigger: 'blur' },
  ],
}

// 表格列配置
const columns = [
  { title: '角色ID', key: 'role_id', width: 80 },
  {
    title: '角色名',
    key: 'role_name',
    width: 150,
    render: (row) => h(NTag, { type: 'info' }, { default: () => row.role_name }),
  },
  { title: '角色描述', key: 'remark', ellipsis: { tooltip: true } },
  {
    title: '状态',
    key: 'is_active',
    width: 80,
    render: (row) => h(NTag,
      { type: row.is_active ? 'success' : 'error', size: 'small' },
      { default: () => row.is_active ? '启用' : '禁用' }
    ),
  },
  {
    title: '创建时间',
    key: 'created_at',
    width: 180,
    render: (row) => row.created_at || '-',
  },
  {
    title: '操作',
    key: 'actions',
    width: 200,
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
        h(NButton, 
          { 
            size: 'small', 
            type: 'info', 
            style: 'margin-right: 8px',
            onClick: () => handleSetPermission(row) 
          },
          { default: () => '设置权限' }
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
            default: () => '确定删除该角色吗？',
          }
        ),
      ])
    },
  },
]

// 构建API树结构
const buildApiTree = (data) => {
  const tree = []
  const groupMap = new Map()

  data.forEach(item => {
    const pathParts = item.path.split('/')
    const groupPath = pathParts.slice(0, -1).join('/')
    const groupName = item.tags || '其他'
    
    if (!groupMap.has(groupName)) {
      const group = {
        unique_id: groupName,
        summary: groupName,
        children: []
      }
      groupMap.set(groupName, group)
      tree.push(group)
    }
    
    groupMap.get(groupName).children.push({
      unique_id: `${item.method.toLowerCase()}${item.path}`,
      summary: `${item.method} ${item.path} - ${item.summary}`,
      path: item.path,
      method: item.method,
      id: item.id
    })
  })

  return tree
}

// 获取角色列表
const getRoleList = async () => {
  try {
    loading.value = true
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize,
      ...queryForm,
    }
    const res = await api.getRoleList(params)
    if (res.code === 200 && res.data) {
      tableData.value = res.data.items || []
      pagination.itemCount = res.data.total || 0
    }
  } catch (error) {
    window.$message?.error('获取角色列表失败')
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  pagination.page = 1
  getRoleList()
}

// 重置
const handleReset = () => {
  Object.assign(queryForm, {
    role_name: '',
  })
  handleSearch()
}

// 分页变化
const handlePageChange = (page) => {
  pagination.page = page
  getRoleList()
}

const handlePageSizeChange = (pageSize) => {
  pagination.pageSize = pageSize
  pagination.page = 1
  getRoleList()
}

// 新增
const handleAdd = () => {
  modalAction.value = 'add'
  modalTitle.value = '新增角色'
  Object.assign(formData, {
    role_id: null,
    role_name: '',
    remark: '',
    is_active: true,
  })
  modalVisible.value = true
}

// 编辑
const handleEdit = (row) => {
  modalAction.value = 'edit'
  modalTitle.value = '编辑角色'
  Object.assign(formData, {
    role_id: row.role_id,
    role_name: row.role_name,
    remark: row.remark || '',
    is_active: row.is_active !== undefined ? row.is_active : true,
  })
  modalVisible.value = true
}

// 提交表单
const handleSubmit = async () => {
  try {
    await formRef.value?.validate()
    submitLoading.value = true
    
    if (modalAction.value === 'add') {
      await api.createRole(formData)
      window.$message?.success('创建成功')
    } else {
      await api.updateRole(formData)
      window.$message?.success('更新成功')
    }
    
    modalVisible.value = false
    getRoleList()
  } catch (error) {
    console.error('提交失败:', error)
  } finally {
    submitLoading.value = false
  }
}

// 删除
const handleDelete = async (row) => {
  try {
    await api.deleteRole({ role_id: row.role_id })
    window.$message?.success('删除成功')
    getRoleList()
  } catch (error) {
    window.$message?.error('删除失败')
  }
}

// 设置权限
const handleSetPermission = async (row) => {
  try {
    currentRoleId.value = row.role_id

    // 并行获取菜单、API和角色权限数据
    const [menuRes, apiRes, roleAuthRes] = await Promise.all([
      api.getMenus(),
      api.getApis(),
      api.getRoleAuthorized({ role_id: row.role_id })
    ])

    // 处理菜单数据
    if (menuRes.code === 200 && menuRes.data) {
      menuOptions.value = Array.isArray(menuRes.data) ? menuRes.data : []
    }

    // 处理API数据
    if (apiRes.code === 200 && apiRes.data) {
      const apiList = apiRes.data.items || []
      apiOptions.value = buildApiTree(apiList)
    }

    // 处理角色权限数据
    if (roleAuthRes.code === 200 && roleAuthRes.data) {
      checkedMenuKeys.value = roleAuthRes.data.menu_ids || []
      checkedApiKeys.value = roleAuthRes.data.api_ids || []
    }

    permissionDrawerVisible.value = true
  } catch (error) {
    console.error('获取权限数据失败:', error)
    window.$message?.error('获取权限数据失败')
  }
}

// 菜单权限选择
const handleMenuCheck = (keys) => {
  checkedMenuKeys.value = keys
}

// API权限选择
const handleApiCheck = (keys) => {
  checkedApiKeys.value = keys
}

// 保存权限
const handleSavePermission = async () => {
  try {
    // 过滤掉分组节点，只保留实际的API ID
    const apiIds = checkedApiKeys.value.filter(key => {
      // 检查是否是实际的API（不是分组）
      let isActualApi = false
      apiOptions.value.forEach(group => {
        group.children?.forEach(api => {
          if (api.unique_id === key && api.id) {
            isActualApi = true
          }
        })
      })
      return isActualApi
    }).map(key => {
      // 从unique_id中提取实际的API ID
      let apiId = null
      apiOptions.value.forEach(group => {
        group.children?.forEach(api => {
          if (api.unique_id === key) {
            apiId = api.id
          }
        })
      })
      return apiId
    }).filter(id => id !== null)

    await api.updateRoleAuthorized({
      role_id: currentRoleId.value,
      menu_ids: checkedMenuKeys.value,
      api_ids: apiIds
    })

    window.$message?.success('权限设置成功')
    permissionDrawerVisible.value = false
  } catch (error) {
    console.error('权限设置失败:', error)
    window.$message?.error('权限设置失败')
  }
}

// 初始化
onMounted(() => {
  getRoleList()
})
</script>

<style scoped>
.role-management {
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

.permission-header {
  display: flex;
  align-items: center;
}
</style>
