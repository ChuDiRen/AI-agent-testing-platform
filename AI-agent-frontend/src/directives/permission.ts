/**
 * 权限控制指令
 * 使用方法：
 * v-permission="'user:add'" - 单个权限
 * v-permission="['user:add', 'user:edit']" - 多个权限（任一匹配）
 * v-permission:every="['user:add', 'user:edit']" - 多个权限（全部匹配）
 * v-role="'admin'" - 单个角色
 * v-role="['admin', 'user']" - 多个角色
 */

import type { App, DirectiveBinding } from 'vue'
import { hasPermission as checkPermissionUtil, hasRole as checkRoleUtil } from '@/utils/permission'

interface PermissionElement extends HTMLElement {
  _originalDisplay?: string
  _originalVisibility?: string
}

// 逻辑改为调用工具函数，避免重复实现

// 隐藏元素
function hideElement(el: PermissionElement) {
  if (!el._originalDisplay) {
    el._originalDisplay = el.style.display || ''
  }
  el.style.display = 'none'
}

// 显示元素
function showElement(el: PermissionElement) {
  if (el._originalDisplay !== undefined) {
    el.style.display = el._originalDisplay
  } else {
    el.style.display = ''
  }
}

// 权限指令
const permissionDirective = {
  mounted(el: PermissionElement, binding: DirectiveBinding) {
    const { value, arg, modifiers } = binding
    const mode = arg === 'every' ? 'every' : 'some'
    
    if (!value) {
      console.warn('v-permission directive requires a value')
      return
    }

    const allowed = checkPermissionUtil(value as any, mode as any)
    
    if (!allowed) {
      if (modifiers.hidden) {
        // 使用 visibility: hidden 隐藏（占位）
        if (!el._originalVisibility) {
          el._originalVisibility = el.style.visibility || ''
        }
        el.style.visibility = 'hidden'
      } else {
        // 使用 display: none 隐藏（不占位）
        hideElement(el)
      }
    } else {
      showElement(el)
      if (el._originalVisibility !== undefined) {
        el.style.visibility = el._originalVisibility
      }
    }
  },

  updated(el: PermissionElement, binding: DirectiveBinding) {
    const { value, arg, modifiers } = binding
    const mode = arg === 'every' ? 'every' : 'some'
    
    if (!value) {
      return
    }

    const allowed = checkPermissionUtil(value as any, mode as any)
    
    if (!allowed) {
      if (modifiers.hidden) {
        if (!el._originalVisibility) {
          el._originalVisibility = el.style.visibility || ''
        }
        el.style.visibility = 'hidden'
      } else {
        hideElement(el)
      }
    } else {
      showElement(el)
      if (el._originalVisibility !== undefined) {
        el.style.visibility = el._originalVisibility
      }
    }
  }
}

// 角色指令
const roleDirective = {
  mounted(el: PermissionElement, binding: DirectiveBinding) {
    const { value, arg, modifiers } = binding
    const mode = arg === 'every' ? 'every' : 'some'
    
    if (!value) {
      console.warn('v-role directive requires a value')
      return
    }

    const allowed = checkRoleUtil(value as any, mode as any)
    
    if (!allowed) {
      if (modifiers.hidden) {
        if (!el._originalVisibility) {
          el._originalVisibility = el.style.visibility || ''
        }
        el.style.visibility = 'hidden'
      } else {
        hideElement(el)
      }
    } else {
      showElement(el)
      if (el._originalVisibility !== undefined) {
        el.style.visibility = el._originalVisibility
      }
    }
  },

  updated(el: PermissionElement, binding: DirectiveBinding) {
    const { value, arg, modifiers } = binding
    const mode = arg === 'every' ? 'every' : 'some'
    
    if (!value) {
      return
    }

    const allowed = checkRoleUtil(value as any, mode as any)
    
    if (!allowed) {
      if (modifiers.hidden) {
        if (!el._originalVisibility) {
          el._originalVisibility = el.style.visibility || ''
        }
        el.style.visibility = 'hidden'
      } else {
        hideElement(el)
      }
    } else {
      showElement(el)
      if (el._originalVisibility !== undefined) {
        el.style.visibility = el._originalVisibility
      }
    }
  }
}

// 安装指令
export function setupPermissionDirectives(app: App) {
  app.directive('permission', permissionDirective)
  app.directive('role', roleDirective)
}

export { checkPermissionUtil as checkPermission, checkRoleUtil as checkRole }