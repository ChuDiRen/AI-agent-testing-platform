<!-- Breadcrumb.vue -->
<template>
  <div class="breadcrumb">
     <el-breadcrumb separator="/">
     <el-breadcrumb-item  to="/Statistics">首页</el-breadcrumb-item>
     <span v-for="(item, index) in breadcrumbs" :key="index">
      <router-link v-if="index < breadcrumbs.length - 1" :to="item.path">
        {{ item.meta.title }}
      </router-link>
      <span v-else>{{ item.meta.title }}</span>
    </span>
    </el-breadcrumb>
  </div>
</template>



<script>
export default {
  computed: {
    breadcrumbs() {
      return this.$route.matched.filter(route => route.meta?.title);
    },
  },
};
</script>

<style scoped>
.breadcrumb{
    margin-bottom: 20px;

}
</style>