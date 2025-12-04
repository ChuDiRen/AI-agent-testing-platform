<template>
  <div class="main-content">
    <header class="page-header">
      <h1 class="page-title">MCP 服务器</h1>
      <p class="page-subtitle">管理模型上下文协议连接</p>
      <div class="header-actions">
        <div class="search-bar">
          <i class="ph ph-magnifying-glass"></i>
          <input type="text" placeholder="搜索服务器...">
        </div>
        <button class="btn-primary">
          <i class="ph ph-plugs-connected"></i>
          添加服务器
        </button>
      </div>
    </header>

    <div class="card-grid">
      <UnifiedCard 
        v-for="item in mcpList" 
        :key="item.id" 
        :item="item" 
        :options="{ 
          badgeText: 'MCP',
          showIcon: true, 
          iconName: item.icon,
          showStatus: true,
          statusText: item.status
        }"
      />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import MockData from '../data/data';
import UnifiedCard from '../components/UnifiedCard.vue';

const mcpList = computed(() => MockData.mcp);
</script>
