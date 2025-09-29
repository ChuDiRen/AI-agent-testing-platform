<template>
  <div class="profile-page">
    <NCard title="个人资料">
      <div class="profile-content">
        <!-- 头像区域 -->
        <div class="avatar-section">
          <NAvatar
            :size="120"
            :src="userStore.avatar"
            fallback-src="/default-avatar.png"
          />
          <div class="avatar-info">
            <h2>{{ userStore.name }}</h2>
            <p>{{ userStore.email }}</p>
            <NTag v-if="userStore.isSuperUser" type="success">超级管理员</NTag>
          </div>
        </div>

        <!-- 基本信息 -->
        <NDivider title-placement="left">基本信息</NDivider>
        <NForm
          ref="profileFormRef"
          :model="profileForm"
          :rules="profileRules"
          label-placement="left"
          label-width="100px"
        >
          <NGrid :cols="2" :x-gap="24">
            <NGridItem>
              <NFormItem label="用户名" path="username">
                <NInput v-model:value="profileForm.username" disabled />
              </NFormItem>
            </NGridItem>
            <NGridItem>
              <NFormItem label="邮箱" path="email">
                <NInput v-model:value="profileForm.email" />
              </NFormItem>
            </NGridItem>
          </NGrid>
          <NFormItem>
            <NButton type="primary" :loading="updateLoading" @click="handleUpdateProfile">
              更新资料
            </NButton>
          </NFormItem>
        </NForm>

        <!-- 修改密码 -->
        <NDivider title-placement="left">修改密码</NDivider>
        <NForm
          ref="passwordFormRef"
          :model="passwordForm"
          :rules="passwordRules"
          label-placement="left"
          label-width="100px"
        >
          <NGrid :cols="1" :x-gap="24">
            <NGridItem>
              <NFormItem label="当前密码" path="old_password">
                <NInput
                  v-model:value="passwordForm.old_password"
                  type="password"
                  show-password-on="mousedown"
                  placeholder="请输入当前密码"
                />
              </NFormItem>
            </NGridItem>
            <NGridItem>
              <NFormItem label="新密码" path="new_password">
                <NInput
                  v-model:value="passwordForm.new_password"
                  type="password"
                  show-password-on="mousedown"
                  placeholder="请输入新密码"
                />
              </NFormItem>
            </NGridItem>
            <NGridItem>
              <NFormItem label="确认密码" path="confirm_password">
                <NInput
                  v-model:value="passwordForm.confirm_password"
                  type="password"
                  show-password-on="mousedown"
                  placeholder="请确认新密码"
                />
              </NFormItem>
            </NGridItem>
          </NGrid>
          <NFormItem>
            <NButton type="primary" :loading="passwordLoading" @click="handleUpdatePassword">
              修改密码
            </NButton>
          </NFormItem>
        </NForm>

        <!-- 登录信息 -->
        <NDivider title-placement="left">登录信息</NDivider>
        <NDescriptions :column="2" bordered>
          <NDescriptionsItem label="用户ID">
            {{ userStore.userId }}
          </NDescriptionsItem>
          <NDescriptionsItem label="账户状态">
            <NTag :type="userStore.isActive ? 'success' : 'error'">
              {{ userStore.isActive ? '正常' : '禁用' }}
            </NTag>
          </NDescriptionsItem>
          <NDescriptionsItem label="用户角色">
            <NSpace>
              <NTag v-for="role in userStore.role" :key="role" type="info">
                {{ role }}
              </NTag>
            </NSpace>
          </NDescriptionsItem>
          <NDescriptionsItem label="最后登录">
            {{ formatDate(userStore.userInfo.last_login) || '暂无记录' }}
          </NDescriptionsItem>
        </NDescriptions>
      </div>
    </NCard>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useUserStore } from '@/store'
import { formatDate } from '@/utils'
import api from '@/api'

defineOptions({ name: '个人资料' })

const userStore = useUserStore()

// 响应式数据
const profileFormRef = ref()
const passwordFormRef = ref()
const updateLoading = ref(false)
const passwordLoading = ref(false)

// 个人资料表单
const profileForm = reactive({
  username: '',
  email: '',
})

// 密码表单
const passwordForm = reactive({
  old_password: '',
  new_password: '',
  confirm_password: '',
})

// 个人资料验证规则
const profileRules = {
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '邮箱格式不正确', trigger: 'blur' },
  ],
}

// 密码验证规则
const passwordRules = {
  old_password: [
    { required: true, message: '请输入当前密码', trigger: 'blur' },
  ],
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' },
  ],
  confirm_password: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    {
      validator: (rule, value) => {
        return value === passwordForm.new_password
      },
      message: '两次密码输入不一致',
      trigger: 'blur',
    },
  ],
}

// 更新个人资料
const handleUpdateProfile = async () => {
  try {
    await profileFormRef.value?.validate()
    updateLoading.value = true
    
    // 更新用户信息
    userStore.setUserInfo({
      email: profileForm.email,
    })
    
    window.$message?.success('个人资料更新成功')
  } catch (error) {
    console.error('更新个人资料失败:', error)
  } finally {
    updateLoading.value = false
  }
}

// 修改密码
const handleUpdatePassword = async () => {
  try {
    await passwordFormRef.value?.validate()
    passwordLoading.value = true
    
    await api.updatePassword({
      old_password: passwordForm.old_password,
      new_password: passwordForm.new_password,
    })
    
    // 清空表单
    Object.assign(passwordForm, {
      old_password: '',
      new_password: '',
      confirm_password: '',
    })
    
    window.$message?.success('密码修改成功')
  } catch (error) {
    console.error('修改密码失败:', error)
  } finally {
    passwordLoading.value = false
  }
}

// 初始化数据
const initData = () => {
  profileForm.username = userStore.name
  profileForm.email = userStore.email
}

onMounted(() => {
  initData()
})
</script>

<style scoped>
.profile-page {
  padding: 16px;
  max-width: 800px;
  margin: 0 auto;
}

.profile-content {
  padding: 24px;
}

.avatar-section {
  display: flex;
  align-items: center;
  margin-bottom: 32px;
}

.avatar-info {
  margin-left: 24px;
}

.avatar-info h2 {
  margin: 0 0 8px 0;
  font-size: 24px;
  font-weight: 600;
}

.avatar-info p {
  margin: 0 0 12px 0;
  color: var(--text-color-3);
  font-size: 14px;
}
</style>
