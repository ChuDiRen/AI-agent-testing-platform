<template>
  <div class="app-tags">
    <el-tabs v-model="activeTab" type="card" class="tags-tabs" @tab-remove="removeTab" @tab-change="changeTab">
      <el-tab-pane v-for="item in tabList" :key="item.path" :closable="item.path !== '/'" :label="item.title" :name="item.path" />
    </el-tabs>
    <span class="tag-btn">
      <el-dropdown>
        <span class="el-dropdown-link"><el-icon><ArrowDown /></el-icon></span>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item @click="clearAll">关闭所有</el-dropdown-item>
            <el-dropdown-item @click="clearOther">关闭其他</el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </span>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { useRoute, onBeforeRouteUpdate, useRouter } from 'vue-router'
import { usePermissionStore } from '@/store/modules/permission'

const route = useRoute()
const router = useRouter()
const permissionStore = usePermissionStore()

const activeTab = ref(route.path)
const tabList = ref([])

// 从路由菜单生成初始标签
const getInitialTabList = () => {
  const menus = permissionStore.menus || []
  const tabs = []
  const extractTabs = (items) => {
    items.forEach(menu => {
      if (menu.children?.length > 0) {
        menu.children.filter(c => !c.isHidden).forEach(child => {
          tabs.push({ title: child.meta?.title || child.name, path: `${menu.path}/${child.path}`.replace('//', '/') })
        })
      } else if (!menu.isHidden) {
        tabs.push({ title: menu.meta?.title || menu.name, path: menu.path })
      }
    })
  }
  extractTabs(menus)
  return tabs
}

// 添加标签
const addTab = (tab) => {
  if (!tabList.value.find(t => t.path === tab.path)) {
    tabList.value.push(tab)
    localStorage.setItem('tabList', JSON.stringify(tabList.value))
  }
}

// 切换标签
const changeTab = (path) => {
  activeTab.value = path
  router.push(path).catch(() => {})
}

// 删除标签
const removeTab = (path) => {
  if (tabList.value.length <= 1 || tabList.value[0]?.path === path) return
  const idx = tabList.value.findIndex(t => t.path === path)
  if (activeTab.value === path) {
    const nextTab = tabList.value[idx + 1] || tabList.value[idx - 1]
    if (nextTab) changeTab(nextTab.path)
  }
  tabList.value = tabList.value.filter(t => t.path !== path)
  localStorage.setItem('tabList', JSON.stringify(tabList.value))
}

// 关闭所有
const clearAll = () => {
  const initial = getInitialTabList()
  tabList.value = initial.length > 0 ? [initial[0]] : []
  if (tabList.value[0]) changeTab(tabList.value[0].path)
  localStorage.setItem('tabList', JSON.stringify(tabList.value))
}

// 关闭其他
const clearOther = () => {
  const home = tabList.value[0]
  const current = tabList.value.find(t => t.path === activeTab.value)
  tabList.value = current && current.path !== home?.path ? [home, current] : [home]
  localStorage.setItem('tabList', JSON.stringify(tabList.value))
}

// 路由更新时添加标签
onBeforeRouteUpdate((to) => {
  activeTab.value = to.path
  addTab({ title: to.meta?.title || to.name, path: to.path })
})

// 初始化
onMounted(() => {
  const saved = localStorage.getItem('tabList')
  if (saved) {
    try {
      tabList.value = JSON.parse(saved)
      if (tabList.value.length > 0 && !tabList.value.find(t => t.path === route.path)) {
        addTab({ title: route.meta?.title || route.name, path: route.path })
      }
    } catch { tabList.value = getInitialTabList() }
  } else {
    tabList.value = getInitialTabList()
  }
})

// 监听权限菜单变化
watch(() => permissionStore.menus, (menus) => {
  if (menus?.length > 0 && tabList.value.length === 0) {
    tabList.value = getInitialTabList()
    if (tabList.value[0]) changeTab(tabList.value[0].path)
  }
}, { deep: true })
</script>

<style scoped>
.app-tags {
  display: flex;
  align-items: center;
  padding: 8px 16px;
  background: #f3f4f6;
  border-bottom: 1px solid #e5e7eb;
}

.tags-tabs { flex: 1; min-width: 100px; }

.tag-btn {
  background: white;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 8px;
  height: 32px;
  margin-left: auto;
  cursor: pointer;
}

:deep(.el-tabs__header) { margin-bottom: 0; }
:deep(.el-tabs__nav) { border: 0 !important; }
:deep(.el-tabs__item) {
  border: 0 !important;
  height: 32px;
  line-height: 32px;
  background: white;
  margin: 0 4px;
  border-radius: 6px;
}
:deep(.el-tabs__nav-next), :deep(.el-tabs__nav-prev) { line-height: 32px; height: 32px; }
</style>

