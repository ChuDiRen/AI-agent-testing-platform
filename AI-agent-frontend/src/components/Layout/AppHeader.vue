<template>
  <div class="app-header">
    <div class="header-left">
      <!-- 折叠按钮 -->
      <el-button
        @click="toggleCollapsed"
        type="text"
        class="collapse-btn"
        :icon="systemStore.collapsed ? Expand : Fold"
      />
      
      <!-- Logo -->
      <div class="logo">
        <span class="logo-text">AI智能代理测试平台</span>
      </div>
    </div>
    
    <div class="header-right">
      <!-- 全屏按钮 -->
      <el-tooltip content="全屏" placement="bottom">
        <el-button
          @click="toggleFullscreen"
          type="text"
          class="header-btn"
          :icon="FullScreen"
        />
      </el-tooltip>
      
      <!-- 消息通知 -->
      <el-tooltip content="消息通知" placement="bottom">
        <el-badge :value="3" :max="99" class="notification-badge">
          <el-button
            type="text"
            class="header-btn"
            :icon="Bell"
          />
        </el-badge>
      </el-tooltip>
      
      <!-- 用户头像菜单 -->
      <el-dropdown @command="handleUserMenuCommand" class="user-dropdown">
        <div class="user-info">
          <el-avatar
            :src="userStore.avatar"
            :size="36"
            class="user-avatar"
          >
            <template #default>
              <el-icon><User /></el-icon>
            </template>
          </el-avatar>
          <span class="username">{{ userStore.username || '用户' }}</span>
          <el-icon class="dropdown-arrow"><ArrowDown /></el-icon>
        </div>
        
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="profile" :icon="User">
              个人中心
            </el-dropdown-item>
            <el-dropdown-item command="settings" :icon="Setting">
              系统设置
            </el-dropdown-item>
            <el-dropdown-item divided command="logout" :icon="SwitchButton">
              退出登录
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Fold,
  Expand,
  FullScreen,
  Bell,
  User,
  ArrowDown,
  Setting,
  SwitchButton
} from '@element-plus/icons-vue'
import { useUserStore, useSystemStore } from '@/store'

const router = useRouter()
const userStore = useUserStore()
const systemStore = useSystemStore()

const isFullscreen = ref(false)

// 切换侧边栏折叠状态
const toggleCollapsed = () => {
  systemStore.toggleCollapsed()
}

// 切换全屏
const toggleFullscreen = () => {
  if (!document.fullscreenElement) {
    document.documentElement.requestFullscreen()
    isFullscreen.value = true
  } else {
    document.exitFullscreen()
    isFullscreen.value = false
  }
}

// 处理用户菜单命令
const handleUserMenuCommand = async (command: string) => {
  switch (command) {
    case 'profile':
      ElMessage.info('个人中心功能开发中...')
      break
    case 'settings':
      ElMessage.info('系统设置功能开发中...')
      break
    case 'logout':
      try {
        await ElMessageBox.confirm(
          '确定要退出登录吗？',
          '提示',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )
        
        await userStore.logout()
        await router.push('/login')
      } catch (error) {
        // 用户取消退出
      }
      break
  }
}
</script>

<style scoped lang="scss">
.app-header {
  height: 60px;
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
  position: relative;
  z-index: 999;
  
  .header-left {
    display: flex;
    align-items: center;
    
    .collapse-btn {
      margin-right: 20px;
      font-size: 18px;
      
      &:hover {
        background-color: #f5f7fa;
      }
    }
    
    .logo {
      .logo-text {
        font-size: 20px;
        font-weight: 600;
        color: #2c3e50;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
      }
    }
  }
  
  .header-right {
    display: flex;
    align-items: center;
    gap: 12px;
    
    .header-btn {
      width: 40px;
      height: 40px;
      border-radius: 50%;
      font-size: 18px;
      
      &:hover {
        background-color: #f5f7fa;
      }
    }
    
    .notification-badge {
      :deep(.el-badge__content) {
        transform: translateY(-50%) translateX(50%);
      }
    }
    
    .user-dropdown {
      .user-info {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 8px 12px;
        border-radius: 6px;
        cursor: pointer;
        transition: background-color 0.3s;
        
        &:hover {
          background-color: #f5f7fa;
        }
        
        .user-avatar {
          border: 2px solid #e4e7ed;
        }
        
        .username {
          font-size: 14px;
          font-weight: 500;
          color: #2c3e50;
          max-width: 80px;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }
        
        .dropdown-arrow {
          font-size: 12px;
          color: #909399;
          transition: transform 0.3s;
        }
      }
      
      &.is-active .user-info .dropdown-arrow {
        transform: rotate(180deg);
      }
    }
  }
}

// 响应式设计
@media (max-width: 1200px) {
  .app-header {
    .header-left {
      .logo {
        .logo-text {
          font-size: 18px;
        }
      }
    }
  }
}

@media (max-width: 992px) {
  .app-header {
    padding: 0 16px;

    .header-left {
      .logo {
        .logo-text {
          font-size: 16px;
        }
      }
    }

    .header-right {
      gap: 10px;
    }
  }
}

@media (max-width: 768px) {
  .app-header {
    padding: 0 15px;

    .header-left {
      .logo {
        .logo-text {
          display: none;
        }
      }
    }

    .header-right {
      gap: 8px;

      .username {
        display: none;
      }
    }
  }
}

@media (max-width: 576px) {
  .app-header {
    padding: 0 12px;

    .header-right {
      gap: 6px;

      .header-btn {
        width: 36px;
        height: 36px;
        font-size: 16px;
      }
    }
  }
}
</style>