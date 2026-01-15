<template>
    <el-result
        icon="error"
        title="500 服务器错误"
        sub-title="抱歉，服务器出现了一些问题，请稍后重试~~"
    >
        <template #extra>
            <el-button type="primary" @click="$router.push('/Statistics')">回到首页</el-button>
            <el-button @click="$router.go(-1)">返回上一页</el-button>
        </template>
    </el-result>
</template>

