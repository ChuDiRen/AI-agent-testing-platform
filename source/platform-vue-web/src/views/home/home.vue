<template>
    <el-container>
        <el-header>
            <f-header/>
        </el-header>
        <el-container>
            <el-aside :width="$store.state.asideWidth">
                <f-menu/>
            </el-aside>
            <el-main>
                <f-tag-list/>
                <router-view></router-view>
            </el-main>
        </el-container>
    </el-container>
</template>

<script setup>
import FHeader from './FHeader.vue';
import FMenu from './FMenu.vue';
import FTagList from './FTagList.vue'
</script>
<style scoped>
    .el-aside{
        transition: all 0.2s;
    }
</style>

