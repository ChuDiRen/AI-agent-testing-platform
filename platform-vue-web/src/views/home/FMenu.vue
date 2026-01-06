<template>
  <div class="f-menu" :style="{width:$store.state.asideWidth}">

    <!--01 添加事件监听 @select="handleSelect-->
    <el-menu 
      unique-opened 
      :collapse="isCollapse" 
      :default-active="currentActive" 
      :default-openeds="defaultOpeneds"
      class="border-0" 
      @select="handleSelect" 
      :collapse-transition="false">
      <template v-for="(item,index) in asideMenus" :key="index">
        <el-sub-menu
          v-if="item.child && item.child.length > 0" :index="item.name">
          <template #title>
            <el-icon>
              <component :is="item.icon"></component>
            </el-icon>
            <span>{{ item.name }}</span>
          </template>
          <el-menu-item v-for="(item2, index2) in item.child" :key="index2" :index="item2.frontpath">
            <el-icon>
              <component :is="item2.icon"></component>
            </el-icon>
            <span>{{ item2.name }}</span>
        </el-menu-item>
        </el-sub-menu>
        <el-menu-item v-else :index="item.frontpath">
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
//03 为了跳转，要引入useRouter 
// 收起折叠功能 
import { computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router';
import {useStore} from 'vuex'
import { getUserMenus, getMenuTree } from '~/views/system/menu/menu'
import { addDynamicRoutes } from '~/router'

const router = useRouter()
const route = useRoute()
const store = useStore()

//是否折叠 - 只有64px和0px才是折叠状态
const isCollapse = computed(()=> {
  const width = store.state.asideWidth
  return width === '64px' || width === '0px'
})

//02 添加事件
const handleSelect =(e)=>{
 router.push(e)
}
// 获取菜单图标名称
function getIconName(iconName) {
  // 如果没有图标或图标为空，返回默认图标
  if (!iconName) {
    return 'Menu'
  }
  
  // 直接返回后端配置的图标名称
  // 后端已经存储的是 Element Plus 的图标组件名（如 'Key', 'User', 'Setting' 等）
  return iconName
}

// 已删除的路由列表（仅删除旧的AI对话系统）
const deletedRoutes = [
  '/ai-chat'
]

// 根据菜单类型和path/component字段生成前端路由路径
function getRoutePath(node) {
  // 如果是目录类型(M)且没有component和path，返回空字符串（不跳转）
  if (node.menu_type === 'M' && !node.component && !node.path) {
    return ''
  }
  
  // 判断path是否为前端路由格式（以/Api或/Test等大写字母开头）
  // 新增的菜单使用这种格式，如 /ApiProjectList, /ApiInfoCaseList
  const isRouterPath = node.path && /^\/[A-Z]/.test(node.path)
  
  if (isRouterPath) {
    // 过滤已删除的路由
    if (deletedRoutes.includes(node.path)) {
      return ''
    }
    return node.path
  }
  
  // 使用component字段生成路由路径
  // 与router/index.js保持一致：提取组件名作为路径
  if (node.component) {
    // component格式可能是 "userList" 或 "system/users/userList"
    // 提取最后的组件名作为路径
    const parts = node.component.split('/')
    const componentName = parts[parts.length - 1]
    const path = `/${componentName}`
    
    // 过滤已删除的路由
    if (deletedRoutes.includes(path)) {
      return ''
    }
    return path
  }
  
  // 其他情况返回空字符串
  return ''
}

// 将后端的菜单树转换为前端侧边栏结构
function transformMenuTree(tree){
  if(!Array.isArray(tree)) {
    return []
  }
  
  const processed = tree
    .filter(node => node.menu_type !== 'F') // 只要菜单和目录类型，过滤按钮(F)
    .filter(node => node.visible === '0' && node.status === '0') // 过滤隐藏和停用的菜单
    .sort((a,b) => (a.order_num||0) - (b.order_num||0))
    .map(node => {
      const routePath = getRoutePath(node)
      return {
        name: node.menu_name,
        icon: getIconName(node.icon), // 直接使用后端返回的图标名称
        frontpath: routePath, // 使用动态路径生成函数
        child: transformMenuTree(node.children||[])
      }
    })
    .filter(n => n.frontpath || (n.child && n.child.length > 0)) // 保留有路径或有子菜单的项
  
  // 去重：根据菜单名称和路径组合去重，保留第一个
  const seen = new Set()
  const deduplicated = processed.filter(item => {
    // 使用名称+路径作为唯一标识，如果路径为空则只使用名称
    const key = item.frontpath ? `${item.name}::${item.frontpath}` : item.name
    if (seen.has(key)) {
      return false // 已存在，过滤掉重复项
    }
    seen.add(key)
    return true
  })
  
  return deduplicated
}

// 兜底：刷新后如无菜单，尝试根据cookie中的用户ID拉取
onMounted(async ()=>{
  await loadMenuData()
})

// 加载菜单数据的统一函数
async function loadMenuData() {
  // 如果已有菜单数据，不重复加载
  if(store.state.menuTree && store.state.menuTree.length > 0){
    // 确保动态路由已注册
    addDynamicRoutes(store.state.menuTree)
    return
  }
  
  // 从 store 中获取用户ID
  const uid = store.state.userInfo?.id
  
  if(!uid){
    // 如果没有用户ID，尝试获取全量菜单
    try{
      const allRes = await getMenuTree()
      if(allRes?.data?.code === 200){
        const menuData = allRes.data.data || []
        store.commit('setMenuTree', menuData)
        // 动态注册路由
        addDynamicRoutes(menuData)
      }
    }catch(e){
      console.error('加载菜单失败:', e)
    }
    return
  }
  
  try{
    // 优先获取用户菜单
    const res = await getUserMenus(uid)
    if(res?.data?.code === 200){
      const tree = res.data.data || []
      if(tree.length > 0){
        store.commit('setMenuTree', tree)
        // 动态注册路由
        addDynamicRoutes(tree)
        return
      }
    }
    
    // 用户菜单为空，获取全量菜单作为兜底
    const allRes = await getMenuTree()
    if(allRes?.data?.code === 200){
      const menuData = allRes.data.data || []
      store.commit('setMenuTree', menuData)
      // 动态注册路由
      addDynamicRoutes(menuData)
    }
  }catch(e){
    console.error('加载菜单失败:', e)
    // 加载失败时，尝试获取全量菜单
    try{
      const allRes = await getMenuTree()
      if(allRes?.data?.code === 200){
        const menuData = allRes.data.data || []
        store.commit('setMenuTree', menuData)
        // 动态注册路由
        addDynamicRoutes(menuData)
      }
    }catch(err){
      console.error('加载全量菜单也失败:', err)
    }
  }
}

// 模块与顶级菜单名称的映射关系（精确匹配顶级菜单）
// 每个模块可以包含多个顶级菜单
// 测试计划和资源管理为公共模块，API 和 Web 共享
const moduleMenuMap = {
  'ai-assistant': ['AI配置'],
  'api-test': ['API自动化', '资源管理', '测试计划'],  // API测试包含资源管理和测试计划
  'web-test': ['Web自动化', '资源管理', '测试计划'],  // Web测试包含资源管理和测试计划（消息通知已集成在Web自动化内）
  'system': ['系统管理'],
  'generator': ['代码生成']
}

// 根据模块过滤顶级菜单
function filterMenusByModule(menus, moduleKey) {
  if (!moduleKey || !menus || menus.length === 0) {
    return menus
  }
  
  const allowedMenuNames = moduleMenuMap[moduleKey] || []
  
  // 只保留匹配的顶级菜单
  return menus.filter(menu => {
    return allowedMenuNames.includes(menu.name)
  })
}

// 菜单完全由后端生成，根据当前模块过滤
const asideMenus = computed(()=> {
  const menuTree = store.state.menuTree || []
  const transformed = transformMenuTree(menuTree)
  
  // 获取当前选择的模块
  const currentModule = store.state.currentModule
  
  // 如果没有选择模块，显示所有菜单
  if (!currentModule) {
    return transformed
  }
  
  // 根据模块过滤顶级菜单
  return filterMenusByModule(transformed, currentModule)
})

// 根据当前路由计算激活的菜单项
const currentActive = computed(() => {
  const currentPath = route.path
  
  // 遍历所有菜单项找到匹配的路径
  for (const menu of asideMenus.value) {
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
  
  return currentPath // 返回当前路径，不强制激活系统总览
})

// 根据当前路由计算需要展开的父菜单
const defaultOpeneds = computed(() => {
  const currentPath = route.path
  const openeds = []
  
  // 遍历所有菜单项找到包含当前路径的父菜单
  for (const menu of asideMenus.value) {
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
</style>

