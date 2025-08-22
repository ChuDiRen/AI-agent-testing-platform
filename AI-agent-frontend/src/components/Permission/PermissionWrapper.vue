<template>
  <div v-if="hasPermission" class="permission-wrapper">
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
import { useUserStore } from '@/store'

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

const userStore = useUserStore()

// 权限检查
const hasPermission = computed(() => {
  // 如果未登录，无权限
  if (!userStore.isLoggedIn) {
    return false
  }

  // 超级管理员拥有所有权限
  if (userStore.hasRole('admin') || userStore.hasRole('super_admin')) {
    return true
  }

  let permissionCheck = true
  let roleCheck = true

  // 检查权限
  if (props.permission) {
    const permissions = Array.isArray(props.permission) ? props.permission : [props.permission]
    
    if (props.mode === 'every') {
      permissionCheck = permissions.every(perm => userStore.hasPermission(perm))
    } else {
      permissionCheck = permissions.some(perm => userStore.hasPermission(perm))
    }
  }

  // 检查角色
  if (props.role) {
    const roles = Array.isArray(props.role) ? props.role : [props.role]
    
    if (props.mode === 'every') {
      roleCheck = roles.every(role => userStore.hasRole(role))
    } else {
      roleCheck = roles.some(role => userStore.hasRole(role))
    }
  }

  // 如果同时指定了权限和角色，两者都需要满足
  if (props.permission && props.role) {
    return permissionCheck && roleCheck
  }

  // 如果只指定了权限或角色，满足其一即可
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