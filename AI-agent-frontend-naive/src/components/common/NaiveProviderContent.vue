<template>
  <div></div>
</template>

<script setup>
// 获取全局组件实例
const dialog = useDialog()
const message = useMessage()
const notification = useNotification()
const loadingBar = useLoadingBar()

// 挂载到全局
window.$dialog = dialog
window.$message = message
window.$notification = notification
window.$loadingBar = loadingBar
</script>
