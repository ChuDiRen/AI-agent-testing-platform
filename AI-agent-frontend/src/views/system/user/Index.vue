<template>
  <PageWrapper title="用户管理" icon="mdi:account-group">
    <template #extra>
      <NButton
        v-permission="['post/user/create']"
        type="primary"
        @click="handleAdd"
      >
        <template #icon>
          <Icon name="mdi:plus" />
        </template>
        新建用户
      </NButton>
    </template>

    <NLayout has-sider>
      <!-- 部门侧边栏 -->
      <NLayoutSider
        bordered
        :collapsed-width="0"
        :width="240"
        show-trigger="arrow-circle"
        content-style="padding: 16px;"
      >
        <div class="dept-header">
          <h3>部门列表</h3>
        </div>
        <NTree
          block-line
          :data="deptOptions"
          key-field="id"
          label-field="name"
          default-expand-all
          :node-props="nodeProps"
        />
      </NLayoutSider>

      <!-- 主内容区 -->
      <NLayoutContent>
        <CrudTable
          ref="tableRef"
          v-model:query-items="queryItems"
          :scroll-x="1200"
          :columns="columns"
          :get-data="api.getUserList"
          @on-data-change="handleDataChange"
        >
          <template #queryBar>
            <QueryBarItem label="用户名">
              <NInput
                v-model:value="queryItems.username"
                placeholder="请输入用户名"
                clearable
              />
            </QueryBarItem>
            <QueryBarItem label="邮箱">
              <NInput
                v-model:value="queryItems.email"
                placeholder="请输入邮箱"
                clearable
              />
            </QueryBarItem>
            <QueryBarItem label="状态">
              <NSelect
                v-model:value="queryItems.status"
                placeholder="请选择状态"
                clearable
                :options="statusOptions"
              />
            </QueryBarItem>
          </template>
        </CrudTable>
      </NLayoutContent>
    </NLayout>

    <!-- 新增/编辑弹窗 -->
    <CrudModal
      v-model:visible="modalVisible"
      :type="modalAction"
      :data="formData"
      :rules="formRules"
      :on-save="handleSave"
      @success="handleSuccess"
    >
      <template #default="{ formData }">
        <NFormItem label="用户名" path="username">
          <NInput
            v-model:value="formData.username"
            placeholder="请输入用户名"
            :disabled="modalAction === 'edit'"
          />
        </NFormItem>
        <NFormItem label="邮箱" path="email">
          <NInput v-model:value="formData.email" placeholder="请输入邮箱" />
        </NFormItem>
        <NFormItem v-if="modalAction === 'add'" label="密码" path="password">
          <NInput
            v-model:value="formData.password"
            type="password"
            show-password-on="mousedown"
            placeholder="请输入密码"
          />
        </NFormItem>
        <NFormItem v-if="modalAction === 'add'" label="确认密码" path="confirmPassword">
          <NInput
            v-model:value="formData.confirmPassword"
            type="password"
            show-password-on="mousedown"
            placeholder="请确认密码"
          />
        </NFormItem>
        <NFormItem label="角色" path="role_ids">
          <NCheckboxGroup v-model:value="formData.role_ids">
            <NSpace>
              <NCheckbox
                v-for="role in roleOptions"
                :key="role.id"
                :value="role.id"
                :label="role.name"
              />
            </NSpace>
          </NCheckboxGroup>
        </NFormItem>
        <NFormItem label="部门" path="dept_id">
          <NTreeSelect
            v-model:value="formData.dept_id"
            :options="deptOptions"
            key-field="id"
            label-field="name"
            placeholder="请选择部门"
            clearable
          />
        </NFormItem>
        <NFormItem label="超级用户">
          <NSwitch v-model:value="formData.is_superuser" />
        </NFormItem>
        <NFormItem label="状态">
          <NSwitch
            v-model:value="formData.is_active"
            :checked-value="true"
            :unchecked-value="false"
          />
        </NFormItem>
      </template>
    </CrudModal>
  </PageWrapper>
</template>

<script setup>
import { ref, reactive, onMounted, h } from 'vue'
import { Icon } from '@iconify/vue'
import { formatDate } from '@/utils'
import { PageWrapper, CrudTable, CrudModal, QueryBarItem } from '@/components'
import api from '@/api'

defineOptions({ name: '用户管理' })

// 响应式数据
const tableRef = ref()
const deptOptions = ref([])
const roleOptions = ref([])
const modalVisible = ref(false)
const modalAction = ref('add')

// 查询条件
const queryItems = reactive({
  username: '',
  email: '',
  status: null,
  dept_id: null,
})

// 状态选项
const statusOptions = [
  { label: '正常', value: '1' },
  { label: '禁用', value: '0' },
]

