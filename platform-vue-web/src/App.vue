<template>
  <router-view v-slot="{ Component }">
    <component :is="Component" />
  </router-view>
</template>

<style>
/* 全局样式 */
body {
  background: var(--bg-secondary);
  color: var(--text-primary);
  margin: 0;
  padding: 0;
  font-family: Inter, system-ui, Avenir, Helvetica, Arial, sans-serif;
  transition: background-color 0.3s ease, color 0.3s ease;
}

#app {
  min-height: 100vh;
}

/* 页面切换动画 */
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

/* 进度条样式 */
#nprogress .bar {
  background: var(--primary-gradient) !important;
  height: 3px !important;
}

#nprogress .spinner-icon {
  border-top-color: var(--primary-color) !important;
  border-left-color: var(--primary-color) !important;
}

/* 滚动条样式 */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-corner {
  display: block;
}

::-webkit-scrollbar-thumb {
  border-radius: 8px;
  background: var(--border-color);
  transition: background 0.3s ease;
}

::-webkit-scrollbar-thumb:hover {
  background: var(--border-hover);
}

::-webkit-scrollbar-track {
  background: var(--bg-secondary);
}

/* 响应式布局 - 移动端适配 */
@media (max-width: 768px) {
  .el-aside {
    position: fixed;
    left: -250px;
    top: 64px;
    bottom: 0;
    z-index: 999;
    transition: left 0.3s ease;
  }
  
  .el-aside.show {
    left: 0;
  }
  
  .el-main {
    margin-left: 0 !important;
  }
  
  .page-container {
    padding: 12px;
  }
  
  .el-table {
    font-size: 12px;
  }
  
  .el-dialog {
    width: 90% !important;
  }
}

/* 响应式布局 - 平板适配 */
@media (min-width: 768px) and (max-width: 1024px) {
  .el-aside {
    width: 200px !important;
  }
  
  .page-container {
    padding: 16px;
  }
}

/* 响应式布局 - 大屏适配 */
@media (min-width: 1920px) {
  .page-container {
    /* 大屏幕充分利用空间，不限制最大宽度 */
    max-width: none;
    padding: 24px 32px;
  }
  
  .el-table {
    font-size: 14px;
  }
}

/* 超大屏幕适配 (2K+) */
@media (min-width: 2560px) {
  .page-container {
    padding: 32px 48px;
  }
  
  .el-table {
    font-size: 15px;
  }
}
</style>
