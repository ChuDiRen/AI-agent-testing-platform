<template>
  <div class="app-sidebar" :class="{ 'collapsed': systemStore.collapsed }">
    <div class="sidebar-content">
      <!-- 菜单导航 -->
      <el-menu
        :default-active="currentRoute"
        :collapse="systemStore.collapsed"
        :unique-opened="true"
        class="sidebar-menu"
        router
        @select="handleMenuSelect"
      >
        <!-- 仪表板 -->
        <el-menu-item index="/dashboard">
          <el-icon><Monitor /></el-icon>
          <template #title>仪表板</template>
        </el-menu-item>
        
        <!-- 系统管理 -->
        <el-sub-menu index="system">
          <template #title>
            <el-icon><Setting /></el-icon>
            <span>系统管理</span>
          </template>
          
          <el-menu-item index="/system/user">
            <el-icon><User /></el-icon>
            <template #title>用户管理</template>
          </el-menu-item>
          
          <el-menu-item index="/system/role">
            <el-icon><UserFilled /></el-icon>
            <template #title>角色管理</template>
          </el-menu-item>
          
          <el-menu-item index="/system/menu">
            <el-icon><Menu /></el-icon>
            <template #title>菜单管理</template>
          </el-menu-item>
          
          <el-menu-item index="/system/department">
            <el-icon><OfficeBuilding /></el-icon>
            <template #title>部门管理</template>
          </el-menu-item>

          <el-menu-item index="/system/logs">
            <el-icon><Operation /></el-icon>
            <template #title>日志管理</template>
          </el-menu-item>
        </el-sub-menu>
        
        <!-- 测试管理 -->
        <el-sub-menu index="test">
          <template #title>
            <el-icon><DataAnalysis /></el-icon>
            <span>测试管理</span>
          </template>
          
          <el-menu-item index="/test/cases">
            <el-icon><Document /></el-icon>
            <template #title>测试用例</template>
          </el-menu-item>
          
          <el-menu-item index="/test/reports">
            <el-icon><PieChart /></el-icon>
            <template #title>测试报告</template>
          </el-menu-item>
        </el-sub-menu>
        
        <!-- AI代理管理 -->
        <el-sub-menu index="agent">
          <template #title>
            <el-icon><Cpu /></el-icon>
            <span>AI代理管理</span>
          </template>
          
          <el-menu-item index="/agent/list">
            <el-icon><List /></el-icon>
            <template #title>代理列表</template>
          </el-menu-item>
          
          <el-menu-item index="/agent/config">
            <el-icon><Tools /></el-icon>
            <template #title>代理配置</template>
          </el-menu-item>
        </el-sub-menu>
        

      </el-menu>
    </div>
    
    <!-- 底部信息 -->
    <div class="sidebar-footer" v-if="!systemStore.collapsed">
      <div class="version-info">
        <span>版本 v1.0.0</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import {
  Monitor,
  Setting,
  User,
  UserFilled,
  Menu,
  OfficeBuilding,
  DataAnalysis,
  Document,
  PieChart,
  Cpu,
  List,
  Tools,
  Operation
} from '@element-plus/icons-vue'
import { useSystemStore } from '@/store'

const route = useRoute()
// const userStore = useUserStore() // 暂时注释掉未使用的store
const systemStore = useSystemStore()

// 当前路由
const currentRoute = computed(() => route.path)

// 处理菜单选择
const handleMenuSelect = (index: string) => {
  console.log('Selected menu:', index)
}
</script>

<style scoped lang="scss">
.app-sidebar {
  width: 250px;
  height: 100vh;
  background: #304156;
  transition: width 0.3s ease;
  position: fixed;
  left: 0;
  top: 60px;
  z-index: 998;
  display: flex;
  flex-direction: column;
  
  &.collapsed {
    width: 64px;
  }
  
  .sidebar-content {
    flex: 1;
    overflow-y: auto;
    overflow-x: hidden;
    
    &::-webkit-scrollbar {
      width: 6px;
    }
    
    &::-webkit-scrollbar-track {
      background: transparent;
    }
    
    &::-webkit-scrollbar-thumb {
      background: rgba(255, 255, 255, 0.2);
      border-radius: 3px;
      
      &:hover {
        background: rgba(255, 255, 255, 0.3);
      }
    }
  }
  
  .sidebar-menu {
    border-right: none;
    background: transparent;
    
    // 菜单项样式
    :deep(.el-menu-item) {
      color: #bfcbd9;
      border-left: 3px solid transparent;
      
      &:hover {
        background-color: #263445;
        color: #fff;
      }
      
      &.is-active {
        background-color: #409eff;
        color: #fff;
        border-left-color: #fff;
      }
      
      .el-icon {
        margin-right: 8px;
      }
    }
    
    // 子菜单样式
    :deep(.el-sub-menu) {
      .el-sub-menu__title {
        color: #bfcbd9;
        border-left: 3px solid transparent;
        
        &:hover {
          background-color: #263445;
          color: #fff;
        }
        
        .el-icon {
          margin-right: 8px;
        }
      }
      
      .el-menu {
        background-color: #1f2d3d;
        
        .el-menu-item {
          background-color: #1f2d3d;
          padding-left: 50px !important;
          
          &:hover {
            background-color: #001528;
          }
          
          &.is-active {
            background-color: #409eff;
            border-left-color: #fff;
          }
        }
      }
      
      &.is-opened .el-sub-menu__title {
        color: #fff;
      }
    }
    
    // 折叠状态样式
    &.el-menu--collapse {
      width: 64px;
      
      .el-sub-menu {
        .el-sub-menu__title {
          padding: 0 20px;
        }
      }
      
      .el-menu-item {
        padding: 0 20px;
      }
    }
  }
  
  .sidebar-footer {
    padding: 20px;
    border-top: 1px solid #434c5e;
    
    .version-info {
      text-align: center;
      color: #8492a6;
      font-size: 12px;
    }
  }
}

// 响应式设计
@media (max-width: 1200px) {
  .app-sidebar {
    width: 220px;

    &.collapsed {
      width: 64px;
    }
  }
}

@media (max-width: 992px) {
  .app-sidebar {
    width: 200px;

    &.collapsed {
      width: 64px;
    }
  }
}

@media (max-width: 768px) {
  .app-sidebar {
    transform: translateX(-100%);
    transition: transform 0.3s ease;
    width: 250px;
    z-index: 1000;

    &.mobile-open {
      transform: translateX(0);
    }

    &.collapsed {
      width: 250px;
    }
  }
}

@media (max-width: 576px) {
  .app-sidebar {
    width: 280px;

    &.mobile-open {
      transform: translateX(0);
    }
  }
}
</style>