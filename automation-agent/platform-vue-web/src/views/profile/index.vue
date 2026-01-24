<template>
  <div class="profile-container">
    <div class="profile-card">
      <div class="profile-header">
        <el-avatar :size="80" :src="userStore.avatar || defaultAvatar" class="profile-avatar" />
        <div class="profile-info">
          <h2 class="profile-name">{{ userStore.username || '用户' }}</h2>
          <p class="profile-email">{{ userStore.email || '暂无邮箱' }}</p>
          <el-tag :type="userStore.isSuperUser ? 'danger' : 'primary'" size="small">
            {{ userStore.isSuperUser ? '超级管理员' : '普通用户' }}
          </el-tag>
        </div>
      </div>

      <el-divider />

      <el-form label-width="100px" class="profile-form">
        <el-form-item label="用户名">
          <el-input v-model="formData.username" disabled />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="formData.email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item label="别名">
          <el-input v-model="formData.alias" placeholder="请输入别名" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSave">保存修改</el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/store/modules/user'

const userStore = useUserStore()
const defaultAvatar = 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png'

const formData = reactive({
  username: '',
  email: '',
  alias: ''
})

onMounted(() => {
  formData.username = userStore.username || ''
  formData.email = userStore.email || ''
  formData.alias = userStore.alias || ''
})

const handleSave = () => {
  ElMessage.success('个人信息已保存')
}
</script>

<style scoped>
.profile-container { padding: 24px; max-width: 600px; margin: 0 auto; }
.profile-card { background: white; border-radius: 12px; padding: 32px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
.profile-header { display: flex; align-items: center; gap: 24px; margin-bottom: 24px; }
.profile-avatar { border: 3px solid #e5e7eb; }
.profile-name { font-size: 24px; font-weight: 600; color: #1f2937; margin: 0 0 4px 0; }
.profile-email { font-size: 14px; color: #6b7280; margin: 0 0 8px 0; }
.profile-form { margin-top: 24px; }
</style>

