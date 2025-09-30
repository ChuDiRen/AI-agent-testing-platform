<template>
  <div class="app-page" :class="{ 'show-footer': showFooter }">
    <div class="app-page-content">
      <slot />
    </div>
    <div v-if="showFooter" class="app-page-footer">
      <slot name="footer">
        <div class="footer-content">
          <p>&copy; 2025 AI Agent Testing Platform. All rights reserved.</p>
        </div>
      </slot>
    </div>
  </div>
</template>

<script setup>
defineProps({
  showFooter: {
    type: Boolean,
    default: true,
  },
})
</script>

<style scoped>
.app-page {
  display: flex;
  flex-direction: column;
  min-height: 100%;
}

.app-page-content {
  flex: 1;
  padding: 16px;
}

.app-page-footer {
  margin-top: auto;
  padding: 16px;
  border-top: 1px solid var(--border-color);
  background-color: var(--body-color);
}

.footer-content {
  text-align: center;
  color: var(--text-color-3);
  font-size: 14px;
}

.footer-content p {
  margin: 0;
}
</style>
