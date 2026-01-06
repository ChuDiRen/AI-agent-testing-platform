<template>
  <div class="workspace-container">
    <!-- 顶部导航 -->
    <header class="workspace-header">
      <div class="logo">
        <span class="logo-icon">🐻</span>
        <span class="logo-text">大熊AI测试平台</span>
      </div>
      <div class="user-info">
        <el-dropdown @command="handleCommand">
          <span class="user-dropdown">
            <el-avatar :size="32" :src="userAvatar">
              {{ userInfo?.username?.charAt(0)?.toUpperCase() || 'U' }}
            </el-avatar>
            <span class="username">{{ userInfo?.username || '用户' }}</span>
            <el-icon><ArrowDown /></el-icon>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="profile">个人中心</el-dropdown-item>
              <el-dropdown-item command="settings">系统设置</el-dropdown-item>
              <el-dropdown-item divided command="logout">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </header>

    <!-- 主体内容 -->
    <main class="workspace-main">
      <div class="welcome-section">
        <h1 class="welcome-title">欢迎回来，{{ userInfo?.nickname || userInfo?.username || '用户' }}</h1>
        <p class="welcome-desc">请选择要进入的功能模块</p>
      </div>

      <!-- 模块卡片 -->
      <div class="module-cards">
        <div 
          v-for="module in modules" 
          :key="module.key"
          class="module-card"
          :class="{ 'disabled': !module.enabled }"
          @click="enterModule(module)"
        >
          <div class="card-icon" :style="{ background: module.gradient }">
            <span class="icon-emoji">{{ module.icon }}</span>
          </div>
          <div class="card-content">
            <h3 class="card-title">{{ module.name }}</h3>
            <p class="card-desc">{{ module.description }}</p>
          </div>
          <div class="card-badge" v-if="module.badge">
            <el-tag :type="module.badgeType" size="small">{{ module.badge }}</el-tag>
          </div>
          <div class="card-arrow">
            <el-icon><ArrowRight /></el-icon>
          </div>
        </div>
      </div>
    </main>

    <!-- 底部 -->
    <footer class="workspace-footer">
      <p>© 2024 大熊AI测试平台 - 让测试更智能</p>
    </footer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useStore } from 'vuex'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowDown, ArrowRight } from '@element-plus/icons-vue'

const router = useRouter()
const store = useStore()

const userInfo = computed(() => store.state.userInfo)
const userAvatar = computed(() => userInfo.value?.avatar || '')

// 功能模块配置（移除消息通知，保留核心模块）
const modules = ref([
  {
    key: 'ai-assistant',
    name: 'AI智能助手',
    description: 'AI驱动的测试用例生成、智能分析、代码生成',
    icon: '🤖',
    gradient: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    enabled: true,
    badge: 'HOT',
    badgeType: 'danger'
  },
  {
    key: 'api-test',
    name: 'API自动化测试',
    description: '接口项目管理、用例编写、资源配置、消息通知、执行报告',
    icon: '🔌',
    gradient: 'linear-gradient(135deg, #11998e 0%, #38ef7d 100%)',
    enabled: true,
    badge: '',
    badgeType: ''
  },
  {
    key: 'web-test',
    name: 'Web UI自动化',
    description: 'Web项目管理、元素定位、用例录制、消息通知、执行报告',
    icon: '🌐',
    gradient: 'linear-gradient(135deg, #fc4a1a 0%, #f7b733 100%)',
    enabled: true,
    badge: '',
    badgeType: ''
  },
  {
    key: 'system',
    name: '系统管理',
    description: '用户管理、角色权限、菜单配置、部门管理',
    icon: '⚙️',
    gradient: 'linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)',
    enabled: true,
    badge: '',
    badgeType: ''
  },
  {
    key: 'generator',
    name: '代码生成器',
    description: '数据库表结构、代码模板、自动生成',
    icon: '🛠️',
    gradient: 'linear-gradient(135deg, #89f7fe 0%, #66a6ff 100%)',
    enabled: true,
    badge: 'NEW',
    badgeType: 'success'
  }
])

// 进入模块
const enterModule = (module) => {
  if (!module.enabled) {
    ElMessage.warning('该模块暂未开放')
    return
  }
  
  // 保存当前选择的模块
  store.commit('setCurrentModule', module.key)
  localStorage.setItem('currentModule', module.key)
  
  // 根据模块跳转到对应的默认页面
  const defaultRoutes = {
    'ai-assistant': '/AgentChatIntegrated',
    'api-test': '/ApiProjectList',
    'web-test': '/WebProjectList',
    'system': '/userList',
    'generator': '/GenTableList'
  }
  
  const targetRoute = defaultRoutes[module.key] || '/Statistics'
  router.push(targetRoute)
}

// 下拉菜单命令
const handleCommand = (command) => {
  switch (command) {
    case 'profile':
      router.push('/userList')
      break
    case 'settings':
      store.commit('setCurrentModule', 'system')
      router.push('/menuList')
      break
    case 'logout':
      ElMessageBox.confirm('确定要退出登录吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        store.dispatch('logout')
        router.replace('/login')
      })
      break
  }
}

onMounted(() => {
  // 清除之前选择的模块
  store.commit('setCurrentModule', '')
})
</script>

<style scoped>
.workspace-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ec 100%);
  display: flex;
  flex-direction: column;
}

[data-theme="dark"] .workspace-container {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
}

/* 顶部导航 */
.workspace-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 32px;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

[data-theme="dark"] .workspace-header {
  background: rgba(30, 41, 59, 0.9);
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-icon {
  font-size: 32px;
}

.logo-text {
  font-size: 20px;
  font-weight: 700;
  color: var(--text-primary);
}

.user-dropdown {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 8px;
  transition: background 0.3s;
}

.user-dropdown:hover {
  background: var(--bg-hover);
}

.username {
  color: var(--text-primary);
  font-weight: 500;
}

/* 主体内容 */
.workspace-main {
  flex: 1;
  padding: 40px 32px;
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
}

.welcome-section {
  text-align: center;
  margin-bottom: 48px;
}

.welcome-title {
  font-size: 32px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 12px;
}

.welcome-desc {
  font-size: 16px;
  color: var(--text-secondary);
}

/* 模块卡片 */
.module-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 24px;
}

.module-card {
  position: relative;
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 24px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
}

[data-theme="dark"] .module-card {
  background: rgba(30, 41, 59, 0.8);
}

.module-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.1);
}

.module-card.disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.module-card.disabled:hover {
  transform: none;
}

.card-icon {
  width: 64px;
  height: 64px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.icon-emoji {
  font-size: 32px;
}

.card-content {
  flex: 1;
  min-width: 0;
}

.card-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.card-desc {
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-badge {
  position: absolute;
  top: 12px;
  right: 12px;
}

.card-arrow {
  color: var(--text-tertiary);
  transition: transform 0.3s;
}

.module-card:hover .card-arrow {
  transform: translateX(4px);
  color: var(--primary-color);
}

/* 底部 */
.workspace-footer {
  text-align: center;
  padding: 24px;
  color: var(--text-tertiary);
  font-size: 14px;
}

/* 响应式 */
@media (max-width: 768px) {
  .workspace-header {
    padding: 12px 16px;
  }
  
  .workspace-main {
    padding: 24px 16px;
  }
  
  .welcome-title {
    font-size: 24px;
  }
  
  .module-cards {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .module-card {
    padding: 16px;
  }
  
  .card-icon {
    width: 48px;
    height: 48px;
  }
  
  .icon-emoji {
    font-size: 24px;
  }
}
</style>
