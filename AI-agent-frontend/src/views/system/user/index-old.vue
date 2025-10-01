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
          key-field="dept_id"
          label-field="dept_name"
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
        <NFormItem label="昵称" path="nickname">
          <NInput v-model:value="formData.nickname" placeholder="请输入昵称" />
        </NFormItem>
        <NFormItem label="邮箱" path="email">
          <NInput v-model:value="formData.email" placeholder="请输入邮箱" />
        </NFormItem>
        <NFormItem label="手机号" path="mobile">
          <NInput v-model:value="formData.mobile" placeholder="请输入手机号" />
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
                :key="role.role_id"
                :value="role.role_id"
                :label="role.role_name"
              />
            </NSpace>
          </NCheckboxGroup>
        </NFormItem>
        <NFormItem label="部门" path="dept_id">
          <NTreeSelect
            v-model:value="formData.dept_id"
            :options="deptOptions"
            key-field="dept_id"
            label-field="dept_name"
            placeholder="请选择部门"
            clearable
          />
        </NFormItem>
        <NFormItem label="状态">
          <NSwitch
            v-model:value="formData.status"
            :checked-value="1"
            :unchecked-value="0"
          />
        </NFormItem>
      </template>
    </CrudModal>
  </PageWrapper>
</template>

<script setup>
import { ref, reactive, onMounted, h } from 'vue'
import { NTag, NButton, NPopconfirm } from 'naive-ui'
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
  user_id: null,
  username: '',
  nickname: '',
  email: '',
  mobile: '',
  password: '',
  confirmPassword: '',
  role_ids: [],
  dept_id: null,
  status: 1,
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
  { title: '用户ID', key: 'user_id', width: 80 },
  { title: '用户名', key: 'username', width: 120 },
  { title: '昵称', key: 'nickname', width: 120 },
  { title: '邮箱', key: 'email', width: 200 },
  { title: '手机号', key: 'mobile', width: 120 },
  { title: '部门', key: 'dept_name', width: 120 },
  {
    title: '状态',
    key: 'status',
    width: 80,
    render: (row) => h(NTag,
      { type: row.status === 1 || row.status === '1' ? 'success' : 'error', size: 'small' },
      { default: () => row.status === 1 || row.status === '1' ? '正常' : '禁用' }
    ),
  },
  {
    title: '创建时间',
    key: 'created_at',
    width: 160,
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
        h(NPopconfirm,
          {
            onPositiveClick: () => handleResetPassword(row),
          },
          {
            trigger: () => h(NButton,
              { size: 'small', type: 'warning' },
              { default: () => '重置密码' }
            ),
            default: () => '确定重置密码吗？',
          }
        ),
      ])
    },
  },
]

// 部门树节点属性
const nodeProps = ({ option }) => ({
  onClick() {
    queryItems.dept_id = option.dept_id
    tableRef.value?.handleSearch()
  },
})

// 数据变化处理
const handleDataChange = (data) => {
  // 可以在这里处理数据变化后的逻辑
  console.log('用户数据已更新:', Array.isArray(data) ? data.length : 0)
}

// 获取角色列表
const getRoleList = async () => {
  try {
    const res = await api.getRoleList({ page: 1, page_size: 100 }) // 修复：使用最大允许值100
    if (res.code === 200 && res.data) {
      roleOptions.value = res.data.items || []
    }
  } catch (error) {
    console.error('获取角色列表失败:', error)
  }
}

// 获取部门列表
const getDeptList = async () => {
  try {
    const res = await api.getDepts()
    if (res.code === 200 && res.data) {
      deptOptions.value = Array.isArray(res.data) ? res.data : []
    } else {
      deptOptions.value = []
    }
  } catch (error) {
    console.error('获取部门列表失败:', error)
    deptOptions.value = []
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
  Object.assign(formData, {
    user_id: null,
    username: '',
    nickname: '',
    email: '',
    mobile: '',
    password: '',
    confirmPassword: '',
    role_ids: [],
    dept_id: null,
    status: 1,
  })
  modalVisible.value = true
}

// 编辑
const handleEdit = async (row) => {
  try {
    // 获取用户详情
    const res = await api.getUserById({ user_id: row.user_id })
    if (res.code === 200 && res.data) {
      modalAction.value = 'edit'
      Object.assign(formData, {
        user_id: res.data.user_id,
        username: res.data.username,
        nickname: res.data.nickname || '',
        email: res.data.email || '',
        mobile: res.data.mobile || '',
        password: '',
        confirmPassword: '',
        role_ids: res.data.role_ids || [],
        dept_id: res.data.dept_id || null,
        status: res.data.status || 1,
      })
      modalVisible.value = true
    }
  } catch (error) {
    window.$message?.error('获取用户信息失败')
  }
}

// 删除
const handleDelete = async (row) => {
  try {
    await api.deleteUser({ user_id: row.user_id })
    window.$message?.success('删除成功')
    tableRef.value?.handleSearch()
  } catch (error) {
    window.$message?.error('删除失败')
  }
}

// 重置密码
const handleResetPassword = async (row) => {
  try {
    // 弹出输入框让用户输入新密码
    const newPassword = prompt('请输入新密码（至少6位）：', '123456')
    if (!newPassword) return

    if (newPassword.length < 6) {
      window.$message?.error('密码长度不能少于6位')
      return
    }

    await api.resetPassword({ user_id: row.user_id, new_password: newPassword })
    window.$message?.success('密码重置成功')
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
