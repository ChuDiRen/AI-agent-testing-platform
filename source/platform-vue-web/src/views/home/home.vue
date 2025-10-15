<template>
  <el-container class="layout-container">
    <el-header class="fixed-header">
      <f-header />
    </el-header>
    
    <el-container class="main-container">
      <el-aside :width="$store.state.asideWidth" :class="{ 'mobile-menu': isMobile, 'show': isMobile && menuVisible }">
        <f-menu />
      </el-aside>
      
      <el-main class="main-content">
        <f-tag-list />
        <router-view v-slot="{ Component }">
          <transition name="fade-slide" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
    
    <!-- 移动端遮罩 -->
    <div v-if="isMobile && menuVisible" class="mobile-overlay" @click="closeMenu"></div>
  </el-container>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useStore } from 'vuex'
import FHeader from './FHeader.vue'
import FMenu from './FMenu.vue'
import FTagList from './FTagList.vue'

const store = useStore()
const windowWidth = ref(window.innerWidth)

// 监听窗口大小变化
const handleResize = () => {
  windowWidth.value = window.innerWidth
}

onMounted(() => {
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})

const isMobile = computed(() => windowWidth.value < 768)
const menuVisible = computed(() => store.state.asideWidth === '250px')

const closeMenu = () => {
  if (isMobile.value) {
    store.commit('handleAsideWidth')
  }
}
</script>

<style scoped>
.layout-container {
  min-height: 100vh;
  background: var(--bg-secondary);
}

.fixed-header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  padding: 0;
  height: 64px;
}

.main-container {
  margin-top: 64px;
  min-height: calc(100vh - 64px);
}

.el-aside {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.main-content {
  background: var(--bg-secondary);
  min-height: calc(100vh - 64px);
  padding: 20px;
  transition: all 0.3s ease;
}

.mobile-overlay {
  position: fixed;
  top: 64px;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 998;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

/* 页面过渡动画 */
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.fade-slide-enter-from {
  opacity: 0;
  transform: translateX(20px);
}

.fade-slide-leave-to {
  opacity: 0;
  transform: translateX(-20px);
}

/* 移动端适配 */
@media (max-width: 768px) {
  .el-aside {
    position: fixed;
    left: -250px;
    top: 64px;
    bottom: 0;
    z-index: 999;
    box-shadow: var(--shadow-xl);
  }
  
  .el-aside.show {
    left: 0;
  }
  
  .main-content {
    padding: 12px;
    margin-left: 0 !important;
  }
}
</style>

