<template>
  <div class="query-bar-item">
    <label
      v-if="!isNullOrWhitespace(label)"
      class="query-label"
      :style="{ width: labelWidth + 'px' }"
    >
      {{ label }}
    </label>
    <div class="query-content" :style="{ width: contentWidth + 'px' }">
      <slot />
    </div>
  </div>
</template>

<script setup>
import { isNullOrWhitespace } from '@/utils'

defineProps({
  label: {
    type: String,
    default: '',
  },
  labelWidth: {
    type: Number,
    default: 80,
  },
  contentWidth: {
    type: Number,
    default: 220,
  },
})
</script>

<style scoped>
.query-bar-item {
  display: flex;
  align-items: center;
}

.query-label {
  flex-shrink: 0;
  margin-right: 8px;
  font-size: 14px;
  color: var(--text-color-2);
}

.query-content {
  flex: 1;
}
</style>
