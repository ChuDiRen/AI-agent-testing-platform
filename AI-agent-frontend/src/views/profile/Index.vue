# Copyright (c) 2025 左岚. All rights reserved.

<template>
  <div class="profile-container">
    <!-- 顶部横幅 -->
    <div class="profile-banner">
      <div class="banner-background">
        <div class="banner-overlay"></div>
      </div>
      <div class="banner-content">
        <div class="user-avatar-section">
          <div class="avatar-wrapper">
            <el-avatar
              :src="avatarUrl"
              :size="120"
              class="main-avatar"
            >
              <template #default>
                <el-icon><User /></el-icon>
              </template>
            </el-avatar>
            <div class="avatar-badge">
              <el-button
                type="primary"
                size="small"
                circle
                @click="handleAvatarUpload"
                class="change-avatar-btn"
              >
                <el-icon><Camera /></el-icon>
              </el-button>
            </div>
          </div>
          <div class="user-basic-info">
            <h2 class="username">{{ userInfo?.username || '用户' }}</h2>
            <p class="user-title">{{ userInfo?.dept_name || '系统管理员' }}</p>
            <div class="user-status">
              <el-tag
                :type="userInfo?.status === '1' ? 'success' : 'danger'"
                size="small"
                effect="light"
              >
                <el-icon><CircleCheck v-if="userInfo?.status === '1'" /><CircleClose v-else /></el-icon>
                {{ userInfo?.status === '1' ? '在线' : '离线' }}
              </el-tag>
            </div>
          </div>
        </div>
        <div class="user-stats">
          <div class="stat-item">
            <div class="stat-value">{{ formatJoinDays(userInfo?.create_time) }}</div>
            <div class="stat-label">加入天数</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ formatLastLogin(userInfo?.last_login_time) }}</div>
            <div class="stat-label">最后登录</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 主要内容区域 -->
    <div class="profile-content">
      <el-row :gutter="24">
        <!-- 左侧信息卡片 -->
        <el-col :span="10">
          <div class="info-cards">
            <!-- 个人信息卡片 -->
            <el-card class="info-card" shadow="hover">
              <template #header>
                <div class="card-header">
                  <div class="header-icon">
                    <el-icon><User /></el-icon>
                  </div>
                  <span class="header-title">个人信息</span>
                </div>
              </template>

              <div class="info-list">
                <div class="info-item">
                  <div class="info-icon">
                    <el-icon><Message /></el-icon>
                  </div>
                  <div class="info-content">
                    <div class="info-label">邮箱地址</div>
                    <div class="info-value">{{ userInfo?.email || '-' }}</div>
                  </div>
                </div>
                <div class="info-item">
                  <div class="info-icon">
                    <el-icon><Phone /></el-icon>
                  </div>
                  <div class="info-content">
                    <div class="info-label">手机号码</div>
                    <div class="info-value">{{ userInfo?.mobile || '-' }}</div>
                  </div>
                </div>
                <div class="info-item">
                  <div class="info-icon">
                    <el-icon><Male v-if="userInfo?.ssex === '0'" /><Female v-else /></el-icon>
                  </div>
                  <div class="info-content">
                    <div class="info-label">性别</div>
                    <div class="info-value">{{ getSexText(userInfo?.ssex) }}</div>
                  </div>
                </div>
                <div class="info-item">
                  <div class="info-icon">
                    <el-icon><Calendar /></el-icon>
                  </div>
                  <div class="info-content">
                    <div class="info-label">注册时间</div>
                    <div class="info-value">{{ formatStandardDateTime(userInfo?.create_time) }}</div>
                  </div>
                </div>
              </div>
            </el-card>
          </div>
        </el-col>

        <!-- 右侧操作区域 -->
        <el-col :span="14">
          <el-card class="operation-card" shadow="hover">
            <el-tabs v-model="activeTab" class="profile-tabs">
              <!-- 编辑信息 -->
              <el-tab-pane name="edit">
                <template #label>
                  <div class="tab-label">
                    <el-icon><Edit /></el-icon>
                    <span>编辑信息</span>
                  </div>
                </template>

                <div class="form-container">
                  <div class="form-header">
                    <h3>基本信息设置</h3>
                    <p>更新您的个人基本信息</p>
                  </div>

                  <el-form
                    ref="formRef"
                    :model="formData"
                    :rules="formRules"
                    label-width="120px"
                    class="profile-form"
                  >
                    <el-row :gutter="24">
                      <el-col :span="12">
                        <el-form-item label="邮箱地址" prop="email">
                          <el-input
                            v-model="formData.email"
                            placeholder="请输入邮箱地址"
                            prefix-icon="Message"
                          />
                        </el-form-item>
                      </el-col>
                      <el-col :span="12">
                        <el-form-item label="手机号码" prop="mobile">
                          <el-input
                            v-model="formData.mobile"
                            placeholder="请输入手机号码"
                            prefix-icon="Phone"
                          />
                        </el-form-item>
                      </el-col>
                    </el-row>

                    <el-row :gutter="24">
                      <el-col :span="12">
                        <el-form-item label="性别" prop="ssex">
                          <el-select
                            v-model="formData.ssex"
                            placeholder="请选择性别"
                            style="width: 100%"
                          >
                            <el-option label="男" value="0">
                              <div class="option-item">
                                <el-icon><Male /></el-icon>
                                <span>男</span>
                              </div>
                            </el-option>
                            <el-option label="女" value="1">
                              <div class="option-item">
                                <el-icon><Female /></el-icon>
                                <span>女</span>
                              </div>
                            </el-option>
                            <el-option label="保密" value="2">
                              <div class="option-item">
                                <el-icon><Hide /></el-icon>
                                <span>保密</span>
                              </div>
                            </el-option>
                          </el-select>
                        </el-form-item>
                      </el-col>
                    </el-row>

                    <el-form-item label="个人描述" prop="description">
                      <el-input
                        v-model="formData.description"
                        type="textarea"
                        :rows="4"
                        placeholder="请输入个人描述，让大家更好地了解您..."
                        maxlength="200"
                        show-word-limit
                        resize="none"
                      />
                    </el-form-item>

                    <el-form-item class="form-actions">
                      <el-button
                        type="primary"
                        @click="handleUpdateProfile"
                        :loading="updateLoading"
                        size="large"
                      >
                        <el-icon><Check /></el-icon>
                        保存修改
                      </el-button>
                      <el-button @click="resetForm" size="large">
                        <el-icon><RefreshLeft /></el-icon>
                        重置
                      </el-button>
                    </el-form-item>
                  </el-form>
                </div>
              </el-tab-pane>

              <!-- 修改密码 -->
              <el-tab-pane name="password">
                <template #label>
                  <div class="tab-label">
                    <el-icon><Lock /></el-icon>
                    <span>修改密码</span>
                  </div>
                </template>

                <div class="form-container">
                  <div class="form-header">
                    <h3>密码安全设置</h3>
                    <p>定期更换密码，保护账户安全</p>
                  </div>

                  <el-form
                    ref="passwordFormRef"
                    :model="passwordForm"
                    :rules="passwordRules"
                    label-width="120px"
                    class="password-form"
                  >
                    <el-form-item label="当前密码" prop="oldPassword">
                      <el-input
                        v-model="passwordForm.oldPassword"
                        type="password"
                        placeholder="请输入当前密码"
                        show-password
                        prefix-icon="Lock"
                      />
                    </el-form-item>

                    <el-form-item label="新密码" prop="newPassword">
                      <el-input
                        v-model="passwordForm.newPassword"
                        type="password"
                        placeholder="请输入新密码（至少6位）"
                        show-password
                        prefix-icon="Key"
                      />
                    </el-form-item>

                    <el-form-item label="确认密码" prop="confirmPassword">
                      <el-input
                        v-model="passwordForm.confirmPassword"
                        type="password"
                        placeholder="请再次输入新密码"
                        show-password
                        prefix-icon="Key"
                      />
                    </el-form-item>

                    <el-form-item class="form-actions">
                      <el-button
                        type="primary"
                        @click="handleChangePassword"
                        :loading="passwordLoading"
                        size="large"
                      >
                        <el-icon><Check /></el-icon>
                        修改密码
                      </el-button>
                      <el-button @click="resetPasswordForm" size="large">
                        <el-icon><RefreshLeft /></el-icon>
                        重置
                      </el-button>
                    </el-form-item>
                  </el-form>
                </div>
              </el-tab-pane>
            </el-tabs>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 头像上传对话框 -->
    <el-dialog
      v-model="avatarDialogVisible"
      title=""
      width="480px"
      :before-close="handleCloseAvatarDialog"
      class="avatar-upload-dialog"
      align-center
    >
      <template #header>
        <div class="dialog-header">
          <div class="header-icon">
            <el-icon><Camera /></el-icon>
          </div>
          <div class="header-content">
            <h3>更换头像</h3>
            <p>选择一张图片作为您的新头像</p>
          </div>
        </div>
      </template>

      <div class="avatar-upload-content">
        <!-- 当前头像预览 -->
        <div class="current-avatar">
          <div class="avatar-wrapper">
            <el-avatar
              :src="avatarUrl"
              :size="100"
              class="current-avatar-img"
            >
              <template #default>
                <el-icon><User /></el-icon>
              </template>
            </el-avatar>
            <div class="avatar-overlay">
              <el-icon><Camera /></el-icon>
            </div>
          </div>
          <p class="avatar-label">当前头像</p>
        </div>

        <!-- 上传区域 -->
        <div class="upload-section">
          <el-upload
            ref="uploadRef"
            :auto-upload="false"
            :show-file-list="false"
            :on-change="handleFileChange"
            :http-request="() => {}"
            accept="image/*"
            drag
            class="avatar-uploader"
          >
            <div v-if="!selectedAvatarFile" class="upload-area">
              <div class="upload-icon">
                <el-icon><Plus /></el-icon>
              </div>
              <div class="upload-text">
                <p class="main-text">点击或拖拽上传新头像</p>
                <p class="sub-text">支持 JPG、PNG 格式，文件大小不超过 2MB</p>
              </div>
            </div>
            <div v-else class="preview-area">
              <div class="preview-wrapper">
                <img :src="previewUrl" alt="预览图片" class="preview-img" />
                <div class="preview-overlay">
                  <el-button
                    type="primary"
                    size="small"
                    circle
                    @click.stop="clearSelectedFile"
                  >
                    <el-icon><RefreshLeft /></el-icon>
                  </el-button>
                </div>
              </div>
              <div class="file-details">
                <p class="file-name">{{ selectedAvatarFile.name }}</p>
                <p class="file-size">{{ formatFileSize(selectedAvatarFile.size) }}</p>
                <el-tag type="success" size="small">
                  <el-icon><Check /></el-icon>
                  已选择
                </el-tag>
              </div>
            </div>
          </el-upload>
        </div>
      </div>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="avatarDialogVisible = false" size="large">
            取消
          </el-button>
          <el-button
            type="primary"
            @click="handleUploadAvatar"
            :loading="avatarUploading"
            :disabled="!selectedAvatarFile"
            size="large"
          >
            <el-icon v-if="!avatarUploading"><Upload /></el-icon>
            {{ avatarUploading ? '上传中...' : '确认上传' }}
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  User,
  UploadFilled,
  Camera,
  Plus,
  RefreshLeft,
  Check,
  Upload,
  Edit,
  Lock,
  Message,
  Phone,
  Male,
  Female,
  Hide,
  Calendar,
  CircleCheck,
  CircleClose,
  Key
} from '@element-plus/icons-vue'
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
const avatarTimestamp = ref(Date.now())
const previewUrl = ref('')

