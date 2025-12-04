<template>
  <div class="main-content">
    <header class="page-header">
      <h1 class="page-title">规则市场</h1>
      <p class="page-subtitle">探索和管理您的测试规则</p>
      <div class="header-actions">
        <div class="search-bar">
          <i class="ph ph-magnifying-glass"></i>
          <input type="text" placeholder="搜索规则...">
        </div>
        <button class="btn-primary">
          <i class="ph ph-plus"></i>
          新建规则
        </button>
      </div>
    </header>

    <!-- Official Rules -->
    <section style="margin-bottom: 40px;">
      <h2 class="section-title">官方推荐</h2>
      <div class="card-grid">
        <UnifiedCard 
          v-for="rule in officialRules" 
          :key="rule.id" 
          :item="rule" 
          :options="{ showIcon: true, iconName: 'scroll' }"
        />
      </div>
    </section>

    <!-- All Rules -->
    <section>
      <h2 class="section-title">全部规则</h2>
      <div class="card-grid">
        <UnifiedCard 
          v-for="rule in allRules" 
          :key="rule.id" 
          :item="rule" 
          :options="{ 
            showIcon: true, 
            iconName: 'scroll',
            extraBadges: rule.tags.slice(1)
          }"
        />
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import MockData from '../data/data';
import UnifiedCard from '../components/UnifiedCard.vue';

const officialRules = computed(() => MockData.rules.filter(r => r.tags.includes('官方')));
const allRules = computed(() => MockData.rules);
</script>
