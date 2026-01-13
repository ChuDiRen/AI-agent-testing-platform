<template>
  <div>
    <h3>今日学习列表</h3>
    <ul>
      <li v-for="(fruit, index) in fruits" :key="index">
        {{ index + 1 }}. {{ fruit }}
      </li>
    </ul>
  </div>
</template>

<script setup>
const fruits= ['软件测试基础', 'HTML', '数据库', '接口自动化', '性能测试']
</script>