// 计算属性
const avatarUrl = computed(() => {
  const avatar = userInfo.value?.avatar || userStore.avatar
  if (!avatar) return ''
  // 添加时间戳避免缓存问题
  const separator = avatar.includes('?') ? '&' : '?'
  return `${avatar}${separator}t=${avatarTimestamp.value}`
})

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

// 计算加入天数
const formatJoinDays = (createTime?: string) => {
  if (!createTime) return '0'
  const now = new Date()
  const create = new Date(createTime)
  const diffTime = Math.abs(now.getTime() - create.getTime())
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  return diffDays.toString()
}

// 格式化最后登录时间
const formatLastLogin = (lastLoginTime?: string) => {
  if (!lastLoginTime) return '从未登录'
  const now = new Date()
  const lastLogin = new Date(lastLoginTime)
  const diffTime = Math.abs(now.getTime() - lastLogin.getTime())
  const diffMinutes = Math.floor(diffTime / (1000 * 60))
  const diffHours = Math.floor(diffTime / (1000 * 60 * 60))
  const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24))

  if (diffMinutes < 60) {
    return `${diffMinutes}分钟前`
  } else if (diffHours < 24) {
    return `${diffHours}小时前`
  } else {
    return `${diffDays}天前`
  }
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
  clearSelectedFile()
}

