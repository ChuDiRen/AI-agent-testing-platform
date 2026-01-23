<template>
  <div class="users-page">
    <div class="page-header">
      <h2>用户管理</h2>
      <el-button type="primary" @click="showCreateDialog = true">
        <el-icon><Plus /></el-icon>
        添加用户
      </el-button>
    </div>

    <!-- 用户列表 -->
    <el-card class="users-card">
      <div class="table-header">
        <div class="search-box">
          <el-input
            v-model="searchQuery"
            placeholder="搜索用户..."
            :prefix-icon="Search"
            @input="handleSearch"
            clearable
            style="width: 300px"
          />
        </div>
        <div class="filters">
          <el-select
            v-model="statusFilter"
            placeholder="状态筛选"
            @change="handleFilter"
            clearable
            style="width: 120px"
          >
            <el-option label="全部" value="" />
            <el-option label="启用" value="active" />
            <el-option label="禁用" value="inactive" />
          </el-select>
          
          <el-select
            v-model="roleFilter"
            placeholder="角色筛选"
            @change="handleFilter"
            clearable
            style="width: 120px"
          >
            <el-option label="全部" value="" />
            <el-option label="管理员" value="superadmin" />
            <el-option label="部门管理员" value="dept_admin" />
            <el-option label="普通用户" value="user" />
          </el-select>
        </div>
      </div>

      <el-table
        :data="filteredUsers"
        v-loading="loading"
        stripe
        style="width: 100%"
      >
        <el-table-column prop="username" label="用户名" min-width="120" />
        
        <el-table-column prop="full_name" label="姓名" min-width="100" />
        
        <el-table-column prop="email" label="邮箱" min-width="150" show-overflow-tooltip />
        
        <el-table-column prop="department" label="部门" min-width="100" />
        
        <el-table-column prop="role" label="角色" width="100">
          <template #default="{ row }">
            <el-tag :type="getRoleType(row.role)">
              {{ getRoleText(row.role) }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="status" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'danger'" size="small">
              {{ row.status === 'active' ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="last_login" label="最后登录" width="150">
          <template #default="{ row }">
            {{ formatDate(row.last_login) }}
          </template>
        </el-table-column>
        
        <el-table-column prop="created_at" label="创建时间" width="150">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button
              size="small"
              @click="handleEditUser(row)"
              :icon="Edit"
            >
              编辑
            </el-button>
            
            <el-button
              size="small"
              :type="row.status === 'active' ? 'warning' : 'success'"
              @click="handleToggleStatus(row)"
              :loading="row.toggling"
            >
              {{ row.status === 'active' ? '禁用' : '启用' }}
            </el-button>
            
            <el-button
              size="small"
              type="danger"
              @click="handleDeleteUser(row)"
              :loading="row.deleting"
              :icon="Delete"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 创建/编辑用户对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      :title="editingUser ? '编辑用户' : '添加用户'"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="userFormRef"
        :model="userForm"
        :rules="userFormRules"
        label-width="100px"
      >
        <el-form-item label="用户名" prop="username">
          <el-input
            v-model="userForm.username"
            placeholder="请输入用户名"
            :disabled="!!editingUser"
          />
        </el-form-item>
        
        <el-form-item label="姓名" prop="full_name">
          <el-input v-model="userForm.full_name" placeholder="请输入真实姓名" />
        </el-form-item>
        
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="userForm.email" placeholder="请输入邮箱地址" />
        </el-form-item>
        
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="userForm.phone" placeholder="请输入手机号码" />
        </el-form-item>
        
        <el-form-item label="部门" prop="department">
          <el-input v-model="userForm.department" placeholder="请输入部门名称" />
        </el-form-item>
        
        <el-form-item label="职位" prop="position">
          <el-input v-model="userForm.position" placeholder="请输入职位" />
        </el-form-item>
        
        <el-form-item label="角色" prop="role">
          <el-select v-model="userForm.role" placeholder="请选择角色" style="width: 100%">
            <el-option label="普通用户" value="user" />
            <el-option label="部门管理员" value="dept_admin" />
            <el-option label="超级管理员" value="superadmin" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="密码" prop="password" v-if="!editingUser">
          <el-input
            v-model="userForm.password"
            type="password"
            placeholder="请输入密码"
            show-password
          />
        </el-form-item>
        
        <el-form-item label="确认密码" prop="confirm_password" v-if="!editingUser">
          <el-input
            v-model="userForm.confirm_password"
            type="password"
            placeholder="请再次输入密码"
            show-password
          />
        </el-form-item>
        
        <el-form-item label="状态" prop="status">
          <el-radio-group v-model="userForm.status">
            <el-radio label="active">启用</el-radio>
            <el-radio label="inactive">禁用</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="cancelUserForm">取消</el-button>
        <el-button type="primary" @click="saveUser" :loading="saving">
          {{ editingUser ? '更新' : '创建' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus,
  Search,
  Edit,
  Delete
} from '@element-plus/icons-vue'
import { getUsers, createUser, updateUser, deleteUser } from '../../api/user'

const userFormRef = ref()
const loading = ref(false)
const saving = ref(false)
const showCreateDialog = ref(false)
const editingUser = ref(null)

const users = ref([])
const searchQuery = ref('')
const statusFilter = ref('')
const roleFilter = ref('')
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

const userForm = reactive({
  username: '',
  full_name: '',
  email: '',
  phone: '',
  department: '',
  position: '',
  role: 'user',
  password: '',
  confirm_password: '',
  status: 'active'
})

const userFormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度在 3 到 20 个字符', trigger: 'blur' }
  ],
  full_name: [
    { required: true, message: '请输入姓名', trigger: 'blur' },
    { min: 2, max: 50, message: '姓名长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ],
  phone: [
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号码', trigger: 'blur' }
  ],
  role: [
    { required: true, message: '请选择角色', trigger: 'change' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度在 6 到 20 个字符', trigger: 'blur' }
  ],
  confirm_password: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== userForm.password) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

const filteredUsers = computed(() => {
  let filtered = users.value

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(user => 
      user.username.toLowerCase().includes(query) ||
      user.full_name.toLowerCase().includes(query) ||
      user.email.toLowerCase().includes(query) ||
      user.department?.toLowerCase().includes(query)
    )
  }

  if (statusFilter.value) {
    filtered = filtered.filter(user => user.status === statusFilter.value)
  }

  if (roleFilter.value) {
    filtered = filtered.filter(user => user.role === roleFilter.value)
  }

  return filtered
})

const loadUsers = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value
    }
    
    const response = await getUsers(params)
    users.value = response.data.items || []
    total.value = response.data.total || 0
  } catch (error) {
    ElMessage.error('加载用户列表失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  currentPage.value = 1
}

const handleFilter = () => {
  currentPage.value = 1
}

const handleSizeChange = (size) => {
  pageSize.value = size
  loadUsers()
}

const handleCurrentChange = (page) => {
  currentPage.value = page
  loadUsers()
}

const handleEditUser = (user) => {
  editingUser.value = user
  Object.assign(userForm, {
    username: user.username,
    full_name: user.full_name,
    email: user.email,
    phone: user.phone || '',
    department: user.department || '',
    position: user.position || '',
    role: user.role,
    status: user.status
  })
  showCreateDialog.value = true
}

const handleToggleStatus = async (user) => {
  user.toggling = true
  try {
    const newStatus = user.status === 'active' ? 'inactive' : 'active'
    await updateUser(user.id, { status: newStatus })
    user.status = newStatus
    ElMessage.success(`用户${newStatus === 'active' ? '启用' : '禁用'}成功`)
  } catch (error) {
    ElMessage.error('操作失败')
  } finally {
    user.toggling = false
  }
}

const handleDeleteUser = async (user) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除用户 "${user.full_name}" 吗？此操作不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    user.deleting = true
    await deleteUser(user.id)
    ElMessage.success('用户删除成功')
    loadUsers()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除用户失败')
    }
  } finally {
    user.deleting = false
  }
}

