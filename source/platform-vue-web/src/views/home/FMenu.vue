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
import { useCookies } from '@vueuse/integrations/useCookies'
import { getUserMenus, getMenuTree } from '~/views/system/menu/menu'
// import store from '../../store';
const router = useRouter()
const route = useRoute()
const store = useStore()

//是否折叠
const isCollapse = computed(()=>!(store.state.asideWidth== '250px'))

//02 添加事件
const handleSelect =(e)=>{
 //可以看看这里点击后事什么?
 console.log(e)
 router.push(e)
}
const cookies = useCookies()

// 图标映射（el-icon-xxx -> ElementPlus组件名）
const iconMap = {
  'el-icon-setting': 'Setting',
  'el-icon-tools': 'Tools',
  'el-icon-user': 'User',
  'el-icon-s-custom': 'UserFilled',
  'el-icon-menu': 'Menu',
  'el-icon-office-building': 'OfficeBuilding',
  'el-icon-document': 'Document',
  'el-icon-folder': 'Folder',
  'el-icon-document-copy': 'DocumentCopy',
  'el-icon-tickets': 'Tickets',
  'el-icon-key': 'Key',
  'el-icon-promotion': 'Promotion',
  'el-icon-monitor': 'Monitor'
}

// 路由映射（后端path -> 前端实际路由）
const routePathMap = {
  '/system': '', // 父级菜单不跳转
  '/system/user': '/userList',
  '/system/role': '/roleList',
  '/system/menu': '/menuList',
  '/system/dept': '/deptList',
  '/apitest': '', // 父级菜单不跳转
  '/apitest/project': '/ApiProjectList',
  '/apitest/keyword': '/ApiKeyWordList',
  '/apitest/mate': '/ApiMateManageList',
  '/apitest/apiinfo': '/ApiInfoList',
  '/apitest/apigroup': '/ApiGroupList',
  '/apitest/testhistory': '/ApiTestHistory',
}

// 将后端的菜单树转换为前端侧边栏结构
function transformMenuTree(tree){
  if(!Array.isArray(tree)) return []
  return tree
    .filter(node => node.type === '0') // 只要菜单类型，过滤按钮
    .sort((a,b) => (a.order_num||0) - (b.order_num||0))
    .map(node => ({
      name: node.menu_name,
      icon: iconMap[node.icon] || node.icon || 'Menu', // 映射图标
      frontpath: routePathMap[node.path] || '',
      child: transformMenuTree(node.children||[])
    }))
    .filter(n => n.frontpath || (n.child && n.child.length > 0)) // 保留有路径或有子菜单的项
}

// 兜底：刷新后如无菜单，尝试根据cookie中的用户ID拉取
onMounted(async ()=>{
  if(!store.state.menuTree || store.state.menuTree.length === 0){
    const uid = cookies.get('l-user-id')
    if(uid){
      try{
        const res = await getUserMenus(uid)
        if(res?.data?.code === 200){
          const tree = res.data.data || []
          if(tree.length > 0){
            store.commit('setMenuTree', tree)
          }else{
            const allRes = await getMenuTree()
            if(allRes?.data?.code === 200){
              store.commit('setMenuTree', allRes.data.data || [])
            }
          }
        }
      }catch(e){}
    }
  }
})

const fixedMenus = computed(()=> [{ name:'系统总览', icon:'Monitor', frontpath:'/Statistics' }])
const asideMenus = computed(()=> [...fixedMenus.value, ...transformMenuTree(store.state.menuTree)])

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
  
  return '/Statistics' // 默认激活系统总览
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

