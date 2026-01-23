<template>
  <div id="app">
    <a href="#main-content" class="skip-to-content">跳转到主要内容</a>

    <!-- Authenticated Layout -->
    <MainLayout v-if="isAuthenticated">
      <template #default>
        <router-view />
      </template>
    </MainLayout>

    <!-- Unauthenticated Pages -->
    <router-view v-else />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import MainLayout from './components/Layout/MainLayout.vue'

const route = useRoute()

// Check if user is authenticated
const isAuthenticated = computed(() => {
  const token = localStorage.getItem('access_token')
  const isAuthRoute = route.path.startsWith('/auth')

  // If on auth route, show unauthenticated layout
  // If authenticated and not on auth route, show main layout
  return token && !isAuthRoute
})
</script>

<style>
#app {
  width: 100%;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}
</style>
