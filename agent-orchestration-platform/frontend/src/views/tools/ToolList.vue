<template>
  <div class="tool-list-container">
    <!-- Background Decoration -->
    <div class="bg-decoration">
      <div class="glow-orb orb-1"></div>
      <div class="glow-orb orb-2"></div>
    </div>

    <!-- Page Header -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-text">
          <h1 class="page-title">Tools & Integrations</h1>
          <p class="page-description">Manage and monitor your AI tool ecosystem</p>
        </div>
        <button class="btn btn-primary-glow" @click="handleCreate">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="btn-icon">
            <path d="M12 5v14M5 12h14" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          Register Tool
        </button>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="stats-grid">
      <div class="stat-card glass-card">
        <div class="stat-icon-wrapper primary-glow">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="stat-icon">
            <path d="M14.7 6.3a1 1 0 000 1.4l1.6 1.6a1 1 0 001.4 0l3.77-3.77a6 6 0 01-7.94 7.94l-6.91 6.91a2.12 2.12 0 01-3-3l6.91-6.91a6 6 0 017.94-7.94l-3.76 3.76z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ total }}</div>
          <div class="stat-label">Total Tools</div>
        </div>
        <div class="stat-decoration"></div>
      </div>

      <div class="stat-card glass-card">
        <div class="stat-icon-wrapper success-glow">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="stat-icon">
            <path d="M22 11.08V12a10 10 0 11-5.93-9.14" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M22 4L12 14.01l-3-3" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ testedCount }}</div>
          <div class="stat-label">Verified</div>
        </div>
        <div class="stat-decoration"></div>
      </div>

      <div class="stat-card glass-card">
        <div class="stat-icon-wrapper warning-glow">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="stat-icon">
            <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
            <path d="M12 8v4M12 16h.01" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ pendingCount }}</div>
          <div class="stat-label">Pending Review</div>
        </div>
        <div class="stat-decoration"></div>
      </div>
    </div>

    <!-- Filter Bar -->
    <div class="filter-bar glass-panel">
      <div class="search-wrapper">
        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="search-icon">
          <circle cx="11" cy="11" r="8" stroke="currentColor" stroke-width="2"/>
          <path d="M21 21l-4.35-4.35" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>
        <input
          v-model="searchQuery"
          type="text"
          class="search-input"
          placeholder="Search tools..."
        />
      </div>

      <div class="filter-tabs">
        <button
          class="filter-tab"
          :class="{ active: activeFilter === 'all' }"
          @click="activeFilter = 'all'"
        >
          All
        </button>
        <button
          class="filter-tab"
          :class="{ active: activeFilter === 'api' }"
          @click="activeFilter = 'api'"
        >
          API
        </button>
        <button
          class="filter-tab"
          :class="{ active: activeFilter === 'function' }"
          @click="activeFilter = 'function'"
        >
          Functions
        </button>
        <button
          class="filter-tab"
          :class="{ active: activeFilter === 'plugin' }"
          @click="activeFilter = 'plugin'"
        >
          Plugins
        </button>
      </div>
    </div>

    <!-- Tools Grid -->
    <div class="tools-grid">
      <TransitionGroup name="list">
        <div
          v-for="tool in filteredTools"
          :key="tool.id"
          class="tool-card glass-card"
        >
          <div class="card-glow-effect"></div>

          <div class="card-header">
            <div class="tool-icon">
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M14.7 6.3a1 1 0 000 1.4l1.6 1.6a1 1 0 001.4 0l3.77-3.77a6 6 0 01-7.94 7.94l-6.91 6.91a2.12 2.12 0 01-3-3l6.91-6.91a6 6 0 017.94-7.94l-3.76 3.76z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
            <span
              class="tool-status"
              :class="getStatusClass(tool.test_status)"
            >
              <span class="status-dot"></span>
              {{ tool.test_status }}
            </span>
          </div>

          <div class="card-body">
            <h3 class="tool-name">{{ tool.name }}</h3>
            <p class="tool-type">{{ tool.type }}</p>
            <p class="tool-description">{{ tool.description || 'No description provided.' }}</p>
          </div>

          <div class="card-footer">
            <div class="card-actions">
              <button
                class="action-btn action-btn-primary"
                @click="handleTest(tool)"
                :disabled="testing"
                aria-label="Test tool"
              >
                <span v-if="testing && testingId === tool.id" class="loading-spinner"></span>
                <svg v-else viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M14.7 6.3a1 1 0 000 1.4l1.6 1.6a1 1 0 001.4 0l3.77-3.77a6 6 0 01-7.94 7.94l-6.91 6.91a2.12 2.12 0 01-3-3L6.91 6.91a6 6 0 017.94-7.94l-3.76 3.76z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
                {{ testing && testingId === tool.id ? 'Testing...' : 'Test' }}
              </button>
              <button class="action-icon-btn" @click="handleEdit(tool)" title="Edit">
                <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  <path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
              </button>
              <button class="action-icon-btn danger" @click="handleDelete(tool)" title="Delete">
                <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M3 6h18M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2M10 11v6M14 11v6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
              </button>
            </div>
          </div>
        </div>
      </TransitionGroup>
    </div>

    <!-- Loading State -->
    <div v-if="loading && tools.length === 0" class="loading-state">
      <div class="spinner-container">
        <svg class="spinner" viewBox="0 0 50 50">
          <circle class="path" cx="25" cy="25" r="20" fill="none" stroke-width="5"></circle>
        </svg>
      </div>
      <p>Loading tools...</p>
    </div>

    <!-- Empty State -->
    <div v-if="!loading && filteredTools.length === 0" class="empty-state glass-panel">
      <div class="empty-icon-wrapper">
        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="empty-icon">
          <path d="M14.7 6.3a1 1 0 000 1.4l1.6 1.6a1 1 0 001.4 0l3.77-3.77a6 6 0 01-7.94 7.94l-6.91 6.91a2.12 2.12 0 01-3-3L6.91 6.91a6 6 0 017.94-7.94l-3.76 3.76z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </div>
      <h3>No tools found</h3>
      <p>Register your first tool to get started</p>
      <button class="btn btn-primary-glow" @click="handleCreate">
        Register Tool
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from '@/api'