const handleFileChange = (file: any) => {
  const rawFile = file.raw
  if (!rawFile) return

  const isImage = rawFile.type.startsWith('image/')
  const isLt2M = rawFile.size / 1024 / 1024 < 2

  if (!isImage) {
    ElMessage.error('只能上传图片文件!')
    return
  }
  if (!isLt2M) {
    ElMessage.error('上传头像图片大小不能超过 2MB!')
    return
  }

  selectedAvatarFile.value = rawFile

  // 创建预览URL
  const reader = new FileReader()
  reader.onload = (e) => {
    previewUrl.value = e.target?.result as string
  }
  reader.readAsDataURL(rawFile)

  ElMessage.success('文件选择成功，点击上传按钮开始上传')
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
      clearSelectedFile()
      // 更新时间戳强制刷新头像
      avatarTimestamp.value = Date.now()
      userStore.updateAvatarTimestamp()
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

// 清除选择的文件
const clearSelectedFile = () => {
  selectedAvatarFile.value = null
  previewUrl.value = ''
  // 清除上传组件的文件列表
  if (uploadRef.value) {
    uploadRef.value.clearFiles()
  }
}

// 格式化文件大小
const formatFileSize = (bytes: number) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// 初始化
onMounted(() => {
  loadUserInfo()
})
</script>

<style scoped lang="scss">
.profile-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);

  // 顶部横幅样式
  .profile-banner {
    position: relative;
    height: 280px;
    margin: -20px -20px 24px -20px;
    border-radius: 0 0 24px 24px;
    overflow: hidden;

    .banner-background {
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);

      .banner-overlay {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.1);
      }
    }

    .banner-content {
      position: relative;
      z-index: 2;
      display: flex;
      align-items: center;
      justify-content: space-between;
      height: 100%;
      padding: 40px 48px;
      color: white;

      .user-avatar-section {
        display: flex;
        align-items: center;
        gap: 24px;

        .avatar-wrapper {
          position: relative;

          .main-avatar {
            border: 4px solid rgba(255, 255, 255, 0.3);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
          }

          .avatar-badge {
            position: absolute;
            bottom: 8px;
            right: 8px;

            .change-avatar-btn {
              background: rgba(255, 255, 255, 0.9);
              border: none;
              color: #667eea;
              box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);

              &:hover {
                background: white;
                transform: scale(1.1);
              }
            }
          }
        }

        .user-basic-info {
          .username {
            margin: 0 0 8px 0;
            font-size: 32px;
            font-weight: 700;
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
          }

          .user-title {
            margin: 0 0 12px 0;
            font-size: 16px;
            opacity: 0.9;
          }

          .user-status {
            .el-tag {
              background: rgba(255, 255, 255, 0.2);
              border: 1px solid rgba(255, 255, 255, 0.3);
              color: white;

              .el-icon {
                margin-right: 4px;
              }
            }
          }
        }
      }

      .user-stats {
        display: flex;
        gap: 32px;

        .stat-item {
          text-align: center;

          .stat-value {
            font-size: 28px;
            font-weight: 700;
            margin-bottom: 4px;
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
          }

          .stat-label {
            font-size: 14px;
            opacity: 0.8;
          }
        }
      }
    }
  }

  // 主要内容区域
  .profile-content {
    padding: 0 24px 24px;

    .info-cards {
      display: flex;
      flex-direction: column;
      gap: 24px;

      .info-card {
        border-radius: 16px;
        border: none;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        transition: all 0.3s ease;

        &:hover {
          transform: translateY(-4px);
          box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
        }

        :deep(.el-card__header) {
          padding: 20px 24px;
          border-bottom: 1px solid #f0f0f0;
          background: linear-gradient(135deg, #f8f9ff 0%, #f0f4ff 100%);
        }

        :deep(.el-card__body) {
          padding: 24px;
        }

        .card-header {
          display: flex;
          align-items: center;
          gap: 12px;

          .header-icon {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;

            .el-icon {
              font-size: 18px;
            }


          }

          .header-title {
            font-size: 16px;
            font-weight: 600;
            color: #2c3e50;
          }
        }

        .info-list {
          .info-item {
            display: flex;
            align-items: center;
            padding: 16px 0;
            border-bottom: 1px solid #f5f5f5;

            &:last-child {
              border-bottom: none;
            }

            .info-icon {
              width: 36px;
              height: 36px;
              border-radius: 50%;
              background: #f8f9ff;
              display: flex;
              align-items: center;
              justify-content: center;
              margin-right: 16px;

              .el-icon {
                font-size: 16px;
                color: #667eea;
              }
            }

            .info-content {
              flex: 1;

              .info-label {
                font-size: 12px;
                color: #909399;
                margin-bottom: 4px;
              }

              .info-value {
                font-size: 14px;
                color: #2c3e50;
                font-weight: 500;
              }
            }
          }
        }


      }
    }

    .operation-card {
      border-radius: 16px;
      border: none;
      box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);

      :deep(.el-card__body) {
        padding: 0;
      }

      .profile-tabs {
        :deep(.el-tabs__header) {
          margin: 0;
          padding: 0 24px;
          background: linear-gradient(135deg, #f8f9ff 0%, #f0f4ff 100%);
          border-radius: 16px 16px 0 0;
        }

        :deep(.el-tabs__nav-wrap) {
          padding: 20px 0;
        }

        :deep(.el-tabs__item) {
          font-weight: 500;

          &.is-active {
            color: #667eea;
          }
        }

        :deep(.el-tabs__active-bar) {
          background: #667eea;
        }

        .tab-label {
          display: flex;
          align-items: center;
          gap: 8px;

          .el-icon {
            font-size: 16px;
          }
        }

        .form-container {
          padding: 32px;

          .form-header {
            margin-bottom: 32px;
            text-align: center;

            h3 {
              margin: 0 0 8px 0;
              font-size: 20px;
              font-weight: 600;
              color: #2c3e50;
            }

            p {
              margin: 0;
              font-size: 14px;
              color: #909399;
            }
          }

          .profile-form,
          .password-form {
            .el-form-item {
              margin-bottom: 24px;

              :deep(.el-form-item__label) {
                font-weight: 500;
                color: #606266;
              }

              :deep(.el-input__wrapper) {
                border-radius: 8px;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
                transition: all 0.3s ease;

                &:hover {
                  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
                }

                &.is-focus {
                  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
                }
              }

              :deep(.el-textarea__inner) {
                border-radius: 8px;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
                transition: all 0.3s ease;

                &:hover {
                  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
                }

                &:focus {
                  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
                }
              }

              :deep(.el-select) {
                width: 100%;

                .el-input__wrapper {
                  border-radius: 8px;
                }
              }
            }

            .form-actions {
              margin-top: 40px;
              text-align: center;

              .el-button {
                border-radius: 8px;
                padding: 12px 32px;
                font-weight: 500;

                &.el-button--primary {
                  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                  border: none;

                  &:hover {
                    background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%);
                  }
                }
              }
            }
          }

          .option-item {
            display: flex;
            align-items: center;
            gap: 8px;

            .el-icon {
              font-size: 14px;
            }
          }
        }
      }
    }
  }
  
  // 头像上传对话框样式
  :deep(.avatar-upload-dialog) {
    .el-dialog__header {
      padding: 0;
      border-bottom: 1px solid #f0f0f0;
    }

    .el-dialog__body {
      padding: 24px;
    }

    .el-dialog__footer {
      padding: 16px 24px;
      border-top: 1px solid #f0f0f0;
      background-color: #fafafa;
    }
  }

  .dialog-header {
    display: flex;
    align-items: center;
    padding: 20px 24px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;

    .header-icon {
      width: 48px;
      height: 48px;
      border-radius: 50%;
      background: rgba(255, 255, 255, 0.2);
      display: flex;
      align-items: center;
      justify-content: center;
      margin-right: 16px;

      .el-icon {
        font-size: 24px;
      }
    }

    .header-content {
      h3 {
        margin: 0 0 4px 0;
        font-size: 18px;
        font-weight: 600;
      }

      p {
        margin: 0;
        font-size: 14px;
        opacity: 0.9;
      }
    }
  }

  .avatar-upload-content {
    display: flex;
    gap: 24px;
    align-items: flex-start;

    .current-avatar {
      text-align: center;
      flex-shrink: 0;

      .avatar-wrapper {
        position: relative;
        display: inline-block;
        margin-bottom: 12px;

        .current-avatar-img {
          border: 3px solid #e4e7ed;
          transition: all 0.3s ease;
        }

        .avatar-overlay {
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: rgba(0, 0, 0, 0.5);
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          opacity: 0;
          transition: opacity 0.3s ease;

          .el-icon {
            color: white;
            font-size: 24px;
          }
        }

        &:hover .avatar-overlay {
          opacity: 1;
        }
      }

      .avatar-label {
        margin: 0;
        font-size: 12px;
        color: #909399;
      }
    }

    .upload-section {
      flex: 1;

      .avatar-uploader {
        :deep(.el-upload-dragger) {
          width: 100%;
          height: 200px;
          border: 2px dashed #d9d9d9;
          border-radius: 12px;
          background: #fafafa;
          transition: all 0.3s ease;

          &:hover {
            border-color: #409eff;
            background: #f0f9ff;
          }
        }

        .upload-area {
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          height: 100%;
          padding: 20px;

          .upload-icon {
            width: 64px;
            height: 64px;
            border-radius: 50%;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 16px;

            .el-icon {
              font-size: 28px;
              color: white;
            }
          }

          .upload-text {
            text-align: center;

            .main-text {
              margin: 0 0 8px 0;
              font-size: 16px;
              font-weight: 500;
              color: #303133;
            }

            .sub-text {
              margin: 0;
              font-size: 12px;
              color: #909399;
              line-height: 1.4;
            }
          }
        }

        .preview-area {
          display: flex;
          align-items: center;
          gap: 16px;
          padding: 20px;
          height: 100%;

          .preview-wrapper {
            position: relative;
            flex-shrink: 0;

            .preview-img {
              width: 120px;
              height: 120px;
              object-fit: cover;
              border-radius: 12px;
              border: 2px solid #e4e7ed;
            }

            .preview-overlay {
              position: absolute;
              top: 8px;
              right: 8px;

              .el-button {
                background: rgba(255, 255, 255, 0.9);
                border: none;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
              }
            }
          }

          .file-details {
            flex: 1;

            .file-name {
              margin: 0 0 8px 0;
              font-size: 14px;
              font-weight: 500;
              color: #303133;
              word-break: break-all;
              line-height: 1.4;
            }

            .file-size {
              margin: 0 0 12px 0;
              font-size: 12px;
              color: #909399;
            }
          }
        }
      }
    }
  }

  .dialog-footer {
    display: flex;
    justify-content: flex-end;
    gap: 12px;
  }
}

