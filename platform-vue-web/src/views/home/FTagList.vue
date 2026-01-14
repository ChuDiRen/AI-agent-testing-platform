<template>
    <!-- eslint-disable-next-line vue/no-multiple-template-root -->
    <div class="f-tag-list" :style="tagListStyle">
        <el-tabs v-model="activeTab" type="card" class="flex-1" @tab-remove="removeTab" @tab-change="changeTab">
            <el-tab-pane
                v-for="item in tabList"
                :closable="item.path!='/'"
                :key="item.path"
                :label="item.title"
                :name="item.path">
            </el-tab-pane>
        </el-tabs>
        
        <!-- 标签操作下拉菜单 -->
        <el-dropdown v-if="tabList.length > 1" @command="handleTagCommand">
            <span class="tag-btn">
                <el-icon><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
                <el-dropdown-menu>
                    <el-dropdown-item command="closeOthers">关闭其他</el-dropdown-item>
                    <el-dropdown-item command="closeAll">全部关闭</el-dropdown-item>
                </el-dropdown-menu>
            </template>
        </el-dropdown>
    </div>
    <!-- eslint-disable-next-line vue/no-multiple-template-root -->
    <div class="tag-list-placeholder"></div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute, onBeforeRouteUpdate, useRouter } from 'vue-router'
import { staticMenus } from '~/config/staticMenus'
import { useAppStore } from '~/stores/index.js'

const route = useRoute()
const router = useRouter()
const appStore = useAppStore()

// 定义好当前绑定的数据就是route中的path
const activeTab = ref(route.path)

// 计算 f-tag-list 的 left 样式 - 响应式调整
const tagListStyle = computed(() => {
  const width = window.innerWidth
  const isMobile = width < 768
  return {
    left: isMobile ? '0' : appStore.asideWidth
  }
})

// 从静态菜单配置生成标签页列表
const tabList = ref([])

// 将菜单树转换为扁平的标签页列表
function menuToTabs(menus) {
  const tabs = []
  
  function traverse(items) {
    items.forEach(item => {
      if (item.frontpath && item.frontpath !== '/') {
        tabs.push({
          title: item.name,
          path: item.frontpath
        })
      }
      if (item.child && item.child.length > 0) {
        traverse(item.child)
      }
    })
  }
  
  traverse(menus)
  return tabs
}

// 从静态菜单生成标签页列表
const menuTabs = computed(() => {
  return menuToTabs(staticMenus)
})

// 初始化标签页列表
function initTabList() {
  try {
    if (menuTabs.value.length > 0) {
      tabList.value = [...menuTabs.value]
    } else {
      tabList.value = [{
        title: '主页信息',
        path: '/Statistics'
      }]
    }
    activeTab.value = route.path || (tabList.value[0]?.path || '/Statistics')
  } catch (e) {
    console.error('初始化标签页失败:', e)
    activeTab.value = route.path || '/Statistics'
  }
}

initTabList()

function addTab(tab) {
  if (!tab.path.endsWith("Form")) {
    let noTab = tabList.value.findIndex(t => t.path == tab.path) == -1
    if (noTab) {
      tabList.value.push(tab)
    }
    localStorage.setItem("tabList", JSON.stringify(tabList.value))
  }
}

onBeforeRouteUpdate((to) => {
  if (!to.path.endsWith("Form")) {
    activeTab.value = to.path
    addTab({
      title: to.meta.title,
      path: to.path
    })
  }
})

const changeTab = (t) => {
  if (!t.endsWith("Form")) {
    activeTab.value = t
    try {
      if (t !== route.path) {
        router.replace(t)
      }
    } catch (error) {
      console.error('导航失败:', error)
    }
  }
}

const removeTab = (t) => {
  let tabs = tabList.value
  if (t == tabs[0]?.path) return
  let a = activeTab.value
  if (a == t) {
    tabs.forEach((tab, index) => {
      if (tab.path == t) {
        const nextTab = tabs[index + 1] || tabs[index - 1]
        if (nextTab) {
          a = nextTab.path
        }
      }
    })
  }
  changeTab(a)
  tabList.value = tabList.value.filter(tab => tab.path != t)
  localStorage.setItem("tabList", JSON.stringify(tabList.value))
}

