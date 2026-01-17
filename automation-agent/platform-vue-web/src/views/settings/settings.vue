<template>
  <div class="settings-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1 class="page-title">系统设置</h1>
      <p class="page-subtitle">配置系统参数和偏好设置</p>
    </div>

    <!-- 设置内容 -->
    <div class="settings-content">
      <!-- 基础设置 -->
      <div class="settings-card">
        <h3 class="card-title">
          <el-icon><Setting /></el-icon>
          基础设置
        </h3>
        <el-form :model="basicSettings" label-width="150px">
          <el-form-item label="系统名称">
            <el-input v-model="basicSettings.systemName" />
          </el-form-item>
          
          <el-form-item label="系统描述">
            <el-input v-model="basicSettings.systemDesc" type="textarea" :rows="3" />
          </el-form-item>
          
          <el-form-item label="默认语言">
            <el-select v-model="basicSettings.language" style="width: 100%">
              <el-option label="简体中文" value="zh-CN" />
              <el-option label="English" value="en-US" />
            </el-select>
          </el-form-item>
          
          <el-form-item label="时区">
            <el-select v-model="basicSettings.timezone" style="width: 100%">
              <el-option label="北京时间 (UTC+8)" value="Asia/Shanghai" />
              <el-option label="东京时间 (UTC+9)" value="Asia/Tokyo" />
              <el-option label="纽约时间 (UTC-5)" value="America/New_York" />
            </el-select>
          </el-form-item>

          <el-form-item>
            <el-button type="primary" @click="saveBasicSettings">
              <el-icon><Check /></el-icon>
              保存设置
            </el-button>
          </el-form-item>
        </el-form>
      </div>

      <!-- 测试设置 -->
      <div class="settings-card">
        <h3 class="card-title">
          <el-icon><Cpu /></el-icon>
          测试设置
        </h3>
        <el-form :model="testSettings" label-width="150px">
          <el-form-item label="默认超时时间">
            <el-input-number v-model="testSettings.defaultTimeout" :min="1" :max="300" />
            <span class="unit-text">秒</span>
          </el-form-item>
          
          <el-form-item label="最大重试次数">
            <el-input-number v-model="testSettings.maxRetries" :min="0" :max="10" />
            <span class="unit-text">次</span>
          </el-form-item>
          
          <el-form-item label="并发执行数">
            <el-input-number v-model="testSettings.concurrency" :min="1" :max="20" />
            <span class="unit-text">个</span>
          </el-form-item>
          
          <el-form-item label="失败后继续">
            <el-switch v-model="testSettings.continueOnFailure" />
          </el-form-item>
          
          <el-form-item label="自动生成报告">
            <el-switch v-model="testSettings.autoGenerateReport" />
          </el-form-item>

          <el-form-item>
            <el-button type="primary" @click="saveTestSettings">
              <el-icon><Check /></el-icon>
              保存设置
            </el-button>
          </el-form-item>
        </el-form>
      </div>

      <!-- 通知设置 -->
      <div class="settings-card">
        <h3 class="card-title">
          <el-icon><Bell /></el-icon>
          通知设置
        </h3>
        <el-form :model="notificationSettings" label-width="150px">
          <el-form-item label="邮件通知">
            <el-switch v-model="notificationSettings.emailEnabled" />
          </el-form-item>
          
          <el-form-item label="微信通知">
            <el-switch v-model="notificationSettings.wechatEnabled" />
          </el-form-item>
          
          <el-form-item label="钉钉通知">
            <el-switch v-model="notificationSettings.dingdingEnabled" />
          </el-form-item>
          
          <el-form-item label="飞书通知">
            <el-switch v-model="notificationSettings.feishuEnabled" />
          </el-form-item>
          
          <el-form-item label="通知时机">
            <el-checkbox-group v-model="notificationSettings.notifyOn">
              <el-checkbox label="success">测试成功</el-checkbox>
              <el-checkbox label="failure">测试失败</el-checkbox>
              <el-checkbox label="error">执行错误</el-checkbox>
            </el-checkbox-group>
          </el-form-item>

          <el-form-item>
            <el-button type="primary" @click="saveNotificationSettings">
              <el-icon><Check /></el-icon>
              保存设置
            </el-button>
          </el-form-item>
        </el-form>
      </div>

      <!-- 安全设置 -->
      <div class="settings-card">
        <h3 class="card-title">
          <el-icon><Lock /></el-icon>
          安全设置
        </h3>
        <el-form :model="securitySettings" label-width="150px">
          <el-form-item label="会话超时">
            <el-input-number v-model="securitySettings.sessionTimeout" :min="5" :max="1440" />
            <span class="unit-text">分钟</span>
          </el-form-item>
          
          <el-form-item label="密码强度">
            <el-select v-model="securitySettings.passwordStrength" style="width: 100%">
              <el-option label="低 (6位以上)" value="low" />
              <el-option label="中 (8位+字母数字)" value="medium" />
              <el-option label="高 (10位+字母数字符号)" value="high" />
            </el-select>
          </el-form-item>
          
          <el-form-item label="登录失败锁定">
            <el-switch v-model="securitySettings.loginLockEnabled" />
          </el-form-item>
          
          <el-form-item label="最大失败次数" v-if="securitySettings.loginLockEnabled">
            <el-input-number v-model="securitySettings.maxLoginAttempts" :min="3" :max="10" />
            <span class="unit-text">次</span>
          </el-form-item>

          <el-form-item>
            <el-button type="primary" @click="saveSecuritySettings">
              <el-icon><Check /></el-icon>
              保存设置
            </el-button>
          </el-form-item>
        </el-form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import axios from '~/axios.js';

