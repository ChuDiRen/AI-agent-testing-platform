<template>
  <div class="modern-sidebar">
    <!-- 菜单列表 -->
    <div class="menu-list">
      <template v-for="(item, index) in filteredMenus" :key="index">
        <!-- 有子菜单的项 -->
        <div v-if="item.child && item.child.length > 0" class="menu-group">
          <div class="menu-group-title">
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
          <span class="item-text">{{ item.name }}</span>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { useRouter, useRoute } from 'vue-router';
import { computed, ref, onMounted } from 'vue';
import { usePermissionStore } from '@/store/modules';

const router = useRouter();
const route = useRoute();
const permissionStore = usePermissionStore();

// 处理菜单选择
const handleSelect = (path) => {
  if (route.path === path) {
    return;
  }
  router.push(path);
};

// 判断菜单项是否激活
const isActive = (path) => {
  return route.path === path;
};

/**
 * 将后端菜单数据转换为前端菜单格式
 */
function transformBackendMenus(backendMenus) {
  if (!backendMenus || !Array.isArray(backendMenus)) {
    return [];
  }

  const transformed = [];
  
  for (const menu of backendMenus) {
    // 检查是否有子菜单
    const hasChildren = menu.children && menu.children.length > 0;
    
    if (hasChildren) {
      // 有子菜单的项，转换为菜单组
      const transformedChildren = menu.children.map(child => ({
        name: child.name,
        icon: child.icon,
        frontpath: child.path
      }));
      
      transformed.push({
        name: menu.name,
        icon: menu.icon,
        child: transformedChildren
      });
    } else {
      // 没有子菜单的项，作为单个菜单项
      transformed.push({
        name: menu.name,
        icon: menu.icon,
        frontpath: menu.path
      });
    }
  }
  
  return transformed;
}

// 显示的菜单（使用Pinia store数据）
const filteredMenus = computed(() => {
  // 获取Pinia store中的菜单数据
  const menuRoutes = permissionStore.menus || [];

  // 如果有菜单数据，转换为显示格式
  if (menuRoutes && menuRoutes.length > 0) {
    // 将路由格式转换为菜单显示格式
    const transformedMenus = menuRoutes.map(menu => {
      if (menu.children && menu.children.length > 0) {
        return {
          name: menu.meta?.title || menu.name,
          icon: menu.meta?.icon,
          child: menu.children.filter(c => !c.isHidden).map(child => ({
            name: child.meta?.title || child.name,
            icon: child.meta?.icon,
            frontpath: child.path
          }))
        };
      } else {
        return {
          name: menu.meta?.title || menu.name,
          icon: menu.meta?.icon,
          frontpath: menu.path
        };
      }
    });
    return transformedMenus;
  }

  return [];
});

// 组件挂载时确保已加载权限
onMounted(async () => {
  try {
    // 如果 Pinia store 中没有菜单数据，加载它
    if (!permissionStore.accessRoutes || permissionStore.accessRoutes.length === 0) {
      await permissionStore.generateRoutes();
    }
  } catch (error) {
    console.error('加载权限失败:', error);
  }
});
</script>

<style scoped>
.modern-sidebar {
  position: fixed;
  top: 70px;
  left: 0;
  bottom: 0;
  width: 250px;
  background: white;
  border-right: 1px solid #e5e7eb;
  overflow-y: auto;
  overflow-x: hidden;
  z-index: 1000;
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
  font-size: 12px;
  font-weight: 600;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.05em;
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
  font-size: 14px;
  color: #374151;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  user-select: none;
}

.menu-item:hover {
  background: #f3f4f6;
  color: #2563eb;
}

.menu-item.active {
  background: rgba(37, 99, 235, 0.1);
  color: #2563eb;
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
  background: #2563eb;
  border-radius: 0 3px 3px 0;
  transition: height 0.2s;
}

.menu-item.active .item-indicator {
  height: 60%;
}

/* 图标 */
.item-icon {
  font-size: 18px;
  flex-shrink: 0;
  transition: transform 0.2s;
}

.menu-item:hover .item-icon {
  transform: scale(1.1);
}

.menu-item.active .item-icon {
  color: #2563eb;
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