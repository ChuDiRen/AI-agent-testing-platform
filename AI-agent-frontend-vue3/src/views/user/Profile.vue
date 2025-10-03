<!-- Copyright (c) 2025 左岚. All rights reserved. -->
<template>
  <div class="profile-container">
    <el-row :gutter="20">
      <!-- 左侧：个人信息卡片 -->
      <el-col :span="8">
        <el-card class="profile-card">
          <template #header>
            <div class="card-header">
              <span>个人信息</span>
            </div>
          </template>
          
          <div class="profile-avatar-section">
            <el-upload
              class="avatar-uploader"
              :show-file-list="false"
              :before-upload="beforeAvatarUpload"
              :http-request="handleAvatarUpload"
            >
              <el-avatar :size="120" :src="userInfo.avatar || defaultAvatar" />
              <div class="avatar-overlay">
                <el-icon><Camera /></el-icon>
                <span>更换头像</span>
              </div>
            </el-upload>
            <h3 class="profile-name">{{ userInfo.nickname || userInfo.username }}</h3>
            <p class="profile-role">{{ userInfo.role_name || '普通用户' }}</p>
          </div>

          <el-descriptions :column="1" border class="profile-info">
            <el-descriptions-item label="用户名">{{ userInfo.username }}</el-descriptions-item>
            <el-descriptions-item label="邮箱">{{ userInfo.email || '未设置' }}</el-descriptions-item>
            <el-descriptions-item label="手机号">{{ userInfo.phone || '未设置' }}</el-descriptions-item>
            <el-descriptions-item label="部门">{{ userInfo.dept_name || '未分配' }}</el-descriptions-item>
            <el-descriptions-item label="账号状态">
              <el-tag :type="userInfo.status === 1 ? 'success' : 'danger'">
                {{ userInfo.status === 1 ? '正常' : '禁用' }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="注册时间">{{ userInfo.created_at }}</el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>

      <!-- 右侧：编辑区域 -->
      <el-col :span="16">
        <el-card class="edit-card">
          <template #header>
            <el-tabs v-model="activeTab">
              <el-tab-pane label="基本信息" name="basic" />
              <el-tab-pane label="安全设置" name="security" />
              <el-tab-pane label="通知设置" name="notification" />
            </el-tabs>
          </template>

          <!-- 基本信息 -->
          <div v-show="activeTab === 'basic'" class="tab-content">
            <el-form :model="basicForm" :rules="basicRules" ref="basicFormRef" label-width="100px">
              <el-form-item label="昵称" prop="nickname">
                <el-input v-model="basicForm.nickname" placeholder="请输入昵称" />
              </el-form-item>
              <el-form-item label="邮箱" prop="email">
                <el-input v-model="basicForm.email" placeholder="请输入邮箱" />
              </el-form-item>
              <el-form-item label="手机号" prop="phone">
                <el-input v-model="basicForm.phone" placeholder="请输入手机号" />
              </el-form-item>
              <el-form-item label="个人简介">
                <el-input
                  v-model="basicForm.bio"
                  type="textarea"
                  :rows="4"
                  placeholder="请输入个人简介"
                  maxlength="200"
                  show-word-limit
                />
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="handleSaveBasic" :loading="saving">保存修改</el-button>
                <el-button @click="handleResetBasic">重置</el-button>
              </el-form-item>
            </el-form>
          </div>

          <!-- 安全设置 -->
          <div v-show="activeTab === 'security'" class="tab-content">
            <el-form :model="passwordForm" :rules="passwordRules" ref="passwordFormRef" label-width="100px">
              <el-form-item label="原密码" prop="old_password">
                <el-input
                  v-model="passwordForm.old_password"
                  type="password"
                  placeholder="请输入原密码"
                  show-password
                />
              </el-form-item>
              <el-form-item label="新密码" prop="new_password">
                <el-input
                  v-model="passwordForm.new_password"
                  type="password"
                  placeholder="请输入新密码（6-20位）"
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
                <el-button type="primary" @click="handleChangePassword" :loading="saving">修改密码</el-button>
                <el-button @click="handleResetPassword">重置</el-button>
              </el-form-item>
            </el-form>

            <el-divider />

            <div class="security-list">
              <h4>安全提示</h4>
              <el-alert
                title="密码强度建议"
                type="info"
                description="密码长度至少8位，包含大小写字母、数字和特殊字符"
                :closable="false"
                style="margin-bottom: 15px"
              />
              <el-alert
                title="定期更换密码"
                type="warning"
                description="建议每3个月更换一次密码以保障账号安全"
                :closable="false"
              />
            </div>
          </div>

          <!-- 通知设置 -->
          <div v-show="activeTab === 'notification'" class="tab-content">
            <el-form label-width="150px">
              <el-form-item label="邮件通知">
                <el-switch v-model="notificationSettings.email" />
                <span class="setting-desc">接收系统邮件通知</span>
              </el-form-item>
              <el-form-item label="测试完成通知">
                <el-switch v-model="notificationSettings.test_complete" />
                <span class="setting-desc">测试执行完成时通知</span>
              </el-form-item>
              <el-form-item label="测试失败通知">
                <el-switch v-model="notificationSettings.test_failed" />
                <span class="setting-desc">测试失败时立即通知</span>
              </el-form-item>
              <el-form-item label="系统公告">
                <el-switch v-model="notificationSettings.system_announcement" />
                <span class="setting-desc">接收系统公告和重要通知</span>
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="handleSaveNotification" :loading="saving">保存设置</el-button>
              </el-form-item>
            </el-form>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, type FormInstance, type FormRules, type UploadRequestOptions } from 'element-plus'
