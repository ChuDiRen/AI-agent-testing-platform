<template>
  <div class="main-content">
    <header class="page-header">
      <h1 class="page-title">智能体广场</h1>
      <p class="page-subtitle">发现并使用强大的AI智能体</p>
      <div class="header-actions">
        <div class="search-bar">
          <i class="ph ph-magnifying-glass"></i>
          <input type="text" placeholder="搜索智能体...">
        </div>
        <button class="btn-primary">
          <i class="ph ph-plus"></i>
          创建智能体
        </button>
      </div>
    </header>

    <div class="card-grid">
      <UnifiedCard 
        v-for="agent in agents" 
        :key="agent.id" 
        :item="agent" 
        :options="{ 
          badgeText: agent.type,
          showIcon: true, 
          iconName: agent.icon 
        }"
      />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import MockData from '../data/data';
import UnifiedCard from '../components/UnifiedCard.vue';

const agents = computed(() => MockData.agents);
</script>
