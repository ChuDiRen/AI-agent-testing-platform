<template>
  <div class="agent-list-container">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-content">
        <div>
          <h1 class="page-title text-glow">Intelligent Agents</h1>
          <p class="page-description">Manage and configure your autonomous AI agents</p>
        </div>
        <button class="btn-primary-glow" @click="handleCreate">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="btn-icon">
            <path d="M12 5v14M5 12h14" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          New Agent
        </button>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="stats-grid">
      <div class="stat-card glass-card">
        <div class="stat-icon-wrapper primary-glow">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="stat-icon">
            <circle cx="12" cy="12" r="3" stroke="currentColor" stroke-width="2"/>
            <path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          </svg>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ total }}</div>
          <div class="stat-label">Total Agents</div>
        </div>
      </div>

      <div class="stat-card glass-card">
        <div class="stat-icon-wrapper success-glow">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="stat-icon">
            <path d="M22 11.08V12a10 10 0 11-5.93-9.14" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M22 4L12 14.01l-3-3" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ activeCount }}</div>
          <div class="stat-label">Active</div>
        </div>
      </div>

      <div class="stat-card glass-card">
        <div class="stat-icon-wrapper warning-glow">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="stat-icon">
            <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
            <path d="M12 8v4M12 16h.01" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ inactiveCount }}</div>
          <div class="stat-label">Inactive</div>
        </div>
      </div>
    </div>

    <!-- Agent Cards Grid -->
    <div class="agents-grid">
      <div
        v-for="agent in agents"
        :key="agent.id"
        class="agent-card glass-card"
        @click="handleViewDetails(agent)"
      >
        <div class="card-header">
          <div class="agent-icon-wrapper">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="agent-icon">
              <circle cx="12" cy="12" r="3" stroke="currentColor" stroke-width="2"/>
              <path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            </svg>
          </div>
          <div class="agent-status-badge" :class="agent.is_active ? 'active' : 'inactive'">
            {{ agent.is_active ? 'Active' : 'Inactive' }}
          </div>
        </div>

        <h3 class="agent-name">{{ agent.name }}</h3>
        <p class="agent-model">{{ agent.model }}</p>

        <div class="agent-config">
          <div class="config-item">
            <span class="config-label">Temp</span>
            <span class="config-value">{{ agent.temperature }}</span>
          </div>
          <div class="config-item">
            <span class="config-label">Tokens</span>
            <span class="config-value">{{ agent.max_tokens }}</span>
          </div>
        </div>

        <div class="card-actions">
          <button class="action-btn" @click.stop="handleEdit(agent)" aria-label="Edit agent">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </button>
          <button class="action-btn danger" @click.stop="handleDelete(agent)" aria-label="Delete agent">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M3 6h18M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2M10 11v6M14 11v6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </button>
        </div>
      </div>
    </div>

    <!-- Pagination -->
    <div v-if="total > pageSize" class="pagination">
      <button
        class="pagination-btn glass-card"
        :disabled="currentPage === 1"
        @click="handlePageChange(currentPage - 1)"
        aria-label="Previous page"
      >
        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M15 19l-7-7 7-7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </button>

      <span class="pagination-info text-glow">
        Page {{ currentPage }} of {{ totalPages }}
      </span>

      <button
        class="pagination-btn glass-card"
        :disabled="currentPage === totalPages"
        @click="handlePageChange(currentPage + 1)"
        aria-label="Next page"
      >
        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M9 5l7 7-7 7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="loading && agents.length === 0" class="loading-state">
      <div class="spinner-large"></div>
      <p>Loading agents...</p>
    </div>

    <!-- Empty State -->
    <div v-if="!loading && agents.length === 0" class="empty-state glass-card">
      <div class="empty-icon-wrapper">
        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="empty-icon">
          <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" stroke-dasharray="4 4"/>
          <circle cx="12" cy="12" r="3" stroke="currentColor" stroke-width="2"/>
        </svg>
      </div>
      <h3>No Agents Found</h3>
      <p>Create your first intelligent agent to get started</p>
      <button class="btn-primary-glow" @click="handleCreate">
        Create Agent
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import axios from '@/api/index'
// Assuming store is available, if not we can use local state only
import { useAgentStore } from '@/store/agent'

