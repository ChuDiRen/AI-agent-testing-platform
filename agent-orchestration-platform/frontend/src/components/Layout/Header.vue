<template>
  <header class="header">
    <div class="header-content">
      <!-- Left Side -->
      <div class="header-left">
        <button
          class="toggle-btn"
          @click="toggleSidebar"
          :aria-label="collapsed ? 'Expand sidebar' : 'Collapse sidebar'"
          aria-expanded="!collapsed"
        >
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="menu-icon">
            <path d="M3 12h18M3 6h18M3 18h18" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          </svg>
        </button>

        <h1 class="page-title text-glow">{{ pageTitle }}</h1>
      </div>

      <!-- Right Side -->
      <div class="header-right">
        <!-- Search -->
        <div class="search-box glass-card">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="search-icon">
            <circle cx="11" cy="11" r="8" stroke="currentColor" stroke-width="2"/>
            <path d="M21 21l-4.35-4.35" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          </svg>
          <input
            type="text"
            v-model="searchQuery"
            placeholder="Search..."
            class="search-input"
            @input="handleSearch"
            aria-label="搜索"
          />
        </div>

        <!-- Notifications -->
        <button class="icon-btn glass-card" aria-label="通知">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="bell-icon">
            <path d="M18 8A6 6 0 006 8c0 7-3 9-3 9h18s-3-2-3-9" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M13.73 21a2 2 0 01-3.46 0" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          <span v-if="notificationCount > 0" class="notification-badge">{{ notificationCount }}</span>
        </button>

        <!-- Help -->
        <button class="icon-btn glass-card" aria-label="帮助">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="help-icon">
            <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
            <path d="M9.09 9a3 3 0 015.83 1c0 2-3 3-3 3" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M12 17h.01" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>
      </div>
    </div>
  </header>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useRoute } from 'vue-router'

const props = defineProps({
  collapsed: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['toggle-sidebar', 'search'])

const route = useRoute()
const searchQuery = ref('')
const notificationCount = ref(3)

const pageTitle = computed(() => {
  const titles = {
    '/agents': 'Intelligent Agents',
    '/workflows': 'Workflows',
    '/tools': 'Tool Management',
    '/monitoring': 'Execution Monitoring',
    '/billing': 'Cost & Quota'
  }

  // Find matching title
  const path = Object.keys(titles).find(path => route.path.startsWith(path))
  return titles[path] || 'Dashboard'
})

function toggleSidebar() {
  emit('toggle-sidebar')
}

function handleSearch(event) {
  emit('search', event.target.value)
}

// Clear search when route changes
watch(() => route.path, () => {
  searchQuery.value = ''
})
</script>

<style scoped>
.header {
  position: sticky;
  top: 0;
  height: 80px;
  background: transparent;
  z-index: 900;
  transition: all 0.3s ease;
}

.header-content {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 var(--space-8);
  margin-left: 292px; /* Sidebar (260) + Spacing (16*2) */
  transition: margin-left 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.sidebar-collapsed + .main-content .header-content {
  margin-left: 112px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: var(--space-4);
}

.toggle-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border: none;
  background: rgba(255, 255, 255, 0.05);
  color: var(--color-text-secondary);
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: all 0.2s ease-out;
  backdrop-filter: blur(4px);
}

.toggle-btn:hover {
  background-color: var(--color-primary);
  color: white;
  box-shadow: 0 0 10px rgba(139, 92, 246, 0.4);
}

.menu-icon {
  width: 24px;
  height: 24px;
}

.page-title {
  font-size: 1.5rem;
  font-weight: 700;
  font-family: 'Space Grotesk', sans-serif;
  color: var(--color-text-primary);
  margin: 0;
  letter-spacing: -0.02em;
}

.header-right {
  display: flex;
  align-items: center;
  gap: var(--space-4);
}

.search-box {
  position: relative;
  display: flex;
  align-items: center;
  padding: 0 var(--space-3);
  height: 40px;
  width: 300px;
  transition: width 0.3s ease;
}

.search-box:focus-within {
  width: 360px;
  border-color: var(--color-primary);
  box-shadow: 0 0 10px rgba(139, 92, 246, 0.2);
}

.search-icon {
  position: absolute;
  left: var(--space-3);
  width: 18px;
  height: 18px;
  color: var(--color-text-muted);
  pointer-events: none;
}

.search-input {
  width: 100%;
  border: none;
  background: transparent;
  color: var(--color-text-primary);
  font-family: var(--font-body);
  font-size: var(--text-sm);
  padding-left: 2rem;
  outline: none;
}

.search-input::placeholder {
  color: var(--color-text-muted);
}

.icon-btn {
  position: relative;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid var(--color-border-glass);
  cursor: pointer;
  color: var(--color-text-secondary);
  transition: all 0.2s ease;
}

.icon-btn:hover {
  background: var(--color-primary);
  border-color: var(--color-primary);
  color: white;
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(139, 92, 246, 0.3);
}

.bell-icon, .help-icon {
  width: 20px;
  height: 20px;
}

.notification-badge {
  position: absolute;
  top: -4px;
  right: -4px;
  background: var(--color-accent);
  color: white;
  font-size: 0.7rem;
  font-weight: 700;
  min-width: 18px;
  height: 18px;
  border-radius: 9px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid var(--color-bg-primary);
  box-shadow: 0 0 5px var(--color-accent);
}

/* Responsive */
@media (max-width: 1024px) {
  .header-content {
    margin-left: 0;
    padding: 0 var(--space-4);
  }

  .page-title {
    font-size: var(--text-lg);
  }

  .search-box {
    display: none;
  }
}
</style>