<template>
  <div class="query-bar">
    <NSpace wrap :size="[35, 15]">
      <slot />
      <div class="query-actions">
        <NButton secondary type="primary" @click="emit('reset')">
          <template #icon>
            <Icon name="mdi:refresh" />
          </template>
          重置
        </NButton>
        <NButton type="primary" @click="emit('search')" style="margin-left: 12px">
          <template #icon>
            <Icon name="mdi:magnify" />
          </template>
          搜索
        </NButton>
      </div>
    </NSpace>
  </div>
</template>

<script setup>
import { Icon } from '@iconify/vue'

const emit = defineEmits(['search', 'reset'])
</script>

<style scoped>
.query-bar {
  background: #fafafc;
  min-height: 60px;
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  border: 1px solid #ccc;
  border-radius: 8px;
  padding: 15px;
}

.dark .query-bar {
  background: #18181c;
  border-color: #262628;
}

.query-actions {
  display: flex;
  align-items: center;
  flex-shrink: 0;
}
</style>
