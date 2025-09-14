# Copyright (c) 2025 左岚. All rights reserved.

<template>
  <div class="profile-container">
    <div class="page-header">
      <h2>个人中心</h2>
      <p>管理个人信息和账户设置</p>
    </div>

    <el-row :gutter="20">
      <!-- 左侧个人信息卡片 -->
      <el-col :span="8">
        <el-card class="profile-card">
          <template #header>
            <div class="card-header">
              <el-icon><User /></el-icon>
              <span>个人信息</span>
            </div>
          </template>
          
          <div class="profile-info">
            <div class="avatar-section">
              <el-avatar
                :src="userStore.avatar"
                :size="80"
                class="profile-avatar"
              >
                <template #default>
                  <el-icon><User /></el-icon>
                </template>
              </el-avatar>
              <el-button
                type="primary"
                size="small"
                @click="handleAvatarUpload"
                class="upload-btn"
              >
                更换头像
              </el-button>
            </div>
            
            <div class="info-list">
              <div class="info-item">
                <label>用户名：</label>
                <span>{{ userInfo?.username || '-' }}</span>
              </div>
              <div class="info-item">
                <label>邮箱：</label>
                <span>{{ userInfo?.email || '-' }}</span>
              </div>
              <div class="info-item">
                <label>手机号：</label>
                <span>{{ userInfo?.mobile || '-' }}</span>
              </div>
              <div class="info-item">
                <label>性别：</label>
                <span>{{ getSexText(userInfo?.ssex) }}</span>
              </div>
              <div class="info-item">
                <label>部门：</label>
                <span>{{ userInfo?.dept_name || '-' }}</span>
              </div>
              <div class="info-item">
                <label>状态：</label>
                <el-tag :type="userInfo?.status === '1' ? 'success' : 'danger'" size="small">
                  {{ userInfo?.status === '1' ? '启用' : '禁用' }}
                </el-tag>
              </div>
              <div class="info-item">
                <label>创建时间：</label>
                <span>{{ formatStandardDateTime(userInfo?.create_time) }}</span>
              </div>
              <div class="info-item">
                <label>最后登录：</label>
                <span>{{ formatStandardDateTime(userInfo?.last_login_time) }}</span>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 右侧操作区域 -->
      <el-col :span="16">
        <el-tabs v-model="activeTab" class="profile-tabs">
          <!-- 编辑信息 -->
          <el-tab-pane label="编辑信息" name="edit">
            <el-card>
              <el-form
                ref="formRef"
                :model="formData"
                :rules="formRules"
                label-width="100px"
                class="profile-form"
              >
                <el-row :gutter="20">
                  <el-col :span="12">
                    <el-form-item label="邮箱" prop="email">
                      <el-input v-model="formData.email" placeholder="请输入邮箱" />
                    </el-form-item>
                  </el-col>
                  <el-col :span="12">
                    <el-form-item label="手机号" prop="mobile">
                      <el-input v-model="formData.mobile" placeholder="请输入手机号" />
                    </el-form-item>
                  </el-col>
                </el-row>
                
                <el-row :gutter="20">
                  <el-col :span="12">
                    <el-form-item label="性别" prop="ssex">
                      <el-select v-model="formData.ssex" placeholder="请选择性别">
                        <el-option label="男" value="0" />
                        <el-option label="女" value="1" />
                        <el-option label="保密" value="2" />
                      </el-select>
                    </el-form-item>
                  </el-col>
                </el-row>
                
                <el-form-item label="个人描述" prop="description">
                  <el-input
                    v-model="formData.description"
                    type="textarea"
                    :rows="4"
                    placeholder="请输入个人描述"
                    maxlength="200"
                    show-word-limit
                  />
                </el-form-item>
                
                <el-form-item>
                  <el-button
                    type="primary"
                    @click="handleUpdateProfile"
                    :loading="updateLoading"
                  >
                    保存修改
                  </el-button>
                  <el-button @click="resetForm">重置</el-button>
                </el-form-item>
              </el-form>
            </el-card>
          </el-tab-pane>

          <!-- 修改密码 -->
          <el-tab-pane label="修改密码" name="password">
            <el-card>
              <el-form
                ref="passwordFormRef"
                :model="passwordForm"
                :rules="passwordRules"
                label-width="100px"
                class="password-form"
              >
                <el-form-item label="当前密码" prop="oldPassword">
                  <el-input
                    v-model="passwordForm.oldPassword"
                    type="password"
                    placeholder="请输入当前密码"
                    show-password
                  />
                </el-form-item>
                
                <el-form-item label="新密码" prop="newPassword">
                  <el-input
                    v-model="passwordForm.newPassword"
                    type="password"
                    placeholder="请输入新密码"
                    show-password
                  />
                </el-form-item>
                
                <el-form-item label="确认密码" prop="confirmPassword">
                  <el-input
                    v-model="passwordForm.confirmPassword"
                    type="password"
                    placeholder="请再次输入新密码"
                    show-password
                  />
                </el-form-item>
                
                <el-form-item>
                  <el-button
                    type="primary"
                    @click="handleChangePassword"
                    :loading="passwordLoading"
                  >
                    修改密码
                  </el-button>
                  <el-button @click="resetPasswordForm">重置</el-button>
                </el-form-item>
              </el-form>
            </el-card>
          </el-tab-pane>
        </el-tabs>
      </el-col>
    </el-row>

    <!-- 头像上传对话框 -->
    <el-dialog
      v-model="avatarDialogVisible"
      title="更换头像"
      width="400px"
      :before-close="handleCloseAvatarDialog"
    >
      <div class="avatar-upload">
        <el-upload
          ref="uploadRef"
          :auto-upload="false"
          :show-file-list="false"
          :before-upload="beforeAvatarUpload"
          accept="image/*"
          drag
        >
          <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
          <div class="el-upload__text">
            将文件拖到此处，或<em>点击上传</em>
          </div>
          <template #tip>
            <div class="el-upload__tip">
              只能上传jpg/png文件，且不超过2MB
            </div>
          </template>
        </el-upload>
      </div>

      <template #footer>
        <el-button @click="avatarDialogVisible = false">取消</el-button>
        <el-button
          type="primary"
          @click="handleUploadAvatar"
          :loading="avatarUploading"
        >
          上传
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { User, UploadFilled } from '@element-plus/icons-vue'
import { useUserStore } from '@/store'
import { UserApi } from '@/api/modules/user'
import { formatStandardDateTime } from '@/utils/dateFormat'
import { getToken } from '@/utils/auth'
import type { UserInfo } from '@/api/types'

