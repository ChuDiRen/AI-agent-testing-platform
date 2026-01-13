<template>
    <div class="f-header">
        <!-- 内容1：显示文字 -->
        <span class="logo">
         <el-icon class="mr-1"><Opportunity /></el-icon>
         华测自动化测试平台
        </span>
        <!-- END 内容1：显示文字 -->

        <div class="icon-btn" @click="$store.commit('handleAsideWidth')">
        <!-- 内容2：显示收起/打开 按钮 -->
        <el-icon>
          <fold v-if="$store.state.asideWidth == '250px'"/>
          <Expand v-else/>
        </el-icon>
        </div>
         <!-- END 内容2：显示收起/打开 按钮 -->
        
        <!-- 内容3：右边下拉列表 -->
        <div class="ml-auto flex items-center">
          <el-dropdown>
            <span class="el-dropdown-link">
            <el-avatar :size="25" :src="circleUrl" />
            <el-icon class="el-icon--right">
           <arrow-down />
          </el-icon>
        </span>
        <template #dropdown>
            <el-dropdown-menu class="drop-down">
            <el-dropdown-item @click="handleLogout">退出登录</el-dropdown-item>
          </el-dropdown-menu>
        </template>
          </el-dropdown>
        </div>
         <!-- END 内容3：右边下拉列表 -->
    </div>
</template>

<script lang="ts" setup>

import { ElMessageBox } from 'element-plus';
import { reactive, toRefs } from 'vue'

import { useStore } from 'vuex' // 引入 useStore

const store = useStore() // 获取 store 实例

const state = reactive({
  circleUrl:
    'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png',
  squareUrl:
    'https://cube.elemecdn.com/9/c2/f0ee8a3c7c9638a54940382568c9dpng.png',
  sizeList: ['small', '', 'large'] as const,
})

const { circleUrl, squareUrl, sizeList } = toRefs(state)
// --------------扩展2 ： 退出功能 ------------------------
function handleLogout() {
  showModal("是否要退出登录？", "warning", "").then((res) => {
      // 清除本地token
      localStorage.removeItem('token');
      // 跳转到登录页
      window.location.href = '/login';
     // 提示退出登录成功
     // 这里可以添加退出登录成功的提示
  });
}


function showModal(content,type,title){
    return ElMessageBox.confirm(
        content,
        title,
        {
          confirmButtonText: '确认',
          cancelButtonText: '取消',
          type,
        }
      )
}
// --------------扩展2 ： 退出功能 ------------------------
</script>


<style>
 .f-header{
    @apply flex items-center bg-indigo-700 text-light-50 fixed top-0 left-0 right-0;
    height: 64px;
    z-index: 100;
 }
 .logo{
    width:250px;
    @apply flex justify-center items-center text-xl font-thin;
 }
 .icon-btn{
    @apply flex justify-center items-center;
    width: 42px;
    height: 64px;
    cursor:pointer;
 }
 .icon-btn:hover{
    @apply bg-indigo-600;
 }
 .f-header .drop-down{
    height: 64px;
    cursor: pointer;
    @apply flex justify-center items-center mx-5;
 }
</style>