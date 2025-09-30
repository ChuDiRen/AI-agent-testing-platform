// 权限指令
const permission = {
  mounted(el, binding) {
    const { value } = binding
    const permissionStore = usePermissionStore()
    
    if (value && value instanceof Array && value.length > 0) {
      const hasPermission = value.some(permission => 
        permissionStore.apis.includes(permission)
      )
      
      if (!hasPermission) {
        el.style.display = 'none'
      }
    }
  },
  updated(el, binding) {
    const { value } = binding
    const permissionStore = usePermissionStore()
    
    if (value && value instanceof Array && value.length > 0) {
      const hasPermission = value.some(permission => 
        permissionStore.apis.includes(permission)
      )
      
      if (!hasPermission) {
        el.style.display = 'none'
      } else {
        el.style.display = ''
      }
    }
  }
}

// 防抖指令
const debounce = {
  mounted(el, binding) {
    let timer
    el.addEventListener('click', () => {
      if (timer) {
        clearTimeout(timer)
      }
      timer = setTimeout(() => {
        binding.value()
      }, binding.arg || 300)
    })
  }
}

// 节流指令
const throttle = {
  mounted(el, binding) {
    let timer
    el.addEventListener('click', () => {
      if (timer) {
        return
      }
      timer = setTimeout(() => {
        binding.value()
        timer = null
      }, binding.arg || 300)
    })
  }
}

export function setupDirectives(app) {
  app.directive('permission', permission)
  app.directive('debounce', debounce)
  app.directive('throttle', throttle)
}
