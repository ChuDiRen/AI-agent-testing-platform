<template>
    <div class="f-tag-list" :style="{ left:$store.state.asideWidth }">
        
        <!-- 使用<v-model>绑定对应的对象-->
        <el-tabs v-model="activeTab" type="card" class="flex-1"  @tab-remove="removeTab" style="min-width:100px;" @tab-change="changeTab">

            <!-- v-for 表示循环，自动生成对应的面板，:closable表示为/的路径不允许屏蔽-->
            <el-tab-pane v-for="item in tabList"   :closable="item.path!='/'"   :key="item.path" :label="item.title" :name="item.path"></el-tab-pane>
        </el-tabs>
        <!--这里是下拉选项的标准写法-->
        <!-- <span class="tag-btn">
            <el-dropdown>
                <span class="el-dropdown-link">
                    <el-icon>
                        <arrow-down />
                    </el-icon>
                </span>
                <template #dropdown>
                    <el-dropdown-menu>
                        <el-dropdown-item>关闭其他 </el-dropdown-item>
                        <el-dropdown-item>全部关闭 </el-dropdown-item>
                    </el-dropdown-menu>
                </template>
            </el-dropdown>
        </span> -->

    </div>
    <div style="height: 44px;"></div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useRoute, onBeforeRouteUpdate, useRouter } from 'vue-router'
import { useStore } from 'vuex'

const route = useRoute()
const router = useRouter()
const store = useStore()

// 定义好当前绑定的数据就是route中的path
const activeTab = ref(route.path)

// 从后端菜单数据生成标签页列表
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

// 监听菜单数据变化，更新标签页列表
const menuTabs = computed(() => {
  const menuTree = store.state.menuTree || []
  return menuToTabs(menuTree)
})

// 初始化标签页列表
function initTabList() {
  try {
    // 优先使用后端菜单数据
    if (menuTabs.value.length > 0) {
      tabList.value = [...menuTabs.value]
      console.log('使用菜单数据初始化标签页:', menuTabs.value)
    } else {
      // 回退到localStorage
      const tbs = JSON.parse(localStorage.getItem("tabList") || 'null')
      if (tbs && Array.isArray(tbs)) {
        tabList.value = tbs
        console.log('使用localStorage初始化标签页:', tbs)
      } else {
        // 最后回退到默认标签页
        tabList.value = [{
          title: '主页信息',
          path: '/Statistics'
        }]
        console.log('使用默认标签页')
      }
    }
    
    // 设置当前活动标签页
    activeTab.value = route.path || (tabList.value[0]?.path || '/Statistics')
    console.log('设置活动标签页:', activeTab.value)
  } catch (e) {
    console.error('初始化标签页失败:', e)
    activeTab.value = route.path || '/Statistics'
  }
}

// 监听菜单数据变化
watch(menuTabs, (newTabs) => {
  if (newTabs.length > 0) {
    console.log('菜单数据变化，新的标签页:', newTabs)
    // 保持当前已打开的标签页，但添加新的菜单标签页
    const currentPaths = tabList.value.map(tab => tab.path)
    const newTabsToAdd = newTabs.filter(tab => !currentPaths.includes(tab.path))
    
    if (newTabsToAdd.length > 0) {
      tabList.value = [...tabList.value, ...newTabsToAdd]
      // 保存到localStorage
      localStorage.setItem("tabList", JSON.stringify(tabList.value))
      console.log('添加新标签页:', newTabsToAdd)
    }
  }
}, { immediate: true })

// 延迟初始化，确保菜单数据加载完成
setTimeout(() => {
  initTabList()
}, 1000)

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
  if (t == tabs[0]?.path) return // 第一个tab不允许删除
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
</script>
<style scoped>
.f-tag-list{
    position: fixed;
    background-color: #f3f4f6;
    display: flex;
    align-items: center;
    padding-left: 8px;
    padding-right: 8px;
    top: 64px;
    right: 0;
    height: 44px;
    left: 260px;
    z-index: 100;
}
.tag-btn{
    background-color: white;
    border-radius: 4px;
    margin-left: auto;
    display: flex;
    align-items: center;
    justify-content: center;
    padding-left: 8px;
    padding-right: 8px;
    height: 32px;
}
:deep(.el-tabs__header){
    margin-bottom: 0;
}
:deep(.el-tabs__nav){
    border: 0!important;
}
:deep(.el-tabs__item){
    border: 0!important;
    height: 32px;
    line-height: 32px;
    background-color: white;
    margin-left: 4px;
    margin-right: 4px;
    border-radius: 4px;
}
:deep(.el-tabs__nav-next),:deep(.el-tabs__nav-prev){
    line-height: 32px;
    height: 32px;
}
:deep(.is-disabled){
    cursor: not-allowed;
    color: #d1d5db;
}
</style>