const router = useRouter()
const agentStore = useAgentStore()

const agents = ref([])
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(9)
const total = ref(0)

const activeCount = computed(() => agents.value.filter(a => a.is_active).length)
const inactiveCount = computed(() => agents.value.filter(a => !a.is_active).length)
const totalPages = computed(() => Math.ceil(total.value / pageSize.value))

async function loadData() {
  loading.value = true
  try {
    const response = await axios.get('/v1/Agent/', {
      params: {
        skip: (currentPage.value - 1) * pageSize.value,
        limit: pageSize.value
      }
    })

    // Adjust based on actual API response structure
    if (response.data && Array.isArray(response.data)) {
        agents.value = response.data
        total.value = response.total || response.data.length
    } else if (Array.isArray(response)) {
        agents.value = response
        total.value = response.length
    } else if (response.data && response.data.data) {
        agents.value = response.data.data
        total.value = response.data.total
    }
    
  } catch (error) {
    ElMessage.error('Failed to load agents')
    console.error(error)
  } finally {
    loading.value = false
  }
}

function handleCreate() {
  router.push('/agents/create')
}

function handleEdit(agent) {
  router.push(`/agents/${agent.id}/edit`)
}

function handleViewDetails(agent) {
  router.push(`/agents/${agent.id}`)
}

async function handleDelete(agent) {
  if (confirm(`Are you sure you want to delete "${agent.name}"?`)) {
    try {
      await agentStore.deleteAgent(agent.id)
      ElMessage.success('Agent deleted')
      await loadData()
    } catch (error) {
      console.error('Delete failed:', error)
      ElMessage.error('Failed to delete agent')
    }
  }
}

function handlePageChange(page) {
  currentPage.value = page
  loadData()
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.agent-list-container {
  max-width: 1400px;
  margin: 0 auto;
}

/* Page Header */
.page-header {
  margin-bottom: var(--space-8);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
}

.page-title {
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: var(--space-2);
}

.page-description {
  color: var(--color-text-secondary);
  font-size: var(--text-lg);
}

.btn-primary-glow {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-3) var(--space-6);
  border-radius: var(--radius-lg);
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  border: none;
  background: var(--color-primary);
  color: white;
  box-shadow: 0 0 15px var(--color-primary-glow);
}

.btn-primary-glow:hover {
  transform: translateY(-2px);
  box-shadow: 0 0 25px var(--color-primary-glow);
}

.btn-icon {
  width: 20px;
  height: 20px;
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--space-6);
  margin-bottom: var(--space-8);
}

.stat-card {
  padding: var(--space-6);
  display: flex;
  align-items: center;
  gap: var(--space-4);
  transition: transform 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  border-color: var(--color-primary-light);
}

.stat-icon-wrapper {
  width: 56px;
  height: 56px;
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.primary-glow { background: rgba(139, 92, 246, 0.15); color: var(--color-primary); }
.success-glow { background: rgba(16, 185, 129, 0.15); color: var(--color-success); }
.warning-glow { background: rgba(245, 158, 11, 0.15); color: var(--color-warning); }

.stat-icon {
  width: 28px;
  height: 28px;
}

.stat-value {
  font-family: 'Space Grotesk', sans-serif;
  font-size: 2rem;
  font-weight: 700;
  line-height: 1;
  color: var(--color-text-primary);
}

.stat-label {
  font-size: 0.875rem;
  color: var(--color-text-secondary);
  margin-top: 4px;
}

/* Agents Grid */
.agents-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: var(--space-6);
  margin-bottom: var(--space-8);
}

.agent-card {
  padding: var(--space-6);
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  position: relative;
  overflow: hidden;
}

.agent-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.1) 0%, transparent 100%);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.agent-card:hover {
  transform: translateY(-5px);
  border-color: var(--color-primary);
  box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5);
}

