<template>
  <div class="main-content">
    <header class="page-header">
      <h1 class="page-title">Prompt 库</h1>
      <p class="page-subtitle">高效的提示词模板集合</p>
      <div class="header-actions">
        <div class="search-bar">
          <i class="ph ph-magnifying-glass"></i>
          <input type="text" placeholder="搜索 Prompt...">
        </div>
        <button class="btn-primary">
          <i class="ph ph-plus"></i>
          新建 Prompt
        </button>
      </div>
    </header>

    <div class="card-grid">
      <UnifiedCard 
        v-for="prompt in prompts" 
        :key="prompt.id" 
        :item="prompt" 
        :options="{ 
          badgeText: prompt.tags[0],
          showIcon: true, 
          iconName: prompt.icon,
          extraBadges: prompt.tags.slice(1)
        }"
      />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import MockData from '../data/data';
import UnifiedCard from '../components/UnifiedCard.vue';

const prompts = computed(() => MockData.prompts);
</script>