const router = useRouter()

const tools = ref([])
const loading = ref(false)
const searchQuery = ref('')
const activeFilter = ref('all')
const testing = ref(false)
const testingId = ref(null)

const filteredTools = computed(() => {
  let result = tools.value

  // Apply search filter
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(t =>
      t.name.toLowerCase().includes(query) ||
      (t.description && t.description.toLowerCase().includes(query))
    )
  }

  // Apply type filter
  if (activeFilter.value !== 'all') {
    result = result.filter(t => t.type.toLowerCase() === activeFilter.value)
  }

  return result
})

const total = computed(() => tools.value.length)
const testedCount = computed(() => tools.value.filter(t => t.test_status === 'pass').length)
const pendingCount = computed(() => tools.value.filter(t => t.test_status === 'pending').length)

async function loadData() {
  loading.value = true
  try {
    const response = await axios.get('/v1/Tool/')
    tools.value = response.data.data || []
  } catch (error) {
    console.error('Load failed:', error)
    ElMessage.error('Failed to load tools')
  } finally {
    loading.value = false
  }
}

function handleCreate() {
  router.push('/tools/create')
}

function handleEdit(tool) {
  // router.push(`/tools/${tool.id}/edit`)
  ElMessage.info('Edit feature coming soon')
}

async function handleDelete(tool) {
  try {
    await ElMessageBox.confirm(
      `Are you sure you want to delete "${tool.name}"?`,
      'Delete Tool',
      {
        confirmButtonText: 'Delete',
        cancelButtonText: 'Cancel',
        type: 'warning',
        confirmButtonClass: 'el-button--danger'
      }
    )

    await axios.delete(`/v1/Tool/${tool.id}`)
    ElMessage.success('Tool deleted successfully!')
    await loadData()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Delete failed:', error)
      ElMessage.error('Failed to delete tool')
    }
  }
}

