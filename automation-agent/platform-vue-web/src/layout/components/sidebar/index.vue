<template>
  <div class="sidebar-container">
    <!-- 菜单列表 -->
    <el-menu
      :default-active="activeMenu"
      :collapse="appStore.collapsed"
      :unique-opened="menuConfig.behavior.uniqueOpened"
      :collapse-transition="menuConfig.behavior.collapseTransition"
      class="sidebar-menu"
    >
      <template v-for="menu in permissionStore.menus" :key="menu.path">
        <!-- 有子菜单 -->
        <el-sub-menu v-if="hasVisibleChildren(menu)" :index="menu.path">
          <template #title>
            <el-icon v-if="menu.meta?.icon"><component :is="menu.meta.icon" /></el-icon>
            <span>{{ menu.meta?.title || menu.name }}</span>
          </template>
          <el-menu-item
            v-for="child in getVisibleChildren(menu)"
            :key="child.path"
            :index="child.path"
            @click="handleMenuClick(menu.path, child.path)"
          >
            <el-icon v-if="child.meta?.icon"><component :is="child.meta.icon" /></el-icon>
            <span>{{ child.meta?.title || child.name }}</span>
          </el-menu-item>
        </el-sub-menu>
        <!-- 无子菜单 -->
        <el-menu-item v-else :index="menu.path" @click="handleMenuClick(menu.path)">
          <el-icon v-if="menu.meta?.icon"><component :is="menu.meta.icon" /></el-icon>
          <span>{{ menu.meta?.title || menu.name }}</span>
        </el-menu-item>
      </template>
    </el-menu>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAppStore } from '@/store/modules/app'
import { usePermissionStore } from '@/store/modules/permission'
import { menuConfig } from '@/config/menu-config'

const route = useRoute()
const router = useRouter()
const appStore = useAppStore()
const permissionStore = usePermissionStore()

// 当前激活的菜单
const activeMenu = computed(() => {
  return route.path
})

// 菜单点击处理
const handleMenuClick = (parentPath, childPath) => {
  // 如果有子路径，构建完整路径；否则使用父路径
  let path
  if (childPath) {
    // 子路径是相对路径，需要与父路径拼接
    path = `${parentPath}/${childPath}`.replace('//', '/')
  } else {
    path = parentPath
  }
  if (route.path !== path) {
    router.push(path)
  }
}

// 检查是否有可见的子菜单
const hasVisibleChildren = (menu) => {
  if (!menu.children || menu.children.length === 0) {
    return false
  }
  return menu.children.some(child => !child.isHidden)
}

// 获取可见的子菜单
const getVisibleChildren = (menu) => {
  if (!menu.children) {
    return []
  }
  return menu.children.filter(child => !child.isHidden)
}
</script>

<style scoped>
.sidebar-container {
  height: 100%;
  overflow-y: auto;
  overflow-x: hidden;
}

.sidebar-menu {
  border-right: none;
  height: 100%;
}

.sidebar-menu:not(.el-menu--collapse) {
  width: 100%;
}

/* 菜单项样式 */
:deep(.el-menu-item),
:deep(.el-sub-menu__title) {
  height: 48px;
  line-height: 48px;
  font-size: 14px;
  color: #374151;
  transition: all 0.2s;
}

:deep(.el-menu-item:hover),
:deep(.el-sub-menu__title:hover) {
  background: #f3f4f6;
  color: #2563eb;
}

:deep(.el-menu-item.is-active) {
  background: rgba(37, 99, 235, 0.1);
  color: #2563eb;
  font-weight: 500;
}

/* 子菜单样式 */
:deep(.el-sub-menu .el-menu-item) {
  padding-left: 50px !important;
  height: 44px;
  line-height: 44px;
}

/* 折叠状态样式 */
:deep(.el-menu--collapse) {
  width: 64px;
}

:deep(.el-menu--collapse .el-sub-menu__title span),
:deep(.el-menu--collapse .el-menu-item span) {
  display: none;
}

:deep(.el-menu--collapse .el-sub-menu__icon-arrow) {
  display: none;
}

/* 图标样式 */
:deep(.el-icon) {
  font-size: 18px;
  margin-right: 10px;
  vertical-align: middle;
}

/* 滚动条样式 */
.sidebar-container::-webkit-scrollbar {
  width: 4px;
}

.sidebar-container::-webkit-scrollbar-thumb {
  background: #d1d5db;
  border-radius: 2px;
}

.sidebar-container::-webkit-scrollbar-track {
  background: transparent;
}
</style>

