<template>
  <div class="app-container">
    <Sidebar />
    <router-view></router-view>
  </div>
</template>

<script setup>
import Sidebar from './components/Sidebar.vue';
</script>

<style>
/* Global styles are imported in main.js */
</style>
