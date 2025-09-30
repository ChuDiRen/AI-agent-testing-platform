<template>
  <div class="page-wrapper" :class="{ 'page-wrapper--fixed-height': fixedHeight }">
    <!-- 页面头部 -->
    <div v-if="$slots.header || title" class="page-header">
      <slot name="header">
        <div class="page-title">
          <AppIcon v-if="icon" :name="icon" :size="20" class="page-icon" />
          <h2>{{ title }}</h2>
        </div>
        <div v-if="$slots.extra" class="page-extra">
          <slot name="extra" />
        </div>
      </slot>
    </div>

    <!-- 页面内容 -->
    <div class="page-content" :class="contentClass">
      <slot />
    </div>

    <!-- 页面底部 -->
    <div v-if="$slots.footer" class="page-footer">
      <slot name="footer" />
    </div>
  </div>
</template>

<script setup>
import { AppIcon } from '@/components/icon'

defineProps({
  title: {
    type: String,
    default: '',
  },
  icon: {
    type: String,
    default: '',
  },
  fixedHeight: {
    type: Boolean,
    default: false,
  },
  contentClass: {
    type: String,
    default: '',
  },
})
</script>

<style scoped>
.page-wrapper {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--body-color);
}

.page-wrapper--fixed-height {
  height: 100vh;
  overflow: hidden;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 24px;
  border-bottom: 1px solid var(--border-color);
  background: var(--card-color);
  flex-shrink: 0;
}

.page-title {
  display: flex;
  align-items: center;
  gap: 8px;
}

.page-title h2 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-color-1);
}

.page-icon {
  color: var(--primary-color);
}

.page-extra {
  display: flex;
  align-items: center;
  gap: 12px;
}

.page-content {
  flex: 1;
  padding: 24px;
  overflow: auto;
}

.page-footer {
  padding: 16px 24px;
  border-top: 1px solid var(--border-color);
  background: var(--card-color);
  flex-shrink: 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .page-header {
    padding: 12px 16px;
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .page-content {
    padding: 16px;
  }

  .page-footer {
    padding: 12px 16px;
  }
}
</style>
