<template>
  <component
    :is="iconComponent"
    v-if="iconComponent"
    :class="['app-icon', customClass]"
    :style="iconStyle"
  />
  <Icon
    v-else-if="name"
    :icon="name"
    :class="['app-icon', customClass]"
    :style="iconStyle"
  />
  <span v-else class="app-icon-placeholder">
    <Icon icon="mdi:help-circle-outline" />
  </span>
</template>

<script setup>
import { computed, defineAsyncComponent } from 'vue'
import { Icon } from '@iconify/vue'

const props = defineProps({
  name: {
    type: String,
    default: '',
  },
  size: {
    type: [String, Number],
    default: 16,
  },
  color: {
    type: String,
    default: '',
  },
  customClass: {
    type: String,
    default: '',
  },
  local: {
    type: Boolean,
    default: false,
  },
})

// 本地图标组件映射
const localIcons = {
  'logo': () => import('@/assets/icons/logo.vue'),
  'user': () => import('@/assets/icons/user.vue'),
  'setting': () => import('@/assets/icons/setting.vue'),
}

// 动态加载本地图标组件
const iconComponent = computed(() => {
  if (props.local && localIcons[props.name]) {
    return defineAsyncComponent(localIcons[props.name])
  }
  return null
})

// 图标样式
const iconStyle = computed(() => {
  const style = {}
  
  if (props.size) {
    const size = typeof props.size === 'number' ? `${props.size}px` : props.size
    style.width = size
    style.height = size
    style.fontSize = size
  }
  
  if (props.color) {
    style.color = props.color
  }
  
  return style
})
</script>

<style scoped>
.app-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  vertical-align: middle;
}

.app-icon-placeholder {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: var(--text-color-3);
  opacity: 0.5;
}
</style>
