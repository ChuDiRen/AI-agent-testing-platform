<template>
    <el-result
        icon="error"
        title="403 禁止访问"
        sub-title="抱歉，您没有权限访问此页面~~"
    >
        <template #extra>
            <el-button type="primary" @click="$router.push('/Statistics')">回到首页</el-button>
        </template>
    </el-result>
</template>