const saveUser = async () => {
  if (!userFormRef.value) return

  try {
    await userFormRef.value.validate()
    saving.value = true

    const userData = { ...userForm }
    delete userData.confirm_password

    if (editingUser.value) {
      delete userData.password
      await updateUser(editingUser.value.id, userData)
      ElMessage.success('用户更新成功')
    } else {
      await createUser(userData)
      ElMessage.success('用户创建成功')
    }

    showCreateDialog.value = false
    cancelUserForm()
    loadUsers()
  } catch (error) {
    ElMessage.error(editingUser.value ? '用户更新失败' : '用户创建失败')
  } finally {
    saving.value = false
  }
}

const cancelUserForm = () => {
  showCreateDialog.value = false
  editingUser.value = null
  Object.assign(userForm, {
    username: '',
    full_name: '',
    email: '',
    phone: '',
    department: '',
    position: '',
    role: 'user',
    password: '',
    confirm_password: '',
    status: 'active'
  })
  if (userFormRef.value) {
    userFormRef.value.resetFields()
  }
}

const getRoleType = (role) => {
  const types = {
    superadmin: 'danger',
    dept_admin: 'warning',
    user: 'primary'
  }
  return types[role] || 'info'
}

const getRoleText = (role) => {
  const texts = {
    superadmin: '超级管理员',
    dept_admin: '部门管理员',
    user: '普通用户'
  }
  return texts[role] || role
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleDateString('zh-CN')
}

onMounted(() => {
  loadUsers()
})
</script>

<style scoped>
.users-page {
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-header h2 {
  margin: 0;
  color: #303133;
  font-size: 24px;
  font-weight: 600;
}

.users-card {
  border: none;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  gap: 16px;
}

.filters {
  display: flex;
  gap: 12px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .users-page {
    padding: 0;
  }
  
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  
  .page-header .el-button {
    width: 100%;
  }
  
  .table-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .search-box {
    width: 100%;
  }
  
  .filters {
    width: 100%;
    justify-content: space-between;
  }
}
</style>
