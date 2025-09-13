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
        <!-- 仪表板 - 固定菜单 -->
        <el-menu-item index="/dashboard">
          <el-icon><Monitor /></el-icon>
          <template #title>仪表板</template>
        </el-menu-item>

        <!-- 动态菜单 -->
        <template v-for="menu in dynamicMenus" :key="menu.name">
          <!-- 有子菜单的情况 -->
          <el-sub-menu v-if="menu.children && menu.children.length > 0" :index="menu.name">
            <template #title>
              <el-icon>
                <component :is="getIconComponent(menu.meta?.icon)" />
              </el-icon>
              <span>{{ menu.meta?.title }}</span>
            </template>

            <!-- 子菜单项 -->
            <template v-for="child in menu.children" :key="child.name">
              <el-menu-item v-if="!child.meta?.hidden" :index="getFullPath(menu.path, child.path)">
                <el-icon v-if="child.meta?.icon">
                  <component :is="getIconComponent(child.meta.icon)" />
                </el-icon>
                <template #title>{{ child.meta?.title }}</template>
              </el-menu-item>
            </template>
          </el-sub-menu>

          <!-- 没有子菜单的情况 -->
          <el-menu-item v-else-if="!menu.meta?.hidden" :index="menu.path">
            <el-icon v-if="menu.meta?.icon">
              <component :is="getIconComponent(menu.meta.icon)" />
            </el-icon>
            <template #title>{{ menu.meta?.title }}</template>
          </el-menu-item>
        </template>

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
import { useSystemStore, usePermissionStore } from '@/store'

const route = useRoute()
const systemStore = useSystemStore()
const permissionStore = usePermissionStore()

// 当前路由
const currentRoute = computed(() => route.path)

// 动态菜单
const dynamicMenus = computed(() => {
  return permissionStore.menus.filter(menu =>
    menu.name !== 'Dashboard' && !menu.meta?.hidden
  )
})

// 图标组件映射
const iconMap: Record<string, any> = {
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
}

// 获取图标组件
const getIconComponent = (iconName?: string) => {
  if (!iconName) return Monitor // 默认图标
  return iconMap[iconName] || Monitor
}

// 处理菜单选择
const handleMenuSelect = (index: string) => {
  console.log('Selected menu:', index)
}

// 获取完整路径
const getFullPath = (parentPath: string, childPath: string) => {
  // 如果子路径是相对路径，则拼接父路径
  if (childPath && !childPath.startsWith('/')) {
    return `${parentPath}/${childPath}`
  }
  // 如果子路径已经是绝对路径，直接返回
  return childPath
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