// 响应式设计
@media (max-width: 1200px) {
  .profile-container {
    .profile-banner {
      height: 240px;
      margin: -20px -20px 20px -20px;

      .banner-content {
        padding: 32px 24px;

        .user-avatar-section {
          gap: 20px;

          .avatar-wrapper .main-avatar {
            width: 100px;
            height: 100px;
          }

          .user-basic-info .username {
            font-size: 28px;
          }
        }

        .user-stats {
          gap: 24px;

          .stat-item .stat-value {
            font-size: 24px;
          }
        }
      }
    }

    .profile-content {
      padding: 0 20px 20px;

      :deep(.el-col-10) {
        width: 100%;
        margin-bottom: 24px;
      }

      :deep(.el-col-14) {
        width: 100%;
      }
    }
  }
}

@media (max-width: 992px) {
  .profile-container {
    .profile-banner {
      height: 200px;

      .banner-content {
        padding: 24px 20px;
        flex-direction: column;
        text-align: center;
        gap: 20px;

        .user-avatar-section {
          flex-direction: column;
          gap: 16px;

          .user-basic-info .username {
            font-size: 24px;
          }
        }

        .user-stats {
          gap: 20px;

          .stat-item .stat-value {
            font-size: 20px;
          }
        }
      }
    }
  }
}

