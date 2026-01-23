<template>
  <div class="main-layout">
    <Sidebar
      :collapsed="sidebarCollapsed"
      @toggle-sidebar="toggleSidebar"
    />

    <div class="main-content" :class="{ 'sidebar-collapsed': sidebarCollapsed }">
      <Header
        :collapsed="sidebarCollapsed"
        @toggle-sidebar="toggleSidebar"
        @search="handleSearch"
      />

      <main class="page-content">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" :key="$route.path" />
          </transition>
        </router-view>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import Sidebar from './Sidebar.vue'
import Header from './Header.vue'

const sidebarCollapsed = ref(false)

function toggleSidebar() {
  sidebarCollapsed.value = !sidebarCollapsed.value
}

function handleSearch(query) {
  // Implement search functionality
}
</script>

<style scoped>
.main-layout {
  display: flex;
  min-height: 100vh;
  width: 100%;
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  margin-left: 292px; /* Sidebar (260) + Spacing (16*2) */
  transition: margin-left 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  padding-right: var(--space-4);
}

.main-content.sidebar-collapsed {
  margin-left: 112px; /* Sidebar (80) + Spacing (16*2) */
}

.page-content {
  padding: 0 var(--space-4) var(--space-6) var(--space-4);
  min-height: calc(100vh - 80px);
}

/* Page Transition */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}

.fade-enter-from {
  opacity: 0;
  transform: translateY(10px);
}
.fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

/* Responsive */
@media (max-width: 1024px) {
  .main-content {
    margin-left: 0;
    padding-left: var(--space-4);
  }
  
  .main-content.sidebar-collapsed {
    margin-left: 0;
  }
}
</style>
