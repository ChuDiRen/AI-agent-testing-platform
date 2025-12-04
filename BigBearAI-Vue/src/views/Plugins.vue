<template>
  <div class="main-content">
    <header class="page-header">
      <h1 class="page-title">插件中心</h1>
      <p class="page-subtitle">扩展平台功能</p>
      <div class="header-actions">
        <div class="search-bar">
          <i class="ph ph-magnifying-glass"></i>
          <input type="text" placeholder="搜索插件...">
        </div>
        <button class="btn-primary">
          <i class="ph ph-puzzle-piece"></i>
          安装插件
        </button>
      </div>
    </header>

    <div class="card-grid">
      <UnifiedCard 
        v-for="plugin in plugins" 
        :key="plugin.id" 
        :item="plugin" 
        :options="{ 
          badgeText: plugin.type,
          showIcon: true, 
          iconName: plugin.icon 
        }"
      />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import MockData from '../data/data';
import UnifiedCard from '../components/UnifiedCard.vue';

const plugins = computed(() => MockData.plugins);
</script>