// 表单数据
const formData = reactive({
  id: null,
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
  role_ids: [],
  dept_id: null,
  is_superuser: false,
  is_active: true,
})

// 表单验证规则
const formRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '邮箱格式不正确', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' },
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    {
      validator: (rule, value) => {
        return value === formData.password
      },
      message: '两次密码输入不一致',
      trigger: 'blur',
    },
  ],
  role_ids: [
    { type: 'array', required: true, message: '请选择角色', trigger: 'change' },
  ],
}

// 表格列配置
const columns = [
  { title: '用户名', key: 'username', width: 120 },
  { title: '邮箱', key: 'email', width: 200 },
  {
    title: '角色',
    key: 'roles',
    width: 150,
    render: (row) => {
      return h('div', 
        row.roles?.map(role => 
          h(NTag, { type: 'info', size: 'small', style: 'margin: 2px' }, 
            { default: () => role.name }
          )
        ) || []
      )
    },
  },
  { title: '部门', key: 'dept.name', width: 120 },
  {
    title: '超级用户',
    key: 'is_superuser',
    width: 100,
    render: (row) => h(NTag, 
      { type: row.is_superuser ? 'success' : 'default', size: 'small' },
      { default: () => row.is_superuser ? '是' : '否' }
    ),
  },
  {
    title: '状态',
    key: 'is_active',
    width: 80,
    render: (row) => h(NTag, 
      { type: row.is_active ? 'success' : 'error', size: 'small' },
      { default: () => row.is_active ? '正常' : '禁用' }
    ),
  },
  {
    title: '最后登录',
    key: 'last_login',
    width: 160,
    render: (row) => row.last_login ? formatDate(row.last_login) : '-',
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
        h(NPopconfirm, 
          {
            onPositiveClick: () => handleDelete(row),
          },
          {
            trigger: () => h(NButton, 
              { size: 'small', type: 'error', style: 'margin-right: 8px' },
              { default: () => '删除' }
            ),
            default: () => '确定删除该用户吗？',
          }
        ),
        !row.is_superuser && h(NPopconfirm,
          {
            onPositiveClick: () => handleResetPassword(row),
          },
          {
            trigger: () => h(NButton, 
              { size: 'small', type: 'warning' },
              { default: () => '重置密码' }
            ),
            default: () => '确定重置密码为123456吗？',
          }
        ),
      ])
    },
  },
]

// 部门树节点属性
const nodeProps = ({ option }) => ({
  onClick() {
    queryForm.dept_id = option.id
    handleSearch()
  },
})

// 数据变化处理
const handleDataChange = (data) => {
  // 可以在这里处理数据变化后的逻辑
  console.log('用户数据已更新:', data.length)
}

// 获取角色列表
const getRoleList = async () => {
  try {
    const res = await api.getRoleList({ page: 1, page_size: 999 })
    roleOptions.value = res.data.items || res.data
  } catch (error) {
    console.error('获取角色列表失败:', error)
  }
}

// 获取部门列表
const getDeptList = async () => {
  try {
    const res = await api.getDepts()
    deptOptions.value = res.data
  } catch (error) {
    console.error('获取部门列表失败:', error)
  }
}

// 保存处理
const handleSave = async (formData, type) => {
  if (type === 'add') {
    await api.createUser(formData)
  } else {
    await api.updateUser(formData)
  }
}

// 保存成功处理
const handleSuccess = () => {
  tableRef.value?.handleSearch()
}

// 新增
const handleAdd = () => {
  modalAction.value = 'add'
  formData.value = {
    id: null,
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
    role_ids: [],
    dept_id: null,
    is_superuser: false,
    is_active: true,
  }
  modalVisible.value = true
}

// 编辑
const handleEdit = (row) => {
  modalAction.value = 'edit'
  formData.value = {
    id: row.id,
    username: row.username,
    email: row.email,
    password: '',
    confirmPassword: '',
    role_ids: row.roles?.map(r => r.id) || [],
    dept_id: row.dept?.id || null,
    is_superuser: row.is_superuser,
    is_active: row.is_active,
  }
  modalVisible.value = true
}



// 删除
const handleDelete = async (row) => {
  try {
    await api.deleteUser({ user_id: row.id })
    window.$message?.success('删除成功')
    tableRef.value?.handleSearch()
  } catch (error) {
    window.$message?.error('删除失败')
  }
}

// 重置密码
const handleResetPassword = async (row) => {
  try {
    await api.resetPassword({ user_id: row.id })
    window.$message?.success('密码已重置为123456')
  } catch (error) {
    window.$message?.error('重置密码失败')
  }
}

// 初始化
onMounted(() => {
  getRoleList()
  getDeptList()
})
</script>

<style scoped>
.dept-header {
  margin-bottom: 16px;
}

.dept-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 500;
}
</style>
