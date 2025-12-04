<template>
  <div class="main-content">
    <header class="page-header">
      <h1 class="page-title">知识库</h1>
      <p class="page-subtitle">管理您的文档和知识资源</p>
      <div class="header-actions">
        <div class="search-bar">
          <i class="ph ph-magnifying-glass"></i>
          <input type="text" placeholder="搜索知识...">
        </div>
        <button class="btn-primary">
          <i class="ph ph-upload-simple"></i>
          上传文档
        </button>
      </div>
    </header>

    <div class="card-grid">
      <UnifiedCard 
        v-for="item in knowledge" 
        :key="item.id" 
        :item="item" 
        :options="{ 
          badgeText: '文档',
          showIcon: true, 
          iconName: item.icon 
        }"
      />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import MockData from '../data/data';
import UnifiedCard from '../components/UnifiedCard.vue';

const knowledge = computed(() => MockData.knowledge);
</script>
