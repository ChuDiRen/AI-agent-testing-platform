<template>
  <div class="profile-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1 class="page-title">个人中心</h1>
      <p class="page-subtitle">管理您的个人信息和账户设置</p>
    </div>

    <!-- 个人信息卡片 -->
    <div class="profile-content">
      <div class="profile-card">
        <div class="profile-header">
          <div class="avatar-section">
            <el-avatar :size="100" :src="userInfo.avatar" class="user-avatar">
              <el-icon><User /></el-icon>
            </el-avatar>
            <el-button type="primary" size="small" class="upload-btn">
              <el-icon><Upload /></el-icon>
              更换头像
            </el-button>
          </div>
          <div class="user-info">
            <h2 class="user-name">{{ userInfo.alias || userInfo.username }}</h2>
            <p class="user-role">{{ userInfo.role }}</p>
            <div class="user-stats">
              <div class="stat-item">
                <span class="stat-value">{{ userInfo.testCount }}</span>
                <span class="stat-label">执行测试</span>
              </div>
              <div class="stat-item">
                <span class="stat-value">{{ userInfo.caseCount }}</span>
                <span class="stat-label">创建用例</span>
              </div>
              <div class="stat-item">
                <span class="stat-value">{{ userInfo.projectCount }}</span>
                <span class="stat-label">参与项目</span>
              </div>
            </div>
          </div>
        </div>

        <el-divider />

        <!-- 个人信息表单 -->
        <el-form :model="userInfo" label-width="120px" class="profile-form">
          <el-form-item label="用户名">
            <el-input v-model="userInfo.username" disabled />
          </el-form-item>
          
          <el-form-item label="姓名">
            <el-input v-model="userInfo.alias" :disabled="!isEditing" placeholder="请输入真实姓名" />
          </el-form-item>
          
          <el-form-item label="邮箱">
            <el-input v-model="userInfo.email" :disabled="!isEditing" />
          </el-form-item>
          
          <el-form-item label="手机号">
            <el-input v-model="userInfo.phone" :disabled="!isEditing" />
          </el-form-item>
          
          <el-form-item label="账户状态">
            <el-tag :type="userInfo.isActive ? 'success' : 'danger'">
              {{ userInfo.isActive ? '已激活' : '已禁用' }}
            </el-tag>
          </el-form-item>
          
          <el-form-item label="最后登录">
            <el-input v-model="userInfo.lastLogin" disabled />
          </el-form-item>

          <el-form-item>
            <el-button v-if="!isEditing" type="primary" @click="startEdit">
              <el-icon><Edit /></el-icon>
              编辑资料
            </el-button>
            <template v-else>
              <el-button type="primary" @click="saveProfile">
                <el-icon><Check /></el-icon>
                保存
              </el-button>
              <el-button @click="cancelEdit">
                <el-icon><Close /></el-icon>
                取消
              </el-button>
            </template>
          </el-form-item>
        </el-form>
      </div>

      <!-- 修改密码卡片 -->
      <div class="password-card">
        <h3 class="card-title">修改密码</h3>
        <el-form :model="passwordForm" :rules="passwordRules" ref="passwordFormRef" label-width="120px">
          <el-form-item label="当前密码" prop="oldPassword">
            <el-input v-model="passwordForm.oldPassword" type="password" show-password />
          </el-form-item>
          
          <el-form-item label="新密码" prop="newPassword">
            <el-input v-model="passwordForm.newPassword" type="password" show-password />
          </el-form-item>
          
          <el-form-item label="确认密码" prop="confirmPassword">
            <el-input v-model="passwordForm.confirmPassword" type="password" show-password />
          </el-form-item>

          <el-form-item>
            <el-button type="primary" @click="changePassword">
              <el-icon><Lock /></el-icon>
              修改密码
            </el-button>
          </el-form-item>
        </el-form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import axios from '~/axios.js';
import loginApi from '../login/loginApi';

const isEditing = ref(false);
const passwordFormRef = ref(null);

const userInfo = reactive({
  id: 0,
  username: '',
  alias: '',
  email: '',
  phone: '',
  department: '',
  position: '',
  bio: '',
  role: '',
  avatar: '',
  testCount: 0,
  caseCount: 0,
  projectCount: 0,
  isActive: true,
  lastLogin: ''
});

const userInfoBackup = ref({});

const passwordForm = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
});

