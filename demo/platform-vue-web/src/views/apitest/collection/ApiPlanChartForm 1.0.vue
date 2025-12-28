<template>
  <div class="button-container">
    <!--返回按钮 不写一个button 而是一个超链接-->
    <el-link type="primary" icon="el-icon-arrow-right" @click="goBack" :underline="false"><<返回主页面</el-link>
  </div>

  <div class="web-plan-chart">
    报表的详情内容
  </div>
</template>

<script setup>
import { ref, reactive } from "vue";
import { useRouter  } from "vue-router";

const router = useRouter();

 function goBack() {
      // 实现返回功能
     router.push("/ApiCollectionInfoList");
  }
</script>

<style scoped>
.button-container {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 20px;
}
</style>