<script setup>
import { renderIcon } from '@/utils'

defineProps({
  icon: {
    type: String,
    default: '', // 允许icon为空,避免Vue警告
  },
  size: {
    type: Number,
    default: 14,
  },
  color: {
    type: String,
    default: undefined,
  },
})
</script>

<template>
  <component v-if="icon" :is="renderIcon(icon, { size, color })" />
</template>