import { Camera } from '@element-plus/icons-vue'
import { useAuthStore } from '@/store/auth'

const authStore = useAuthStore()
const activeTab = ref('basic')
const saving = ref(false)
const defaultAvatar = 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png'

// 用户信息
const userInfo = reactive({
  username: '',
  nickname: '',
  email: '',
  phone: '',
  avatar: '',
  role_name: '',
  dept_name: '',
  status: 1,
  created_at: '',
  bio: ''
})

// 基本信息表单
const basicFormRef = ref<FormInstance>()
const basicForm = reactive({
  nickname: '',
  email: '',
  phone: '',
  bio: ''
})

const basicRules: FormRules = {
  nickname: [
    { required: true, message: '请输入昵称', trigger: 'blur' },
    { min: 2, max: 20, message: '昵称长度在2-20个字符之间', trigger: 'blur' }
  ],
  email: [
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ],
  phone: [
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' }
  ]
}

// 密码表单
const passwordFormRef = ref<FormInstance>()
const passwordForm = reactive({
  old_password: '',
  new_password: '',
  confirm_password: ''
})

const validateConfirmPassword = (rule: any, value: any, callback: any) => {
  if (value === '') {
    callback(new Error('请再次输入密码'))
  } else if (value !== passwordForm.new_password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const passwordRules: FormRules = {
  old_password: [
    { required: true, message: '请输入原密码', trigger: 'blur' }
  ],
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度在6-20个字符之间', trigger: 'blur' }
  ],
  confirm_password: [
    { required: true, validator: validateConfirmPassword, trigger: 'blur' }
  ]
}

// 通知设置
const notificationSettings = reactive({
  email: true,
  test_complete: true,
  test_failed: true,
  system_announcement: true
})

// 加载用户信息
const loadUserInfo = () => {
  const user = authStore.userInfo
  if (user) {
    Object.assign(userInfo, user)
    basicForm.nickname = user.nickname || ''
    basicForm.email = user.email || ''
    basicForm.phone = user.phone || ''
    basicForm.bio = user.bio || ''
  }
}

// 保存基本信息
const handleSaveBasic = async () => {
  if (!basicFormRef.value) return

  await basicFormRef.value.validate(async (valid) => {
    if (valid) {
      saving.value = true
      try {
        // TODO: 调用API保存用户信息
        // await updateUserProfile(basicForm)
        
        // 模拟保存
        await new Promise(resolve => setTimeout(resolve, 1000))
        
        Object.assign(userInfo, basicForm)
        ElMessage.success('保存成功')
      } catch (error) {
        ElMessage.error('保存失败')
      } finally {
        saving.value = false
      }
    }
  })
}

// 重置基本信息
const handleResetBasic = () => {
  loadUserInfo()
}

// 修改密码
const handleChangePassword = async () => {
  if (!passwordFormRef.value) return

  await passwordFormRef.value.validate(async (valid) => {
    if (valid) {
      saving.value = true
      try {
        // TODO: 调用API修改密码
        // await changePassword(passwordForm)
        
        // 模拟保存
        await new Promise(resolve => setTimeout(resolve, 1000))
        
        ElMessage.success('密码修改成功，请重新登录')
        // 清空表单
        passwordFormRef.value?.resetFields()
        // 可以在这里触发重新登录
      } catch (error) {
        ElMessage.error('密码修改失败')
      } finally {
        saving.value = false
      }
    }
  })
}

// 重置密码表单
const handleResetPassword = () => {
  passwordFormRef.value?.resetFields()
}

// 保存通知设置
const handleSaveNotification = async () => {
  saving.value = true
  try {
    // TODO: 调用API保存通知设置
    // await saveNotificationSettings(notificationSettings)
    
    // 模拟保存
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    ElMessage.success('通知设置已保存')
  } catch (error) {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

// 头像上传前验证
const beforeAvatarUpload = (file: File) => {
  const isImage = file.type.startsWith('image/')
  const isLt2M = file.size / 1024 / 1024 < 2

  if (!isImage) {
    ElMessage.error('只能上传图片文件!')
    return false
  }
  if (!isLt2M) {
    ElMessage.error('图片大小不能超过 2MB!')
    return false
  }
  return true
}

// 处理头像上传
const handleAvatarUpload = async (options: UploadRequestOptions) => {
  try {
    // TODO: 调用API上传头像
    // const formData = new FormData()
    // formData.append('file', options.file)
    // const response = await uploadAvatar(formData)
    // userInfo.avatar = response.url
    
    // 模拟上传
    ElMessage.success('头像上传成功')
  } catch (error) {
    ElMessage.error('头像上传失败')
  }
}

onMounted(() => {
  loadUserInfo()
})
</script>

<style scoped>
.profile-container {
  padding: 20px;
}

.profile-card {
  margin-bottom: 20px;
}

.card-header {
  font-weight: 600;
  font-size: 16px;
}

.profile-avatar-section {
  text-align: center;
  padding: 20px 0;
}

.avatar-uploader {
  display: inline-block;
  position: relative;
  cursor: pointer;
}

.avatar-uploader:hover .avatar-overlay {
  opacity: 1;
}

.avatar-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: white;
  opacity: 0;
  transition: opacity 0.3s;
  font-size: 12px;
}

.avatar-overlay .el-icon {
  font-size: 24px;
  margin-bottom: 4px;
}

.profile-name {
  margin: 15px 0 5px 0;
  font-size: 20px;
  font-weight: 600;
}

.profile-role {
  color: #909399;
  font-size: 14px;
  margin: 0;
}

.profile-info {
  margin-top: 20px;
}

.edit-card :deep(.el-card__header) {
  padding: 0;
}

.edit-card :deep(.el-tabs__header) {
  margin: 0;
  padding: 0 20px;
}

.tab-content {
  padding: 20px;
}

.setting-desc {
  margin-left: 10px;
  color: #909399;
  font-size: 13px;
}

.security-list {
  margin-top: 20px;
}

.security-list h4 {
  margin-bottom: 15px;
  color: #303133;
}
</style>

