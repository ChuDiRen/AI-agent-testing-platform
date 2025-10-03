<!-- Copyright (c) 2025 左岚. All rights reserved. -->
<template>
  <div class="test-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>测试页面</span>
          <el-button type="primary" :icon="Plus">测试按钮</el-button>
        </div>
      </template>
      
      <div class="content">
        <el-alert
          title="Layout测试"
          type="success"
          description="如果您能看到这个页面，说明Layout组件已经正常工作！"
          show-icon
          :closable="false"
        />
        
        <div class="icon-test" style="margin-top: 20px;">
          <h3>图标测试：</h3>
          <el-space>
            <el-button :icon="Plus">Plus</el-button>
            <el-button :icon="Edit">Edit</el-button>
            <el-button :icon="Delete">Delete</el-button>
            <el-button :icon="Search">Search</el-button>
            <el-button :icon="Refresh">Refresh</el-button>
          </el-space>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
// Copyright (c) 2025 左岚. All rights reserved.
import { Plus, Edit, Delete, Search, Refresh } from '@element-plus/icons-vue'
</script>

<style scoped>
.test-page {
  padding: 24px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.content {
  padding: 20px 0;
}
</style>
