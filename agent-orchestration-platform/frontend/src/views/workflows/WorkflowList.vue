<template>
  <div class="workflow-list-container">
    <!-- Background Decoration -->
    <div class="bg-decoration">
      <div class="glow-orb orb-1"></div>
      <div class="glow-orb orb-2"></div>
    </div>

    <!-- Page Header -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-text">
          <h1 class="page-title">Workflows</h1>
          <p class="page-description">Orchestrate and manage your AI automation pipelines</p>
        </div>
        <button class="btn btn-primary-glow" @click="handleCreate">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="btn-icon">
            <path d="M12 5v14M5 12h14" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          Create Workflow
        </button>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="stats-grid">
      <div class="stat-card glass-card">
        <div class="stat-icon-wrapper primary-glow">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="stat-icon">
            <rect x="2" y="7" width="20" height="14" rx="2" ry="2" stroke="currentColor" stroke-width="2"/>
            <path d="M16 21V5a2 2 0 00-2-2h-4a2 2 0 00-2 2v16" stroke="currentColor" stroke-width="2"/>
          </svg>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ total }}</div>
          <div class="stat-label">Total Workflows</div>
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
          <div class="stat-value">{{ publishedCount }}</div>
          <div class="stat-label">Published</div>
        </div>
        <div class="stat-decoration"></div>
      </div>

      <div class="stat-card glass-card">
        <div class="stat-icon-wrapper warning-glow">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="stat-icon">
            <path d="M9 12l2 2 4-4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M12 1v22" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ draftCount }}</div>
          <div class="stat-label">Drafts</div>
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
          placeholder="Search workflows..."
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
          :class="{ active: activeFilter === 'published' }"
          @click="activeFilter = 'published'"
        >
          Published
        </button>
        <button
          class="filter-tab"
          :class="{ active: activeFilter === 'draft' }"
          @click="activeFilter = 'draft'"
        >
          Drafts
        </button>
      </div>
    </div>

    <!-- Workflows Grid -->
    <div class="workflows-grid">
      <TransitionGroup name="list">
        <div
          v-for="workflow in filteredWorkflows"
          :key="workflow.id"
          class="workflow-card glass-card"
          @click="handleViewDetails(workflow)"
        >
          <div class="card-glow-effect"></div>
          
          <div class="card-header">
            <div class="workflow-icon">
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M22 12h-4l-3 9L9 3l-3 9H2" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
            <span
              class="workflow-status"
              :class="workflow.is_published ? 'status-published' : 'status-draft'"
            >
              <span class="status-dot"></span>
              {{ workflow.is_published ? 'Published' : 'Draft' }}
            </span>
          </div>

          <div class="card-body">
            <h3 class="workflow-name">{{ workflow.name }}</h3>
            <p class="workflow-description">{{ workflow.description || 'No description provided.' }}</p>
          </div>

          <div class="card-footer">
            <div class="workflow-meta">
              <div class="meta-item" title="Created at">
                <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="meta-icon">
                  <path d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
                <span>{{ formatDate(workflow.created_at) }}</span>
              </div>
            </div>

            <div class="card-actions">
              <button class="action-icon-btn" @click.stop="handleEdit(workflow)" title="Edit">
                <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  <path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
              </button>
              <button
                v-if="!workflow.is_published"
                class="action-icon-btn success"
                @click.stop="handlePublish(workflow)"
                title="Publish"
              >
                <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M7 11l5 5m0 0l5-5m-5 5V6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
              </button>
              <button
                class="action-icon-btn danger"
                @click.stop="handleDelete(workflow)"
                title="Delete"
              >
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
    <div v-if="loading && workflows.length === 0" class="loading-state">
      <div class="spinner-container">
        <svg class="spinner" viewBox="0 0 50 50">
          <circle class="path" cx="25" cy="25" r="20" fill="none" stroke-width="5"></circle>
        </svg>
      </div>
      <p>Loading workflows...</p>
    </div>

    <!-- Empty State -->
    <div v-if="!loading && filteredWorkflows.length === 0" class="empty-state glass-panel">
      <div class="empty-icon-wrapper">
        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="empty-icon">
          <rect x="2" y="7" width="20" height="14" rx="2" ry="2" stroke="currentColor" stroke-width="2"/>
          <path d="M16 21V5a2 2 0 00-2-2h-4a2 2 0 00-2 2v16" stroke="currentColor" stroke-width="2"/>
        </svg>
      </div>
      <h3>No workflows found</h3>
      <p>Create your first automation workflow to get started</p>
      <button class="btn btn-primary-glow" @click="handleCreate">
        Create Workflow
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