const passwordRules = {
  oldPassword: [
    { required: true, message: '请输入当前密码', trigger: 'blur' }
  ],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度为6-20个字符', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请再次输入新密码', trigger: 'blur' },
    { 
      validator: (rule, value, callback) => {
        if (value !== passwordForm.newPassword) {
          callback(new Error('两次输入的密码不一致'));
        } else {
          callback();
        }
      }, 
      trigger: 'blur' 
    }
  ]
};

onMounted(() => {
  fetchUserProfile();
});

const fetchUserProfile = async () => {
  try {
    const response = await axios.get('/api/profile');
    if (response.data.code === 200) {
      Object.assign(userInfo, response.data.data);
    }
  } catch (error) {
    console.error('获取用户信息失败:', error);
  }
};

const startEdit = () => {
  userInfoBackup.value = { ...userInfo };
  isEditing.value = true;
};

const cancelEdit = () => {
  Object.assign(userInfo, userInfoBackup.value);
  isEditing.value = false;
};

const saveProfile = async () => {
  try {
    // 只发送可修改的字段
    const updateData = {
      alias: userInfo.alias,
      email: userInfo.email,
      phone: userInfo.phone
    };
    
    const response = await axios.put('/api/profile', updateData);
    if (response.data.code === 200) {
      ElMessage.success('个人信息更新成功');
      isEditing.value = false;
      // 重新获取用户信息
      await fetchUserProfile();
    }
  } catch (error) {
    ElMessage.error(error.response?.data?.msg || '更新失败，请重试');
  }
};

const changePassword = async () => {
  if (!passwordFormRef.value) return;
  
  await passwordFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        const response = await loginApi.changePassword({
          old_password: passwordForm.oldPassword,
          new_password: passwordForm.newPassword
        });
        
        if (response.data.code === 200) {
          ElMessage.success('密码修改成功，请重新登录');
          passwordForm.oldPassword = '';
          passwordForm.newPassword = '';
          passwordForm.confirmPassword = '';
          
          setTimeout(() => {
            localStorage.removeItem('token');
            localStorage.removeItem('refreshToken');
            window.location.href = '/login';
          }, 1500);
        }
      } catch (error) {
        ElMessage.error(error.response?.data?.msg || '密码修改失败');
      }
    }
  });
};
</script>

<style scoped>
.profile-page {
  padding: 2rem;
  background: var(--color-bg-primary);
  min-height: calc(100vh - 70px);
}

.page-header {
  margin-bottom: 2rem;
}

.page-title {
  font-family: var(--font-heading);
  font-size: var(--text-3xl);
  font-weight: 700;
  color: var(--color-text-primary);
  margin-bottom: 0.5rem;
}

.page-subtitle {
  font-size: var(--text-base);
  color: var(--color-text-muted);
}

.profile-content {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 2rem;
}

.profile-card,
.password-card {
  background: white;
  border-radius: var(--radius-lg);
  padding: 2rem;
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--color-border);
}

.profile-header {
  display: flex;
  gap: 2rem;
  margin-bottom: 2rem;
}

.avatar-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.user-avatar {
  border: 4px solid var(--color-border);
  box-shadow: var(--shadow-md);
}

.upload-btn {
  font-size: var(--text-xs);
}

.user-info {
  flex: 1;
}

.user-name {
  font-family: var(--font-heading);
  font-size: var(--text-2xl);
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: 0.5rem;
}

.user-role {
  font-size: var(--text-sm);
  color: var(--color-text-muted);
  margin-bottom: 1.5rem;
}

.user-stats {
  display: flex;
  gap: 2rem;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 1rem;
  background: var(--color-bg-secondary);
  border-radius: var(--radius-md);
  min-width: 100px;
}

.stat-value {
  font-family: var(--font-heading);
  font-size: var(--text-2xl);
  font-weight: 700;
  color: var(--color-primary);
  margin-bottom: 0.25rem;
}

.stat-label {
  font-size: var(--text-xs);
  color: var(--color-text-muted);
}

.profile-form {
  margin-top: 2rem;
}

.card-title {
  font-family: var(--font-heading);
  font-size: var(--text-xl);
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: 1.5rem;
}

@media (max-width: 1024px) {
  .profile-content {
    grid-template-columns: 1fr;
  }
  
  .profile-header {
    flex-direction: column;
    align-items: center;
    text-align: center;
  }
}
</style>