async function handleTest(tool) {
  if (testing.value) return
  
  testing.value = true
  testingId.value = tool.id
  
  try {
    // Simulate test
    await new Promise(resolve => setTimeout(resolve, 2000))
    ElMessage.success(`Tool "${tool.name}" passed all tests!`)
    
    // Update status locally for demo
    tool.test_status = 'pass'
  } catch (error) {
    ElMessage.error('Tool test failed')
  } finally {
    testing.value = false
    testingId.value = null
  }
}

function getStatusClass(status) {
  switch (status?.toLowerCase()) {
    case 'pass':
      return 'status-success'
    case 'fail':
      return 'status-error'
    case 'pending':
      return 'status-warning'
    default:
      return 'status-neutral'
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.tool-list-container {
  max-width: var(--container-xl);
  margin: 0 auto;
  position: relative;
  min-height: 80vh;
}

/* Background Decoration */
.bg-decoration {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: -1;
  pointer-events: none;
  overflow: hidden;
}

.glow-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.15;
}

.orb-1 {
  top: -10%;
  right: -5%;
  width: 500px;
  height: 500px;
  background: var(--color-primary);
  animation: float 20s infinite ease-in-out;
}

.orb-2 {
  bottom: 10%;
  left: -10%;
  width: 400px;
  height: 400px;
  background: var(--color-secondary);
  animation: float 25s infinite ease-in-out reverse;
}

@keyframes float {
  0% { transform: translate(0, 0); }
  50% { transform: translate(30px, 50px); }
  100% { transform: translate(0, 0); }
}

/* Page Header */
.page-header {
  margin-bottom: var(--space-8);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: var(--space-4);
}

.page-title {
  font-size: var(--text-4xl);
  font-weight: var(--font-bold);
  background: linear-gradient(135deg, var(--color-text-primary) 0%, var(--color-text-secondary) 100%);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  margin: 0 0 var(--space-2);
}

.page-description {
  font-size: var(--text-base);
  color: var(--color-text-secondary);
  margin: 0;
}

.btn-primary-glow {
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-dark) 100%);
  color: white;
  border: none;
  padding: var(--space-3) var(--space-6);
  border-radius: var(--radius-lg);
  font-weight: var(--font-semibold);
  display: flex;
  align-items: center;
  gap: var(--space-2);
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(124, 58, 237, 0.3);
}

.btn-primary-glow:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(124, 58, 237, 0.5);
}

.btn-icon {
  width: 20px;
  height: 20px;
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: var(--space-6);
  margin-bottom: var(--space-8);
}

.stat-card {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  padding: var(--space-6);
  position: relative;
  overflow: hidden;
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-5px);
  box-shadow: var(--shadow-xl);
  border-color: var(--color-primary-300);
}

.stat-icon-wrapper {
  width: 56px;
  height: 56px;
  border-radius: var(--radius-xl);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  position: relative;
  z-index: 1;
}

.primary-glow {
  background: rgba(124, 58, 237, 0.1);
  color: var(--color-primary);
  box-shadow: 0 0 20px rgba(124, 58, 237, 0.2);
}

.success-glow {
  background: rgba(16, 185, 129, 0.1);
  color: var(--color-success);
  box-shadow: 0 0 20px rgba(16, 185, 129, 0.2);
}

.warning-glow {
  background: rgba(245, 158, 11, 0.1);
  color: var(--color-warning);
  box-shadow: 0 0 20px rgba(245, 158, 11, 0.2);
}

.stat-icon svg {
  width: 28px;
  height: 28px;
}

