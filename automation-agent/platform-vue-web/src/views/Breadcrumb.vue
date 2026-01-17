<!-- Breadcrumb.vue -->
<template>
  <div class="breadcrumb">
    <el-breadcrumb separator="/">
      <el-breadcrumb-item to="/Statistics">首页</el-breadcrumb-item>
      <el-breadcrumb-item v-for="(item, index) in breadcrumbs" :key="index">
        {{ item.meta?.title || item.title }}
      </el-breadcrumb-item>
    </el-breadcrumb>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

const breadcrumbs = computed(() => {
  // 获取当前路由的所有匹配记录，过滤掉根路由和没有 title 的路由
  const matched = route.matched.filter(r => r.path !== '/' && r.path !== '/home' && (r.meta?.title || r.title))
  // 过滤掉重复的路由记录
  const seen = new Set()
  return matched.filter(r => {
    const key = r.path
    if (seen.has(key)) return false
    seen.add(key)
    return true
  })
})
</script>

<style scoped>
.breadcrumb {
  margin-bottom: 20px;
}
</style>