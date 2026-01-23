<template>
  <el-container>
    <el-header >
         <f-header/>
    </el-header>
    <el-container>
      <el-aside :width="asideWidth">
        <f-menu v-if="!isCollapsed"/> 
      </el-aside>
      <el-main>
        <f-tag-list/>
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" :key="$route.fullPath" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed } from 'vue';
import { useStore } from 'vuex';
import FHeader from './FHeader.vue'
import FMenu from './FMenu.vue'; 
import FTagList from './FTagList.vue';

const store = useStore();

// 使用计算属性避免响应式问题
const asideWidth = computed(() => store.state.asideWidth || '250px');
const isCollapsed = computed(() => store.state.asideWidth === '20px');
</script>

<style scoped>
    .el-aside{
        transition: all 0.2s;
    }
    
    /* 路由过渡动画 */
    .fade-enter-active,
    .fade-leave-active {
        transition: opacity 0.3s ease;
    }
    
    .fade-enter-from,
    .fade-leave-to {
        opacity: 0;
    }
</style>
