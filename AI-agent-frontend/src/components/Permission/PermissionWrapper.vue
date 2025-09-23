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
import { usePermission } from '@/utils/permission'

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

// 权限工具
const { hasPermission, hasAnyPermission, hasAllPermissions, hasRole, hasAnyRole } = usePermission()

// 复用统一的权限工具函数
const allowed = computed(() => {
  let permissionCheck = true
  let roleCheck = true

  if (props.permission) {
    const permissions = Array.isArray(props.permission) ? props.permission : [props.permission]
    permissionCheck = props.mode === 'every' 
      ? hasAllPermissions(permissions)
      : hasAnyPermission(permissions)
  }
  
  if (props.role) {
    const roles = Array.isArray(props.role) ? props.role : [props.role]
    roleCheck = props.mode === 'every'
      ? roles.every(role => hasRole(role))
      : hasAnyRole(roles)
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