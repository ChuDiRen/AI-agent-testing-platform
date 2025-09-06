<template>
  <div v-if="allowed" class="permission-wrapper">
    <slot />
  </div>
  <div v-else-if="fallback" class="permission-fallback">
    <slot name="fallback">
      {{ fallback }}
    </slot>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { hasPermission as hasPermUtil, hasRole as hasRoleUtil } from '@/utils/permission'

interface PermissionProps {
  // 权限标识
  permission?: string | string[]
  // 角色标识
  role?: string | string[]
  // 权限检查模式：'some' 任一匹配 | 'every' 全部匹配
  mode?: 'some' | 'every'
  // 回退内容
  fallback?: string
}

const props = withDefaults(defineProps<PermissionProps>(), {
  mode: 'some'
})

// 复用统一的权限工具函数
const allowed = computed(() => {
  let permissionCheck = true
  let roleCheck = true

  if (props.permission) {
    permissionCheck = hasPermUtil(props.permission, props.mode)
    }
  if (props.role) {
    roleCheck = hasRoleUtil(props.role, props.mode)
  }

  if (props.permission && props.role) return permissionCheck && roleCheck
  return props.permission ? permissionCheck : roleCheck
})
</script>

<style scoped lang="scss">
.permission-wrapper {
  display: contents;
}

.permission-fallback {
  color: #909399;
  font-size: 12px;
  font-style: italic;
}
</style>