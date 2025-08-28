<template>
  <div class="dashboard">
    <!-- 欢迎信息 -->
    <div class="welcome-card">
      <div class="welcome-content">
        <h2>欢迎回来，{{ userStore.username || '用户' }}！</h2>
        <p>今天是 {{ currentDate }}，祝您工作愉快！</p>
      </div>
      <div class="welcome-stats">
        <el-row :gutter="20">
          <el-col :span="6">
            <div class="stat-item">
              <div class="stat-icon">
                <el-icon><User /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ statsData.userCount }}</div>
                <div class="stat-label">用户总数</div>
              </div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="stat-item">
              <div class="stat-icon">
                <el-icon><UserFilled /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ statsData.roleCount }}</div>
                <div class="stat-label">角色数量</div>
              </div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="stat-item">
              <div class="stat-icon">
                <el-icon><Menu /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ statsData.menuCount }}</div>
                <div class="stat-label">菜单数量</div>
              </div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="stat-item">
              <div class="stat-icon">
                <el-icon><OfficeBuilding /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ statsData.deptCount }}</div>
                <div class="stat-label">部门数量</div>
              </div>
            </div>
          </el-col>
        </el-row>
      </div>
    </div>
    
    <!-- 快捷操作 -->
    <el-row :gutter="20" class="quick-actions">
      <el-col :span="6">
        <el-card class="action-card" @click="$router.push('/system/user')">
          <div class="action-content">
            <el-icon class="action-icon"><User /></el-icon>
            <div class="action-text">
              <h3>用户管理</h3>
              <p>管理系统用户</p>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="action-card" @click="$router.push('/system/role')">
          <div class="action-content">
            <el-icon class="action-icon"><UserFilled /></el-icon>
            <div class="action-text">
              <h3>角色管理</h3>
              <p>配置用户角色</p>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="action-card" @click="$router.push('/system/menu')">
          <div class="action-content">
            <el-icon class="action-icon"><Menu /></el-icon>
            <div class="action-text">
              <h3>菜单管理</h3>
              <p>配置系统菜单</p>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="action-card" @click="$router.push('/system/department')">
          <div class="action-content">
            <el-icon class="action-icon"><OfficeBuilding /></el-icon>
            <div class="action-text">
              <h3>部门管理</h3>
              <p>管理组织架构</p>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 系统信息 -->
    <el-row :gutter="20" class="system-info">
      <el-col :span="12">
        <el-card>
          <template #header>
            <h3>系统信息</h3>
          </template>
          <div class="info-list">
            <div class="info-item">
              <span class="info-label">系统版本:</span>
              <span class="info-value">{{ systemInfo.system_version }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">服务器:</span>
              <span class="info-value">{{ systemInfo.server_info }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">数据库:</span>
              <span class="info-value">{{ systemInfo.database_info }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">最后登录:</span>
              <span class="info-value">{{ systemInfo.last_login_time || '首次登录' }}</span>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <h3>快速链接</h3>
          </template>
          <div class="quick-links">
            <el-button type="primary" @click="$router.push('/system/user')">
              <el-icon><User /></el-icon>
              用户管理
            </el-button>
            <el-button type="success" @click="$router.push('/system/role')">
              <el-icon><UserFilled /></el-icon>
              角色管理
            </el-button>
            <el-button type="warning" @click="$router.push('/system/menu')">
              <el-icon><Menu /></el-icon>
              菜单管理
            </el-button>
            <el-button type="primary" @click="$router.push('/system/department')">
              <el-icon><OfficeBuilding /></el-icon>
              部门管理
            </el-button>
            <el-button type="info" @click="$router.push('/logs')">
              <el-icon><Operation /></el-icon>
              日志管理
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { DashboardApi, type DashboardStats, type SystemInfo } from '@/api/modules/dashboard'
import { ElMessage } from 'element-plus'
import {
  User,
  UserFilled,
  Menu,
  OfficeBuilding,
  Operation
} from '@element-plus/icons-vue'
import { useUserStore } from '@/store'

const router = useRouter()
const userStore = useUserStore()

// 统计数据
const statsData = ref({
  userCount: 0,
  roleCount: 0,
  menuCount: 0,
  deptCount: 0
})

// 系统信息
const systemInfo = ref<SystemInfo>({
  system_version: 'v1.0.0',
  server_info: 'FastAPI + Vue 3',
  database_info: 'SQLite',
  last_login_time: undefined
})

// 加载状态
const loading = ref(false)

// 当前日期
const currentDate = computed(() => {
  return new Date().toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    weekday: 'long'
  })
})

// 获取仪表板统计数据
const loadDashboardStats = async () => {
  try {
    loading.value = true
    const response = await DashboardApi.getStats()

    if (response.success && response.data) {
      statsData.value = {
        userCount: response.data.user_count,
        roleCount: response.data.role_count,
        menuCount: response.data.menu_count,
        deptCount: response.data.department_count
      }
    }
  } catch (error) {
    console.error('获取仪表板统计数据失败:', error)
    ElMessage.error('获取统计数据失败')
  } finally {
    loading.value = false
  }
}

// 获取系统信息
const loadSystemInfo = async () => {
  try {
    const response = await DashboardApi.getSystemInfo()

    if (response.success && response.data) {
      systemInfo.value = response.data
    }
  } catch (error) {
    console.error('获取系统信息失败:', error)
  }
}

// 初始化数据
onMounted(async () => {
  await Promise.all([
    loadDashboardStats(),
    loadSystemInfo()
  ])
})
</script>

<style scoped lang="scss">
.dashboard {
  .welcome-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 12px;
    padding: 30px;
    margin-bottom: 20px;
    color: white;
    
    .welcome-content {
      margin-bottom: 30px;
      
      h2 {
        font-size: 28px;
        font-weight: 600;
        margin: 0 0 10px 0;
      }
      
      p {
        font-size: 16px;
        opacity: 0.9;
        margin: 0;
      }
    }
    
    .welcome-stats {
      .stat-item {
        display: flex;
        align-items: center;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        padding: 20px;
        
        .stat-icon {
          width: 50px;
          height: 50px;
          background: rgba(255, 255, 255, 0.2);
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          margin-right: 15px;
          
          .el-icon {
            font-size: 24px;
          }
        }
        
        .stat-info {
          .stat-value {
            font-size: 24px;
            font-weight: 600;
            margin-bottom: 5px;
          }
          
          .stat-label {
            font-size: 14px;
            opacity: 0.8;
          }
        }
      }
    }
  }
  
  .quick-actions {
    margin-bottom: 20px;
    
    .action-card {
      cursor: pointer;
      transition: all 0.3s ease;
      
      &:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
      }
      
      .action-content {
        text-align: center;
        padding: 20px;
        
        .action-icon {
          font-size: 48px;
          color: #409eff;
          margin-bottom: 15px;
        }
        
        .action-text {
          h3 {
            font-size: 18px;
            margin: 0 0 8px 0;
            color: #2c3e50;
          }
          
          p {
            font-size: 14px;
            color: #7f8c8d;
            margin: 0;
          }
        }
      }
    }
  }
  
  .system-info {
    .info-list {
      .info-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 12px 0;
        border-bottom: 1px solid #ebeef5;
        
        &:last-child {
          border-bottom: none;
        }
        
        .info-label {
          font-weight: 500;
          color: #606266;
        }
        
        .info-value {
          color: #2c3e50;
        }
      }
    }
    
    .quick-links {
      display: flex;
      flex-direction: column;
      gap: 10px;

      .el-button {
        justify-content: flex-start;
        width: 100% !important; // 强制所有按钮宽度一致
        min-width: 100% !important; // 确保最小宽度一致
        box-sizing: border-box; // 包含边框和内边距

        .el-icon {
          margin-right: 8px;
        }
      }
    }
  }
}

// 响应式设计
@media (max-width: 768px) {
  .dashboard {
    .welcome-stats {
      :deep(.el-col) {
        margin-bottom: 15px;
      }
    }
    
    .quick-actions {
      :deep(.el-col) {
        margin-bottom: 15px;
      }
    }
  }
}
</style>