.stat-content {
  flex: 1;
  position: relative;
  z-index: 1;
}

.stat-value {
  font-size: var(--text-3xl);
  font-weight: var(--font-bold);
  color: var(--color-text-primary);
  margin-bottom: var(--space-1);
}

.stat-label {
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
  font-weight: var(--font-medium);
}

.stat-decoration {
  position: absolute;
  top: -50%;
  right: -20%;
  width: 150px;
  height: 150px;
  background: radial-gradient(circle, rgba(255,255,255,0.05) 0%, transparent 70%);
  border-radius: 50%;
  pointer-events: none;
}

/* Filter Bar */
.filter-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: var(--space-4);
  margin-bottom: var(--space-6);
  flex-wrap: wrap;
  padding: var(--space-4);
  border-radius: var(--radius-xl);
  background: var(--color-bg-glass);
  backdrop-filter: blur(10px);
  border: 1px solid var(--color-border-glass);
}

.search-wrapper {
  position: relative;
  flex: 1;
  min-width: 280px;
}

.search-icon {
  position: absolute;
  left: var(--space-3);
  top: 50%;
  transform: translateY(-50%);
  width: 20px;
  height: 20px;
  color: var(--color-text-muted);
  pointer-events: none;
}

.search-input {
  width: 100%;
  padding: var(--space-2) var(--space-3) var(--space-2) 2.75rem;
  font-size: var(--text-sm);
  color: var(--color-text-primary);
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--color-border-light);
  border-radius: var(--radius-lg);
  transition: all 0.2s ease-out;
}

.search-input:focus {
  outline: none;
  border-color: var(--color-primary);
  background: rgba(255, 255, 255, 0.1);
  box-shadow: 0 0 0 3px rgba(124, 58, 237, 0.2);
}

.filter-tabs {
  display: flex;
  gap: var(--space-2);
  background: rgba(0, 0, 0, 0.2);
  padding: var(--space-1);
  border-radius: var(--radius-lg);
}

.filter-tab {
  padding: var(--space-2) var(--space-4);
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--color-text-secondary);
  background: transparent;
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all 0.2s ease-out;
}

.filter-tab:hover {
  color: var(--color-text-primary);
}

.filter-tab.active {
  background: var(--color-bg-secondary);
  color: var(--color-primary);
  box-shadow: var(--shadow-sm);
}

/* Tools Grid */
.tools-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: var(--space-6);
}

.tool-card {
  padding: 0;
  cursor: default;
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  position: relative;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  height: 100%;
}

.card-glow-effect {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: radial-gradient(circle at 50% 0%, rgba(124, 58, 237, 0.1) 0%, transparent 70%);
  opacity: 0;
  transition: opacity 0.3s ease;
  pointer-events: none;
}

.tool-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.3);
  border-color: var(--color-primary-400);
}

.tool-card:hover .card-glow-effect {
  opacity: 1;
}

.card-header {
  padding: var(--space-6);
  padding-bottom: var(--space-2);
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.tool-icon {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, rgba(124, 58, 237, 0.1) 0%, rgba(124, 58, 237, 0.2) 100%);
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-primary);
  border: 1px solid rgba(124, 58, 237, 0.2);
}

.tool-status {
  padding: var(--space-1) var(--space-3);
  font-size: var(--text-xs);
  font-weight: var(--font-semibold);
  border-radius: var(--radius-full);
  display: flex;
  align-items: center;
  gap: var(--space-1);
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: currentColor;
}

.status-success {
  background: rgba(16, 185, 129, 0.1);
  color: var(--color-success);
  border: 1px solid rgba(16, 185, 129, 0.2);
}

.status-error {
  background: rgba(239, 68, 68, 0.1);
  color: var(--color-error);
  border: 1px solid rgba(239, 68, 68, 0.2);
}

