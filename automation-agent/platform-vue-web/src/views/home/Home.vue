<template>
  <el-container>
    <el-header >
         <f-header/>
    </el-header>
    <el-container>
      <el-aside :width="$store.state.asideWidth">
      <!-- <el-aside style="width: 250px;" > -->
        <!-- 应用菜单cass -->
        <!-- <f-menu/> -->
        <f-menu v-show="$store.state.asideWidth !== '20px'"/> 
      </el-aside>
      <el-main>
        <f-tag-list/>
        <!-- 结合对应的路由进行显示 -->
        <router-view></router-view>  
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import FHeader from './FHeader.vue'
import FMenu from './FMenu.vue'; 
import FTagList from './FTagList.vue'; // 导入头部的Tag

// 打印$store.state.asideWidth的值



</script>

<style scoped>
    .el-aside{
        transition: all 0.2s;
    }
</style>