.agent-card:hover::before {
  opacity: 1;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: var(--space-4);
  position: relative;
  z-index: 1;
}

.agent-icon-wrapper {
  width: 48px;
  height: 48px;
  background: var(--color-bg-tertiary);
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-primary);
  border: 1px solid var(--color-border-glass);
}

.agent-icon {
  width: 24px;
  height: 24px;
}

.agent-status-badge {
  padding: 4px 10px;
  border-radius: var(--radius-full);
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.agent-status-badge.active {
  background: rgba(16, 185, 129, 0.15);
  color: var(--color-success);
  border: 1px solid rgba(16, 185, 129, 0.3);
  box-shadow: 0 0 10px rgba(16, 185, 129, 0.2);
}

.agent-status-badge.inactive {
  background: rgba(148, 163, 184, 0.15);
  color: var(--color-text-muted);
  border: 1px solid rgba(148, 163, 184, 0.3);
}

.agent-name {
  font-size: 1.25rem;
  font-weight: 600;
  margin: 0 0 var(--space-1);
  color: var(--color-text-primary);
  position: relative;
  z-index: 1;
}

.agent-model {
  font-family: var(--font-mono);
  font-size: 0.875rem;
  color: var(--color-text-muted);
  margin: 0 0 var(--space-4);
  background: rgba(0, 0, 0, 0.2);
  display: inline-block;
  padding: 2px 6px;
  border-radius: 4px;
  position: relative;
  z-index: 1;
}

.agent-config {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-2);
  margin-bottom: var(--space-6);
  background: rgba(0, 0, 0, 0.2);
  padding: var(--space-3);
  border-radius: var(--radius-md);
  position: relative;
  z-index: 1;
}

.config-item {
  display: flex;
  flex-direction: column;
}

.config-label {
  font-size: 0.75rem;
  color: var(--color-text-muted);
  text-transform: uppercase;
}

.config-value {
  font-family: var(--font-mono);
  font-size: 0.875rem;
  color: var(--color-text-secondary);
}

.card-actions {
  display: flex;
  justify-content: flex-end;
  gap: var(--space-2);
  margin-top: auto;
  position: relative;
  z-index: 1;
  opacity: 0.6;
  transition: opacity 0.2s;
}

.agent-card:hover .card-actions {
  opacity: 1;
}

.action-btn {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid var(--color-border-glass);
  background: rgba(255, 255, 255, 0.05);
  border-radius: var(--radius-md);
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all 0.2s;
}

.action-btn:hover {
  background: var(--color-primary);
  border-color: var(--color-primary);
  color: white;
}

.action-btn.danger:hover {
  background: var(--color-error);
  border-color: var(--color-error);
}

/* Pagination */
.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-4);
  margin-top: var(--space-8);
}

.pagination-btn {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid var(--color-border-glass);
  background: rgba(255, 255, 255, 0.05);
  border-radius: var(--radius-lg);
  color: var(--color-text-primary);
  cursor: pointer;
  transition: all 0.2s;
}

.pagination-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pagination-btn:not(:disabled):hover {
  background: var(--color-primary);
  border-color: var(--color-primary);
}

.pagination-info {
  font-family: var(--font-mono);
  color: var(--color-text-secondary);
}

/* Empty State */
.empty-state {
  text-align: center;
  padding: var(--space-12);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-4);
}

.empty-icon-wrapper {
  width: 80px;
  height: 80px;
  background: var(--color-bg-tertiary);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text-muted);
  margin-bottom: var(--space-2);
}

.empty-icon {
  width: 40px;
  height: 40px;
}

.empty-state h3 {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0;
}

.empty-state p {
  color: var(--color-text-secondary);
  margin-bottom: var(--space-4);
}

/* Loading State */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--space-16);
  color: var(--color-text-muted);
}

.spinner-large {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(139, 92, 246, 0.1);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: var(--space-4);
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--space-4);
  }
}
</style>