// 标签操作命令处理
const handleTagCommand = (command) => {
  if (command === 'closeOthers') {
    const currentTab = tabList.value.find(t => t.path === activeTab.value)
    if (currentTab) {
      tabList.value = [currentTab]
    }
    localStorage.setItem("tabList", JSON.stringify(tabList.value))
  } else if (command === 'closeAll') {
    tabList.value = tabList.value.slice(0, 1)
    activeTab.value = tabList.value[0]?.path
    changeTab(activeTab.value)
    localStorage.setItem("tabList", JSON.stringify(tabList.value))
  }
}
</script>
<style scoped>
.f-tag-list {
  position: fixed;
  top: 64px;
  right: 0;
  height: 44px;
  z-index: 99;
  display: flex;
  align-items: center;
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-color);
  padding: 0 12px;
  transition: left 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: var(--shadow-sm);
}

.tag-list-placeholder {
  height: 44px;
}

.tag-btn {
  background-color: white;
  border-radius: 4px;
  margin-left: auto;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 8px;
  height: 32px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: var(--shadow-sm);
}

.tag-btn:hover {
  background: var(--bg-hover);
  transform: scale(1.05);
}

:deep(.el-tabs__header) {
  margin-bottom: 0;
  border: none;
  flex: 1;
  overflow-x: auto;
}

:deep(.el-tabs__nav-wrap) {
  padding: 0;
}

:deep(.el-tabs__nav-wrap::after) {
  display: none;
}

:deep(.el-tabs__nav) {
  border: none !important;
  border-radius: 0;
}

:deep(.el-tabs__item) {
  border: none !important;
  height: 32px;
  line-height: 32px;
  background-color: white;
  margin: 6px 4px 6px 0;
  border-radius: 4px;
  padding: 0 16px;
  font-size: 13px;
  color: var(--text-primary);
  transition: all 0.3s ease;
  white-space: nowrap;
}

:deep(.el-tabs__item:hover) {
  background: var(--bg-hover);
  color: var(--primary-color);
}

:deep(.el-tabs__item.is-active) {
  background: var(--primary-gradient);
  color: white !important;
  box-shadow: var(--shadow-sm);
}

:deep(.el-tabs__item .el-icon-close) {
  width: 14px;
  height: 14px;
  margin-left: 8px;
  border-radius: 50%;
  transition: all 0.3s ease;
}

:deep(.el-tabs__item .el-icon-close:hover) {
  background: rgba(255, 255, 255, 0.3);
}

:deep(.el-tabs__nav-next),
:deep(.el-tabs__nav-prev) {
  line-height: 32px;
  height: 32px;
  display: flex;
  align-items: center;
}

:deep(.is-disabled) {
  cursor: not-allowed;
  color: var(--text-disabled);
}

/* 响应式适配 */
@media (max-width: 768px) {
  .f-tag-list {
    left: 0 !important;
    padding: 0 8px;
  }
  
  :deep(.el-tabs__item) {
    font-size: 12px;
    padding: 0 12px;
  }
  
  .tag-btn {
    width: 28px;
    height: 28px;
    padding: 0;
  }
}

@media (max-width: 480px) {
  .f-tag-list {
    height: 40px;
    padding: 0 4px;
  }
  
  .tag-list-placeholder {
    height: 40px;
  }
  
  :deep(.el-tabs__item) {
    font-size: 11px;
    padding: 0 8px;
    height: 28px;
    line-height: 28px;
    margin: 6px 2px 6px 0;
  }
  
  .tag-btn {
    display: none;
  }
}

/* 平板适配 */
@media (min-width: 769px) and (max-width: 1024px) {
  .f-tag-list {
    padding: 0 16px;
  }
  
  :deep(.el-tabs__item) {
    padding: 0 14px;
  }
}
</style>