const userStore = useUserStore()

// 响应式数据
const activeTab = ref('edit')
const userInfo = ref<UserInfo | null>(null)
const updateLoading = ref(false)
const passwordLoading = ref(false)
const avatarDialogVisible = ref(false)
const avatarUploading = ref(false)
const selectedAvatarFile = ref<File | null>(null)

// 表单引用
const formRef = ref()
const passwordFormRef = ref()
const uploadRef = ref()

// 个人信息表单
const formData = reactive({
  email: '',
  mobile: '',
  ssex: '',
  description: ''
})

// 密码表单
const passwordForm = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

// 删除不再需要的上传配置

// 性别文本转换
const getSexText = (sex?: string) => {
  const sexMap: Record<string, string> = {
    '0': '男',
    '1': '女',
    '2': '保密'
  }
  return sexMap[sex || ''] || '未知'
}

// 表单验证规则
const formRules = {
  email: [
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  mobile: [
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' }
  ]
}

const passwordRules = {
  oldPassword: [
    { required: true, message: '请输入当前密码', trigger: 'blur' }
  ],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    {
      validator: (rule: any, value: string, callback: Function) => {
        if (value !== passwordForm.newPassword) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

// 加载用户信息
const loadUserInfo = async () => {
  try {
    const userId = userStore.userInfo?.user_id
    if (!userId) return
    
    const response = await UserApi.getUserById(userId)
    if (response.success && response.data) {
      userInfo.value = response.data
      
      // 填充表单数据
      Object.assign(formData, {
        email: response.data.email || '',
        mobile: response.data.mobile || '',
        ssex: response.data.ssex || '',
        description: response.data.description || ''
      })
    }
  } catch (error) {
    console.error('加载用户信息失败:', error)
    ElMessage.error('加载用户信息失败')
  }
}

// 更新个人信息
const handleUpdateProfile = async () => {
  try {
    await formRef.value?.validate()
    
    updateLoading.value = true
    const userId = userStore.userInfo?.user_id
    if (!userId) return
    
    const response = await UserApi.updateUser(userId, formData)
    if (response.success) {
      ElMessage.success('个人信息更新成功')
      await loadUserInfo()
      // 更新store中的用户信息
      await userStore.getUserInfo()
    }
  } catch (error) {
    console.error('更新个人信息失败:', error)
    ElMessage.error('更新个人信息失败')
  } finally {
    updateLoading.value = false
  }
}

// 修改密码
const handleChangePassword = async () => {
  try {
    await passwordFormRef.value?.validate()
    
    passwordLoading.value = true
    const userId = userStore.userInfo?.user_id
    if (!userId) return
    
    const response = await UserApi.changePassword(userId, {
      old_password: passwordForm.oldPassword,
      new_password: passwordForm.newPassword
    })
    
    if (response.success) {
      ElMessage.success('密码修改成功')
      resetPasswordForm()
    }
  } catch (error) {
    console.error('修改密码失败:', error)
    ElMessage.error('修改密码失败')
  } finally {
    passwordLoading.value = false
  }
}

// 重置表单
const resetForm = () => {
  formRef.value?.resetFields()
  loadUserInfo()
}

const resetPasswordForm = () => {
  passwordFormRef.value?.resetFields()
  Object.assign(passwordForm, {
    oldPassword: '',
    newPassword: '',
    confirmPassword: ''
  })
}

// 头像上传相关
const handleAvatarUpload = () => {
  avatarDialogVisible.value = true
}

const handleCloseAvatarDialog = () => {
  avatarDialogVisible.value = false
}

const beforeAvatarUpload = (file: File) => {
  const isImage = file.type.startsWith('image/')
  const isLt2M = file.size / 1024 / 1024 < 2

  if (!isImage) {
    ElMessage.error('只能上传图片文件!')
    return false
  }
  if (!isLt2M) {
    ElMessage.error('上传头像图片大小不能超过 2MB!')
    return false
  }

  selectedAvatarFile.value = file
  return false // 阻止自动上传
}

const handleUploadAvatar = async () => {
  if (!selectedAvatarFile.value) {
    ElMessage.warning('请先选择头像文件')
    return
  }

  try {
    avatarUploading.value = true
    const response = await UserApi.uploadAvatar(selectedAvatarFile.value)

    if (response.success) {
      ElMessage.success('头像上传成功')
      avatarDialogVisible.value = false
      selectedAvatarFile.value = null
      await loadUserInfo()
      await userStore.getUserInfo()
    }
  } catch (error) {
    console.error('头像上传失败:', error)
    ElMessage.error('头像上传失败')
  } finally {
    avatarUploading.value = false
  }
}

// 初始化
onMounted(() => {
  loadUserInfo()
})
</script>

<style scoped lang="scss">
.profile-container {
  padding: 20px;
  
  .page-header {
    margin-bottom: 20px;
    
    h2 {
      margin: 0 0 8px 0;
      color: #2c3e50;
      font-size: 24px;
      font-weight: 600;
    }
    
    p {
      margin: 0;
      color: #7f8c8d;
      font-size: 14px;
    }
  }
  
  .profile-card {
    .card-header {
      display: flex;
      align-items: center;
      gap: 8px;
      font-weight: 600;
      color: #2c3e50;
    }
    
    .profile-info {
      .avatar-section {
        text-align: center;
        margin-bottom: 30px;
        
        .profile-avatar {
          margin-bottom: 15px;
          border: 3px solid #e4e7ed;
        }
        
        .upload-btn {
          font-size: 12px;
        }
      }
      
      .info-list {
        .info-item {
          display: flex;
          margin-bottom: 16px;
          
          label {
            min-width: 80px;
            font-weight: 500;
            color: #606266;
          }
          
          span {
            color: #2c3e50;
            flex: 1;
          }
        }
      }
    }
  }
  
  .profile-tabs {
    :deep(.el-tabs__header) {
      margin-bottom: 20px;
    }
    
    .profile-form,
    .password-form {
      max-width: 600px;
      
      .el-form-item {
        margin-bottom: 24px;
      }
      
      .el-select {
        width: 100%;
      }
    }
  }
  
  .avatar-upload {
    text-align: center;
    
    :deep(.el-upload-dragger) {
      width: 300px;
      height: 180px;
    }
  }
}

// 响应式设计
@media (max-width: 1200px) {
  .profile-container {
    :deep(.el-col-8) {
      width: 100%;
      margin-bottom: 20px;
    }
    
    :deep(.el-col-16) {
      width: 100%;
    }
  }
}

@media (max-width: 768px) {
  .profile-container {
    padding: 10px;
    
    .profile-form,
    .password-form {
      :deep(.el-col-12) {
        width: 100%;
      }
    }
  }
}
</style>