const workflows = ref([])
const loading = ref(false)
const searchQuery = ref('')
const activeFilter = ref('all')

const filteredWorkflows = computed(() => {
  let result = workflows.value

  // Apply search filter
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(w =>
      w.name.toLowerCase().includes(query) ||
      (w.description && w.description.toLowerCase().includes(query))
    )
  }

  // Apply status filter
  if (activeFilter.value === 'published') {
    result = result.filter(w => w.is_published)
  } else if (activeFilter.value === 'draft') {
    result = result.filter(w => !w.is_published)
  }

  return result
})

const total = computed(() => workflows.value.length)
const publishedCount = computed(() => workflows.value.filter(w => w.is_published).length)
const draftCount = computed(() => workflows.value.filter(w => !w.is_published).length)

async function loadData() {
  loading.value = true
  try {
    const response = await axios.get('/v1/Workflow/')
    workflows.value = response.data.data || []
  } catch (error) {
    console.error('Load failed:', error)
    ElMessage.error('Failed to load workflows')
  } finally {
    loading.value = false
  }
}

function handleCreate() {
  router.push('/workflows/create')
}

function handleEdit(workflow) {
  router.push(`/workflows/${workflow.id}/edit`)
}

function handleViewDetails(workflow) {
  router.push(`/workflows/${workflow.id}`)
}

async function handlePublish(workflow) {
  try {
    await axios.post(`/v1/Workflow/${workflow.id}/publish`)
    ElMessage.success('Workflow published successfully!')
    await loadData()
  } catch (error) {
    console.error('Publish failed:', error)
    ElMessage.error('Failed to publish workflow')
  }
}

async function handleDelete(workflow) {
  try {
    await ElMessageBox.confirm(
      `Are you sure you want to delete "${workflow.name}"?`,
      'Delete Workflow',
      {
        confirmButtonText: 'Delete',
        cancelButtonText: 'Cancel',
        type: 'warning',
        confirmButtonClass: 'el-button--danger'
      }
    )

    await axios.delete(`/v1/Workflow/${workflow.id}`)
    ElMessage.success('Workflow deleted successfully!')
    await loadData()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Delete failed:', error)
      ElMessage.error('Failed to delete workflow')
    }
  }
}

function formatDate(dateString) {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  const now = new Date()
  const diff = now - date
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))

  if (days === 0) return 'Today'
  if (days === 1) return 'Yesterday'
  if (days < 7) return `${days} days ago`
  if (days < 30) return `${Math.floor(days / 7)} weeks ago`
  return date.toLocaleDateString()
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.workflow-list-container {
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

/* Workflows Grid */
.workflows-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: var(--space-6);
}

.workflow-card {
  padding: 0;
  cursor: pointer;
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

.workflow-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.3);
  border-color: var(--color-primary-400);
}

.workflow-card:hover .card-glow-effect {
  opacity: 1;
}

.card-header {
  padding: var(--space-6);
  padding-bottom: var(--space-2);
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.workflow-icon {
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

.workflow-status {
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

.status-published {
  background: rgba(16, 185, 129, 0.1);
  color: var(--color-success);
  border: 1px solid rgba(16, 185, 129, 0.2);
}

.status-draft {
  background: rgba(245, 158, 11, 0.1);
  color: var(--color-warning);
  border: 1px solid rgba(245, 158, 11, 0.2);
}

.card-body {
  padding: 0 var(--space-6);
  flex: 1;
}

.workflow-name {
  font-size: var(--text-xl);
  font-weight: var(--font-bold);
  color: var(--color-text-primary);
  margin-bottom: var(--space-2);
  line-height: 1.4;
}

.workflow-description {
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
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-top: 1px solid var(--color-border-light);
  margin-top: var(--space-4);
}

.workflow-meta {
  display: flex;
  gap: var(--space-4);
}

.meta-item {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-size: var(--text-xs);
  color: var(--color-text-muted);
}

.meta-icon {
  width: 14px;
  height: 14px;
}

.card-actions {
  display: flex;
  gap: var(--space-2);
}

.action-icon-btn {
  width: 32px;
  height: 32px;
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

.action-icon-btn.success:hover {
  background: rgba(16, 185, 129, 0.1);
  color: var(--color-success);
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