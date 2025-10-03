<template>
     <el-result
        icon="warning"
        title="404警告"
        sub-title="非常抱歉,你的页面走丢了~~"
      >
        <template #extra>
          <el-button type="primary"  @click="$router.push('/Statistics')">回到首页</el-button>
        </template>
      </el-result>
</template>
