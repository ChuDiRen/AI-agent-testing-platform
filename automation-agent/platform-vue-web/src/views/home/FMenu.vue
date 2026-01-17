<template>
  <div class="modern-sidebar">
    <!-- 菜单列表 -->
    <div class="menu-list">
      <template v-for="(item, index) in asideMenus" :key="index">
        <!-- 有子菜单的项 -->
        <div v-if="item.child && item.child.length > 0" class="menu-group">
          <div class="menu-group-title">
            <el-icon class="group-icon">
              <component :is="item.icon"></component>
            </el-icon>
            <span class="group-text">{{ item.name }}</span>
          </div>
          
          <div class="menu-items">
            <div
              v-for="(item2, index2) in item.child"
              :key="index2"
              :class="['menu-item', { 'active': isActive(item2.frontpath) }]"
              @click="handleSelect(item2.frontpath)"
            >
              <div class="item-indicator"></div>
              <el-icon class="item-icon">
                <component :is="item2.icon"></component>
              </el-icon>
              <span class="item-text">{{ item2.name }}</span>
            </div>
          </div>
        </div>
        
        <!-- 没有子菜单的项 -->
        <div
          v-else
          :class="['menu-item', { 'active': isActive(item.frontpath) }]"
          @click="handleSelect(item.frontpath)"
        >
          <div class="item-indicator"></div>
          <el-icon class="item-icon">
            <component :is="item.icon"></component>
          </el-icon>
          <span class="item-text">{{ item.name }}</span>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { useRouter, useRoute } from 'vue-router';
import { computed } from 'vue';

const router = useRouter();
const route = useRoute();

// 处理菜单选择 - 添加导航守卫
const handleSelect = (path) => {
  // 检查是否已经在这个路径
  if (route.path === path) {
    return;
  }
  console.log('导航到:', path);
  router.push(path);
};

// 判断菜单项是否激活
const isActive = (path) => {
  return route.path === path;
};

const asideMenus = [{
    "name":"数据统计",
    "icon":"DataAnalysis",
    "frontpath":"/Statistics"
  },{
    "name":"系统管理",
    "icon":"Tools",
    "child":[
        {
          "name":"用户管理",
          "icon":"User",
          "frontpath":"/userList"
        },
        {
          "name":"角色管理",
          "icon":"UserFilled",
          "frontpath":"/roleList"
        },
        {
          "name":"菜单管理",
          "icon":"Menu",
          "frontpath":"/menuList"
        },
        {
          "name":"部门管理",
          "icon":"OfficeBuilding",
          "frontpath":"/deptList"
        },
        {
          "name":"API管理",
          "icon":"Connection",
          "frontpath":"/apiList"
        },
        {
          "name":"审计日志",
          "icon":"DocumentChecked",
          "frontpath":"/auditLogList"
        }
    ]
 },{
     "name":"API自动化",
     "icon":"Promotion",
     "child":[
     {
        "name": "项目管理",
        "icon": "Tickets",
        "frontpath": "/ApiProjectList",
      },{
        "name": "关键字方法管理",
        "icon":"Key",
        "frontpath": "/ApiKeyWordList",
      },{
        "name": "素材维护管理",
        "icon":"Document",
        "frontpath": "/ApiMateManageList",
      },{
        "name": "接口信息维护",
        "icon": "Link",
        "frontpath": "/ApiInfoList",
      },{
        "name": "API用例信息管理",
        "icon": "Reading",
        "frontpath": "/ApiInfoCaseList",
      },{
        "name": "API测试计划管理",
        "icon": "Collection",
        "frontpath": "/ApiCollectionInfoList",
      },
      ]
  },{
    "name":"消息通知管理", 
    "icon":"Comment",
    "child":[
      {
        "name": "微信配置",
        "icon": "ChatSquare",
        "frontpath": "/WeChartMsgManageList",
      },{
        "name": "钉钉配置",
        "icon": "Coordinate",
        "frontpath": "/DingDingMsgManageList",
       },{
        "name": "飞书配置",
        "icon": "Position",
        "frontpath": "/FeiShuMsgManageList",
      }
  ]
}]
</script>

<style scoped>
.modern-sidebar {
  position: fixed;
  top: 70px;
  left: 0;
  bottom: 0;
  width: 250px;
  background: white;
  border-right: 1px solid var(--color-border);
  overflow-y: auto;
  overflow-x: hidden;
  transition: all var(--transition-base);
  z-index: var(--z-sticky);
}

/* 自定义滚动条 */
.modern-sidebar::-webkit-scrollbar {
  width: 6px;
}

.modern-sidebar::-webkit-scrollbar-track {
  background: transparent;
}

.modern-sidebar::-webkit-scrollbar-thumb {
  background: var(--color-border-dark);
  border-radius: var(--radius-full);
}

/* 菜单列表 */
.menu-list {
  padding: 1rem 0.75rem;
}

/* 菜单组 */
.menu-group {
  margin-bottom: 1.5rem;
}

.menu-group-title {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem 0.75rem;
  margin-bottom: 0.5rem;
  font-size: var(--text-xs);
  font-weight: 600;
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.group-icon {
  font-size: 16px;
  color: var(--color-text-muted);
}

.group-text {
  flex: 1;
}

/* 菜单项容器 */
.menu-items {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

/* 菜单项 */
.menu-item {
  position: relative;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  margin: 0 0.25rem;
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-base);
  user-select: none;
}

.menu-item:hover {
  background: var(--color-bg-hover);
  color: var(--color-primary);
}

.menu-item.active {
  background: rgba(37, 99, 235, 0.1);
  color: var(--color-primary);
  font-weight: 500;
}

/* 活动指示器 */
.item-indicator {
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 0;
  background: var(--color-primary);
  border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
  transition: height var(--transition-base);
}

.menu-item.active .item-indicator {
  height: 60%;
}

/* 图标 */
.item-icon {
  font-size: 18px;
  flex-shrink: 0;
  transition: transform var(--transition-base);
}

.menu-item:hover .item-icon {
  transform: scale(1.1);
}

.menu-item.active .item-icon {
  color: var(--color-primary);
}

/* 文本 */
.item-text {
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .modern-sidebar {
    transform: translateX(-100%);
  }
  
  .modern-sidebar.open {
    transform: translateX(0);
  }
}
</style>