<template>
  <div class="profile-container">
    <el-card class="profile-card">
      <template #header>
        <div class="card-header">
          <h3>个人信息</h3>
          <el-button type="primary" @click="editMode = !editMode">
            {{ editMode ? '取消' : '编辑' }}
          </el-button>
        </div>
      </template>

      <el-form
        ref="formRef"
        :model="profileForm"
        :rules="formRules"
        label-width="100px"
        :disabled="!editMode"
      >
        <el-form-item label="头像">
          <div class="avatar-section">
            <el-avatar :size="80" :src="profileForm.avatar">
              <el-icon><UserFilled /></el-icon>
            </el-avatar>
            <div v-if="editMode" class="avatar-upload">
              <el-button size="small" type="primary">上传头像</el-button>
              <div class="upload-tip">支持 JPG、PNG 格式，大小不超过 2MB</div>
            </div>
          </div>
        </el-form-item>

        <el-form-item label="用户名" prop="username">
          <el-input v-model="profileForm.username" :disabled="true" />
        </el-form-item>

        <el-form-item label="姓名" prop="full_name">
          <el-input v-model="profileForm.full_name" placeholder="请输入您的真实姓名" />
        </el-form-item>

        <el-form-item label="邮箱" prop="email">
          <el-input v-model="profileForm.email" placeholder="请输入邮箱地址" />
        </el-form-item>

        <el-form-item label="手机号" prop="phone">
          <el-input v-model="profileForm.phone" placeholder="请输入手机号码" />
        </el-form-item>

        <el-form-item label="部门">
          <el-input v-model="profileForm.department" :disabled="true" />
        </el-form-item>

        <el-form-item label="职位">
          <el-input v-model="profileForm.position" placeholder="请输入您的职位" />
        </el-form-item>

        <el-form-item label="个人简介">
          <el-input
            v-model="profileForm.bio"
            type="textarea"
            :rows="3"
            placeholder="请简单介绍一下自己"
          />
        </el-form-item>

        <el-form-item v-if="editMode">
          <el-button type="primary" @click="saveProfile" :loading="saving">
            保存
          </el-button>
          <el-button @click="cancelEdit">取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 修改密码 -->
    <el-card class="password-card">
      <template #header>
        <h3>修改密码</h3>
      </template>

      <el-form
        ref="passwordFormRef"
        :model="passwordForm"
        :rules="passwordRules"
        label-width="100px"
      >
        <el-form-item label="当前密码" prop="current_password">
          <el-input
            v-model="passwordForm.current_password"
            type="password"
            placeholder="请输入当前密码"
            show-password
          />
        </el-form-item>

        <el-form-item label="新密码" prop="new_password">
          <el-input
            v-model="passwordForm.new_password"
            type="password"
            placeholder="请输入新密码"
            show-password
          />
        </el-form-item>

        <el-form-item label="确认密码" prop="confirm_password">
          <el-input
            v-model="passwordForm.confirm_password"
            type="password"
            placeholder="请再次输入新密码"
            show-password
          />
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            @click="changePassword"
            :loading="changingPassword"
          >
            修改密码
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 账户信息 -->
    <el-card class="account-card">
      <template #header>
        <h3>账户信息</h3>
      </template>

      <div class="account-info">
        <div class="info-item">
          <span class="label">账户ID：</span>
          <span class="value">{{ authStore.user?.id }}</span>
        </div>
        <div class="info-item">
          <span class="label">用户角色：</span>
          <el-tag :type="authStore.isAdmin ? 'danger' : 'primary'">
            {{ authStore.isAdmin ? '管理员' : '普通用户' }}
          </el-tag>
        </div>
        <div class="info-item">
          <span class="label">注册时间：</span>
          <span class="value">{{ formatDate(authStore.user?.created_at) }}</span>
        </div>
        <div class="info-item">
          <span class="label">最后登录：</span>
          <span class="value">{{ formatDate(authStore.user?.last_login) }}</span>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { UserFilled } from '@element-plus/icons-vue'
import { useAuthStore } from '../store/auth'
import { updateUser, changePassword as changePasswordApi } from '../api/user'

const authStore = useAuthStore()

const formRef = ref()
const passwordFormRef = ref()
const editMode = ref(false)
const saving = ref(false)
const changingPassword = ref(false)

const profileForm = reactive({
  username: '',
  full_name: '',
  email: '',
  phone: '',
  department: '',
  position: '',
  bio: '',
  avatar: ''
})

const originalProfile = { ...profileForm }

const passwordForm = reactive({
  current_password: '',
  new_password: '',
  confirm_password: ''
})

const formRules = {
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
  ]
}

const passwordRules = {
  current_password: [
    { required: true, message: '请输入当前密码', trigger: 'blur' }
  ],
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度在 6 到 20 个字符', trigger: 'blur' }
  ],
  confirm_password: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== passwordForm.new_password) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

const loadProfile = () => {
  const user = authStore.user
  if (user) {
    Object.assign(profileForm, {
      username: user.username || '',
      full_name: user.full_name || '',
      email: user.email || '',
      phone: user.phone || '',
      department: user.department || '',
      position: user.position || '',
      bio: user.bio || '',
      avatar: user.avatar || ''
    })
    Object.assign(originalProfile, profileForm)
  }
}

const saveProfile = async () => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()
    saving.value = true

    const response = await updateUser(authStore.user.id, profileForm)
    
    if (response.success) {
      // 更新store中的用户信息
      authStore.updateUser(profileForm)
      editMode.value = false
      ElMessage.success('个人信息保存成功')
    } else {
      ElMessage.error(response.message || '保存失败')
    }
  } catch (error) {
    console.error('保存个人信息失败:', error)
    ElMessage.error('保存失败，请稍后重试')
  } finally {
    saving.value = false
  }
}

const cancelEdit = () => {
  Object.assign(profileForm, originalProfile)
  editMode.value = false
  if (formRef.value) {
    formRef.value.clearValidate()
  }
}

const changePassword = async () => {
  if (!passwordFormRef.value) return

  try {
    await passwordFormRef.value.validate()
    changingPassword.value = true

    const response = await changePasswordApi(authStore.user.id, {
      current_password: passwordForm.current_password,
      new_password: passwordForm.new_password
    })

    if (response.success) {
      ElMessage.success('密码修改成功')
      // 清空表单
      Object.assign(passwordForm, {
        current_password: '',
        new_password: '',
        confirm_password: ''
      })
      if (passwordFormRef.value) {
        passwordFormRef.value.resetFields()
      }
    } else {
      ElMessage.error(response.message || '密码修改失败')
    }
  } catch (error) {
    console.error('修改密码失败:', error)
    ElMessage.error('修改密码失败，请稍后重试')
  } finally {
    changingPassword.value = false
  }
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

onMounted(() => {
  loadProfile()
})
</script>

<style scoped>
.profile-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.profile-card,
.password-card,
.account-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h3 {
  margin: 0;
  color: #303133;
}

.avatar-section {
  display: flex;
  align-items: center;
  gap: 20px;
}

.avatar-upload {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.upload-tip {
  font-size: 12px;
  color: #999;
}

.account-info {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.info-item .label {
  color: #606266;
  min-width: 80px;
}

.info-item .value {
  color: #303133;
}

@media (max-width: 768px) {
  .profile-container {
    padding: 16px;
  }
  
  .avatar-section {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .info-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 4px;
  }
  
  .info-item .label {
    min-width: auto;
  }
}
</style>