@media (max-width: 768px) {
  .profile-container {
    .profile-banner {
      height: 180px;
      margin: -20px -10px 16px -10px;
      border-radius: 0 0 16px 16px;

      .banner-content {
        padding: 20px 16px;

        .user-avatar-section {
          .avatar-wrapper .main-avatar {
            width: 80px;
            height: 80px;
          }

          .user-basic-info .username {
            font-size: 20px;
          }
        }

        .user-stats {
          gap: 16px;

          .stat-item {
            .stat-value {
              font-size: 18px;
            }

            .stat-label {
              font-size: 12px;
            }
          }
        }
      }
    }

    .profile-content {
      padding: 0 16px 16px;

      .operation-card .profile-tabs .form-container {
        padding: 24px 20px;

        .profile-form,
        .password-form {
          :deep(.el-col-12) {
            width: 100%;
            margin-bottom: 0;
          }

          .el-form-item {
            margin-bottom: 20px;
          }
        }
      }
    }
  }
}

@media (max-width: 576px) {
  .profile-container {
    .profile-banner {
      height: 160px;

      .banner-content {
        padding: 16px 12px;

        .user-avatar-section {
          .avatar-wrapper .main-avatar {
            width: 70px;
            height: 70px;
          }

          .user-basic-info .username {
            font-size: 18px;
          }
        }

        .user-stats {
          gap: 12px;

          .stat-item {
            .stat-value {
              font-size: 16px;
            }

            .stat-label {
              font-size: 11px;
            }
          }
        }
      }
    }

    .profile-content {
      padding: 0 12px 12px;

      .info-cards .info-card {
        :deep(.el-card__header) {
          padding: 16px 20px;
        }

        :deep(.el-card__body) {
          padding: 20px;
        }
      }

      .operation-card .profile-tabs .form-container {
        padding: 20px 16px;

        .form-header {
          margin-bottom: 24px;

          h3 {
            font-size: 18px;
          }
        }
      }
    }
  }
}
</style>
