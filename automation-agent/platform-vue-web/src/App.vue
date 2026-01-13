<template>
  <div id="app">
    <!-- 路由出口：所有页面内容都会在这里渲染 -->
    <router-view />
  </div>
</template>

<style>
/* 全局样式 */
body {
  @apply bg-gray-100;
}

#nprogress .bar {
  background-color: #f4f4f4 !important;
  height: 3px !important;
}

::-webkit-scrollbar {
  width: 4px;
  height: 6px;
}

::-webkit-scrollbar-corner {
  display: block;
}
</style>