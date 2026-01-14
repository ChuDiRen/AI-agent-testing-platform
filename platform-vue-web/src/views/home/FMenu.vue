<template>
  <div class="f-menu" :style="{width: appStore.asideWidth}">

    <!--01 添加事件监听 @select="handleSelect-->
    <el-menu 
      unique-opened 
      :collapse="isCollapse" 
      :default-active="currentActive" 
      :default-openeds="defaultOpeneds"
      class="border-0"
      @select="handleSelect"
      :collapse-transition="false">
      <template v-for="item in asideMenus">
        <el-sub-menu
          v-if="item.child && item.child.length > 0" 
          :key="'sub-' + item.name" 
          :index="item.name">
          <template #title>
            <el-icon>
              <component :is="item.icon"></component>
            </el-icon>
            <span>{{ item.name }}</span>
          </template>
          <el-menu-item v-for="(item2, index2) in item.child" :key="item2.frontpath || index2" :index="item2.frontpath">
            <el-icon>
              <component :is="item2.icon"></component>
            </el-icon>
            <span>{{ item2.name }}</span>
        </el-menu-item>
        </el-sub-menu>
        <el-menu-item v-else :key="'item-' + item.name" :index="item.frontpath">
          <el-icon>
            <component :is="item.icon"></component>
          </el-icon>
          <span>{{ item.name }}</span>
        </el-menu-item>
      </template>
    </el-menu>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAppStore, useMenuStore } from '~/stores/index.js'
import { staticMenus } from '~/config/staticMenus'

const router = useRouter()
const route = useRoute()
const appStore = useAppStore()
const menuStore = useMenuStore()

//是否折叠 - 只有64px和0px才是折叠状态
const isCollapse = computed(()=> {
  const width = appStore.asideWidth
  return width === '64px' || width === '0px'
})

//02 添加事件
const handleSelect =(e)=>{
 router.push(e)
}

// 转换后端菜单数据为前端需要的格式
const transformMenuData = (menuList) => {
  return menuList.map(menu => {
    const transformed = {
      name: menu.menu_name,
      icon: menu.icon || 'Document',
      frontpath: menu.path || '',
      child: []
    }

    // 如果有子菜单，递归转换
    if (menu.children && menu.children.length > 0) {
      transformed.child = transformMenuData(menu.children)
    }

    return transformed
  })
}

// 使用动态菜单（优先），如果没有则使用静态菜单
const asideMenus = computed(()=> {
  const dynamicMenus = menuStore.menus
  if (dynamicMenus && dynamicMenus.length > 0) {
    return transformMenuData(dynamicMenus)
  }
  return staticMenus
})

// 根据当前路由计算激活的菜单项
const currentActive = computed(() => {
  const currentPath = route.path
  const menus = asideMenus.value

  // 遍历所有菜单项找到匹配的路径
  for (const menu of menus) {
    if (menu.frontpath === currentPath) {
      return menu.frontpath
    }

    // 检查子菜单
    if (menu.child && menu.child.length > 0) {
      for (const child of menu.child) {
        if (child.frontpath === currentPath) {
          return child.frontpath
        }
      }
    }
  }

  return currentPath
})

// 根据当前路由计算需要展开的父菜单
const defaultOpeneds = computed(() => {
  const currentPath = route.path
  const menus = asideMenus.value
  const openeds = []

  // 遍历所有菜单项找到包含当前路径的父菜单
  for (const menu of menus) {
    if (menu.child && menu.child.length > 0) {
      for (const child of menu.child) {
        if (child.frontpath === currentPath) {
          openeds.push(menu.name)
          break
        }
      }
    }
  }

  return openeds
})

// 组件挂载时获取用户菜单
onMounted(() => {
  if (menuStore.menus.length === 0) {
    menuStore.fetchUserMenus()
  }
})
</script>

<style scoped>
.f-menu {
  height: calc(100vh - 64px);
  overflow-y: auto;
  overflow-x: hidden;
  background: var(--bg-card);
  border-right: 1px solid var(--border-color);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: fixed;
  top: 64px;
  bottom: 0;
  left: 0;
  box-shadow: var(--shadow-md);
}

/* 自定义滚动条 */
.f-menu::-webkit-scrollbar {
  width: 6px;
}

.f-menu::-webkit-scrollbar-thumb {
  background: var(--border-color);
  border-radius: 3px;
}

.f-menu::-webkit-scrollbar-thumb:hover {
  background: var(--border-hover);
}

:deep(.el-menu) {
  border: none;
  background: transparent;
}

:deep(.el-menu-item),
:deep(.el-sub-menu__title) {
  transition: all 0.3s ease;
  border-radius: 8px;
  margin: 4px 8px;
  color: var(--text-primary);
  height: 48px;
  line-height: 48px;
}

:deep(.el-menu-item:hover),
:deep(.el-sub-menu__title:hover) {
  background: var(--bg-hover) !important;
  transform: translateX(4px);
  color: var(--primary-color);
}

:deep(.el-menu-item.is-active) {
  background: var(--primary-gradient) !important;
  color: white !important;
  box-shadow: var(--shadow-md);
  font-weight: 600;
}

:deep(.el-menu-item.is-active .el-icon) {
  color: white !important;
}

:deep(.el-sub-menu .el-icon) {
  color: var(--text-secondary);
}

:deep(.el-sub-menu__title) {
  font-weight: 500;
}

/* 折叠状态优化 */
:deep(.el-menu--collapse) {
  width: 64px;
}

:deep(.el-menu--collapse .el-menu-item),
:deep(.el-menu--collapse .el-sub-menu__title) {
  justify-content: center;
  padding: 0 !important;
}

/* 移动端适配 */
@media (max-width: 768px) {
  .f-menu {
    width: 250px;
    left: -250px;
    z-index: 999;
  }
  
  .f-menu.show {
    left: 0;
  }
  
  :deep(.el-menu-item),
  :deep(.el-sub-menu__title) {
    height: 50px;
    line-height: 50px;
  }
}

/* 小屏幕手机适配 */
@media (max-width: 480px) {
  .f-menu {
    width: 100%;
    max-width: 280px;
  }
  
  :deep(.el-menu-item),
  :deep(.el-sub-menu__title) {
    margin: 4px 6px;
    font-size: 14px;
  }
}

/* 平板适配 */
@media (min-width: 769px) and (max-width: 1024px) {
  :deep(.el-menu-item),
  :deep(.el-sub-menu__title) {
    height: 46px;
    line-height: 46px;
    margin: 3px 6px;
  }
}
</style>

