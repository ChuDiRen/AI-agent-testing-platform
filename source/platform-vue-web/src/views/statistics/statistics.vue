<template>
    <div>
        欢迎来到首页，这是展示一些统计信息
        <!-- <el-button @click="addCount2" type="primary">保存</el-button> -->
    </div>
    
</template>
<script setup>
    import { useCookies } from '@vueuse/integrations/useCookies';
    const cookie = useCookies()
    
    console.log(cookie)
</script>