const basicSettings = reactive({
  systemName: 'API 自动化测试平台',
  systemDesc: '专业的接口测试管理解决方案',
  language: 'zh-CN',
  timezone: 'Asia/Shanghai'
});

const testSettings = reactive({
  defaultTimeout: 30,
  maxRetries: 3,
  concurrency: 5,
  continueOnFailure: true,
  autoGenerateReport: true
});

const notificationSettings = reactive({
  emailEnabled: false,
  wechatEnabled: true,
  dingdingEnabled: false,
  feishuEnabled: false,
  notifyOn: ['failure', 'error']
});

const securitySettings = reactive({
  sessionTimeout: 30,
  passwordStrength: 'medium',
  loginLockEnabled: true,
  maxLoginAttempts: 5
});

onMounted(() => {
  fetchSettings();
});

const fetchSettings = async () => {
  try {
    const response = await axios.get('/api/settings');
    if (response.data.code === 200) {
      const data = response.data.data;
      if (data.basic) Object.assign(basicSettings, data.basic);
      if (data.test) Object.assign(testSettings, data.test);
      if (data.notification) Object.assign(notificationSettings, data.notification);
      if (data.security) Object.assign(securitySettings, data.security);
    }
  } catch (error) {
    console.error('获取设置失败:', error);
  }
};

const saveBasicSettings = async () => {
  try {
    const response = await axios.put('/api/settings/basic', basicSettings);
    if (response.data.code === 200) {
      ElMessage.success('基础设置保存成功');
    }
  } catch (error) {
    ElMessage.error('保存失败，请重试');
  }
};

const saveTestSettings = async () => {
  try {
    const response = await axios.put('/api/settings/test', testSettings);
    if (response.data.code === 200) {
      ElMessage.success('测试设置保存成功');
    }
  } catch (error) {
    ElMessage.error('保存失败，请重试');
  }
};

const saveNotificationSettings = async () => {
  try {
    const response = await axios.put('/api/settings/notification', notificationSettings);
    if (response.data.code === 200) {
      ElMessage.success('通知设置保存成功');
    }
  } catch (error) {
    ElMessage.error('保存失败，请重试');
  }
};

const saveSecuritySettings = async () => {
  try {
    const response = await axios.put('/api/settings/security', securitySettings);
    if (response.data.code === 200) {
      ElMessage.success('安全设置保存成功');
    }
  } catch (error) {
    ElMessage.error('保存失败，请重试');
  }
};
</script>

<style scoped>
.settings-page {
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

.settings-content {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
  gap: 2rem;
}

.settings-card {
  background: white;
  border-radius: var(--radius-lg);
  padding: 2rem;
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--color-border);
}

.card-title {
  font-family: var(--font-heading);
  font-size: var(--text-xl);
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: 1.5rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.unit-text {
  margin-left: 0.5rem;
  color: var(--color-text-muted);
  font-size: var(--text-sm);
}

@media (max-width: 1024px) {
  .settings-content {
    grid-template-columns: 1fr;
  }
}
</style>
