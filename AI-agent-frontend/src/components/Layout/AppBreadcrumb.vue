<template>
  <div class="app-breadcrumb">
    <el-breadcrumb separator="/">
      <el-breadcrumb-item
        v-for="item in breadcrumbItems"
        :key="item.path"
        :to="item.path === currentPath ? undefined : item.path"
      >
        <el-icon v-if="item.icon" class="breadcrumb-icon">
          <component :is="item.icon" />
        </el-icon>
        {{ item.title }}
      </el-breadcrumb-item>
    </el-breadcrumb>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import {
  House,
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

const route = useRoute()

// 路由标题映射
const routeTitleMap: Record<string, { title: string; icon?: any }> = {
  '/': { title: '首页', icon: House },
  '/dashboard': { title: '仪表板', icon: Monitor },
  '/system': { title: '系统管理', icon: Setting },
  '/system/user': { title: '用户管理', icon: User },
  '/system/role': { title: '角色管理', icon: UserFilled },
  '/system/menu': { title: '菜单管理', icon: Menu },
  '/system/department': { title: '部门管理', icon: OfficeBuilding },
  '/test': { title: '测试管理', icon: DataAnalysis },
  '/test/cases': { title: '测试用例', icon: Document },
  '/test/reports': { title: '测试报告', icon: PieChart },
  '/agent': { title: 'AI代理管理', icon: Cpu },
  '/agent/list': { title: '代理列表', icon: List },
  '/agent/config': { title: '代理配置', icon: Tools },
  '/logs': { title: '日志管理', icon: Operation }
}

// 当前路径
const currentPath = computed(() => route.path)

// 面包屑项目
const breadcrumbItems = computed(() => {
  const pathArray = route.path.split('/').filter(path => path)
  const items: Array<{ path: string; title: string; icon?: any }> = []
  
  // 添加首页
  if (route.path !== '/') {
    items.push({
      path: '/',
      title: '首页',
      icon: House
    })
  }
  
  // 构建面包屑路径
  let currentPath = ''
  pathArray.forEach((path, index) => {
    currentPath += `/${path}`
    const routeInfo = routeTitleMap[currentPath]
    
    if (routeInfo) {
      items.push({
        path: currentPath,
        title: routeInfo.title,
        icon: routeInfo.icon
      })
    }
  })
  
  return items
})
</script>

<style scoped lang="scss">
.app-breadcrumb {
  padding: 15px 20px;
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
  
  :deep(.el-breadcrumb) {
    font-size: 14px;
    
    .el-breadcrumb__item {
      .el-breadcrumb__inner {
        display: flex;
        align-items: center;
        color: #606266;
        
        &:hover {
          color: #409eff;
        }
        
        .breadcrumb-icon {
          margin-right: 4px;
          font-size: 16px;
        }
      }
      
      &:last-child .el-breadcrumb__inner {
        color: #303133;
        font-weight: 500;
      }
    }
    
    .el-breadcrumb__separator {
      color: #c0c4cc;
    }
  }
}
</style>