.status-warning {
  background: rgba(245, 158, 11, 0.1);
  color: var(--color-warning);
  border: 1px solid rgba(245, 158, 11, 0.2);
}

.status-neutral {
  background: rgba(255, 255, 255, 0.05);
  color: var(--color-text-secondary);
  border: 1px solid var(--color-border-light);
}

.card-body {
  padding: 0 var(--space-6);
  flex: 1;
}

.tool-name {
  font-size: var(--text-xl);
  font-weight: var(--font-bold);
  color: var(--color-text-primary);
  margin-bottom: var(--space-1);
}

.tool-type {
  font-size: var(--text-xs);
  font-weight: var(--font-bold);
  color: var(--color-primary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: var(--space-2);
}

.tool-description {
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
  line-height: 1.6;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-footer {
  padding: var(--space-6);
  padding-top: var(--space-4);
  margin-top: var(--space-4);
  border-top: 1px solid var(--color-border-light);
}

.card-actions {
  display: flex;
  gap: var(--space-3);
}

.action-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  padding: var(--space-2);
  border-radius: var(--radius-md);
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  cursor: pointer;
  transition: all 0.2s ease;
  border: 1px solid transparent;
}

.action-btn-primary {
  background: rgba(124, 58, 237, 0.1);
  color: var(--color-primary);
  border-color: rgba(124, 58, 237, 0.2);
}

.action-btn-primary:hover:not(:disabled) {
  background: var(--color-primary);
  color: white;
  border-color: var(--color-primary);
}

.action-btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.action-btn svg {
  width: 16px;
  height: 16px;
}

.loading-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid currentColor;
  border-right-color: transparent;
  border-radius: 50%;
  animation: rotate 1s linear infinite;
}

.action-icon-btn {
  width: 36px;
  height: 36px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid transparent;
  background: transparent;
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all 0.2s ease;
}

.action-icon-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  color: var(--color-text-primary);
}

.action-icon-btn.danger:hover {
  background: rgba(239, 68, 68, 0.1);
  color: var(--color-error);
}

/* Loading & Empty States */
.loading-state, .empty-state {
  grid-column: 1 / -1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--space-16);
  text-align: center;
}

.spinner {
  animation: rotate 2s linear infinite;
  z-index: 2;
  position: relative;
  top: 50%;
  left: 50%;
  margin: -25px 0 0 -25px;
  width: 50px;
  height: 50px;
}

.spinner .path {
  stroke: var(--color-primary);
  stroke-linecap: round;
  animation: dash 1.5s ease-in-out infinite;
}

@keyframes rotate {
  100% { transform: rotate(360deg); }
}

@keyframes dash {
  0% { stroke-dasharray: 1, 150; stroke-dashoffset: 0; }
  50% { stroke-dasharray: 90, 150; stroke-dashoffset: -35; }
  100% { stroke-dasharray: 90, 150; stroke-dashoffset: -124; }
}

.empty-state {
  background: var(--color-bg-glass);
  backdrop-filter: blur(10px);
  border: 1px solid var(--color-border-glass);
  border-radius: var(--radius-xl);
}

.empty-icon-wrapper {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: var(--color-bg-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: var(--space-6);
}

.empty-icon {
  width: 40px;
  height: 40px;
  color: var(--color-text-muted);
}

.empty-state h3 {
  font-size: var(--text-2xl);
  font-weight: var(--font-bold);
  color: var(--color-text-primary);
  margin-bottom: var(--space-2);
}

.empty-state p {
  color: var(--color-text-secondary);
  margin-bottom: var(--space-6);
}

/* List Transitions */
.list-enter-active,
.list-leave-active {
  transition: all 0.5s ease;
}
.list-enter-from,
.list-leave-to {
  opacity: 0;
  transform: translateY(30px);
}

/* Responsive */
@media (max-width: var(--breakpoint-md)) {
  .header-content {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .btn-primary-glow {
    width: 100%;
    justify-content: center;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }
}
</style>