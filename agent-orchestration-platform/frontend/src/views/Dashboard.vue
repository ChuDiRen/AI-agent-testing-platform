<template>
  <div class="dashboard-container">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-content">
        <div>
          <h1 class="page-title text-glow">Overview</h1>
          <p class="page-description">Welcome back! Here's what's happening in your agent orchestration platform.</p>
        </div>
        <div class="header-actions">
          <button class="btn-primary-glow" @click="handleCreateAgent">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="btn-icon">
              <path d="M12 5v14M5 12h14" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            New Agent
          </button>
          <button class="btn-secondary-glow" @click="handleCreateWorkflow">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="btn-icon">
              <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M2 17L12 22L22 17" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M2 12L12 17L22 12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            New Workflow
          </button>
        </div>
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
          <div class="stat-value">{{ stats.totalAgents }}</div>
          <div class="stat-label">Active Agents</div>
        </div>
        <div class="stat-trend positive">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="trend-icon">
            <path d="M23 6l-9.5 9.5-5-5L1 18" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          <span>+12%</span>
        </div>
      </div>

      <div class="stat-card glass-card">
        <div class="stat-icon-wrapper success-glow">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="stat-icon">
            <rect x="2" y="7" width="20" height="14" rx="2" ry="2" stroke="currentColor" stroke-width="2"/>
            <path d="M16 21V5a2 2 0 00-2-2h-4a2 2 0 00-2 2v16" stroke="currentColor" stroke-width="2"/>
          </svg>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.totalWorkflows }}</div>
          <div class="stat-label">Workflows</div>
        </div>
        <div class="stat-trend positive">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="trend-icon">
            <path d="M22 11.08V12a10 10 0 11-5.93-9.14" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M22 4L12 14.01l-3-3" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          <span>Deployed</span>
        </div>
      </div>

      <div class="stat-card glass-card">
        <div class="stat-icon-wrapper warning-glow">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="stat-icon">
            <path d="M14.7 6.3a1 1 0 000 1.4l1.6 1.6a1 1 0 001.4 0l3.77-3.77a6 6 0 01-7.94 7.94l-6.91 6.91a2.12 2.12 0 01-3-3l6.91-6.91a6 6 0 017.94-7.94l-3.76 3.76z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.totalTools }}</div>
          <div class="stat-label">Integrations</div>
        </div>
        <div class="stat-trend neutral">
          <span>Configured</span>
        </div>
      </div>

      <div class="stat-card glass-card">
        <div class="stat-icon-wrapper accent-glow">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="stat-icon">
            <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
            <path d="M12 6v6l4 2" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.totalExecutions }}</div>
          <div class="stat-label">Total Executions</div>
        </div>
        <div class="stat-trend positive">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="trend-icon">
            <path d="M13 2L3 14h9l-1 8 10-12-9-4z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          <span>Today</span>
        </div>
      </div>
    </div>

    <!-- Quick Actions & Recent Activity -->
    <div class="dashboard-grid-layout">
      <!-- Quick Actions -->
      <section class="dashboard-section glass-card">
        <h2 class="section-title">Quick Actions</h2>
        <div class="quick-actions-grid">
          <div class="action-card" @click="handleCreateAgent">
            <div class="action-icon-wrapper">
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="action-icon">
                <circle cx="12" cy="12" r="3" stroke="currentColor" stroke-width="2"/>
                <path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              </svg>
            </div>
            <h3>Create Agent</h3>
            <p>Deploy a new intelligent agent</p>
          </div>

          <div class="action-card" @click="handleCreateWorkflow">
            <div class="action-icon-wrapper">
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="action-icon">
                <rect x="2" y="7" width="20" height="14" rx="2" ry="2" stroke="currentColor" stroke-width="2"/>
                <path d="M16 21V5a2 2 0 00-2-2h-4a2 2 0 00-2 2v16" stroke="currentColor" stroke-width="2"/>
              </svg>
            </div>
            <h3>Design Workflow</h3>
            <p>Orchestrate complex tasks</p>
          </div>

          <div class="action-card" @click="handleRegisterTool">
            <div class="action-icon-wrapper">
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="action-icon">
                <path d="M14.7 6.3a1 1 0 000 1.4l1.6 1.6a1 1 0 001.4 0l3.77-3.77a6 6 0 01-7.94 7.94l-6.91 6.91a2.12 2.12 0 01-3-3l6.91-6.91a6 6 0 017.94-7.94l-3.76 3.76z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
            <h3>Register Tool</h3>
            <p>Connect external APIs</p>
          </div>
        </div>
      </section>

      <!-- Recent Activity -->
      <section class="dashboard-section glass-card">
        <h2 class="section-title">Recent Activity</h2>
        <div class="activity-list">
          <div class="activity-item" v-for="activity in recentActivities" :key="activity.id">
            <div class="activity-status-indicator" :class="activity.type"></div>
            <div class="activity-content">
              <div class="activity-header">
                <h4>{{ activity.title }}</h4>
                <span class="activity-time">{{ activity.time }}</span>
              </div>
              <p>{{ activity.description }}</p>
            </div>
          </div>
          <div v-if="recentActivities.length === 0" class="empty-state">
            No recent activity
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAgentStore } from '@/store/agent'
import axios from '@/api/index'

const router = useRouter()
const agentStore = useAgentStore()

const stats = ref({
  totalAgents: 0,
  totalWorkflows: 0,
  totalTools: 0,
  totalExecutions: 0
})

const recentActivities = ref([])

async function loadStats() {
  try {
    const agentResponse = await axios.get('/v1/Agent/', { params: { skip: 0, limit: 1000 } })
    if (agentResponse.data && agentResponse.data.code === 200) {
      stats.value.totalAgents = agentResponse.data.total || 0
    }
    
    const workflowResponse = await axios.get('/v1/Workflow/', { params: { skip: 0, limit: 1000 } })
    if (workflowResponse.data && workflowResponse.data.code === 200) {
      stats.value.totalWorkflows = workflowResponse.data.total || 0
    }
    
    const toolResponse = await axios.get('/v1/Tool/', { params: { skip: 0, limit: 1000 } })
    if (toolResponse.data && toolResponse.data.code === 200) {
      stats.value.totalTools = toolResponse.data.total || 0
    }
    
    const executionResponse = await axios.get('/v1/Execution/')
    if (executionResponse.data && executionResponse.data.code === 200) {
      stats.value.totalExecutions = executionResponse.data.total || 0
    }
  } catch (error) {
    console.error('Failed to load stats:', error)
  }
}

async function loadRecentActivities() {
  try {
    const response = await axios.get('/v1/Execution/', { params: { skip: 0, limit: 5 } })
    if (response.data && response.data.code === 200 && response.data.data) {
      recentActivities.value = response.data.data.map((execution, index) => ({
        id: execution.id || index,
        type: execution.status === 'completed' ? 'success' : execution.status === 'failed' ? 'error' : 'processing',
        title: execution.status === 'completed' ? 'Execution Completed' : execution.status === 'failed' ? 'Execution Failed' : 'Running',
        description: `Workflow ${execution.workflow_id || 'Unknown'} - ${execution.status}`,
        time: formatTime(execution.created_at)
      }))
    }
  } catch (error) {
    console.error('Failed to load recent activities:', error)
  }
}

function formatTime(dateString) {
  if (!dateString) return 'Unknown'
  const date = new Date(dateString)
  const now = new Date()
  const diff = Math.floor((now - date) / 1000)
  
  if (diff < 60) return 'Just now'
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`
  return `${Math.floor(diff / 86400)}d ago`
}

function handleCreateAgent() {
  router.push('/agents/create')
}

function handleCreateWorkflow() {
  router.push('/workflows/create')
}

function handleRegisterTool() {
  router.push('/tools')
}

function handleViewMonitoring() {
  router.push('/monitoring')
}

onMounted(() => {
  loadStats()
  loadRecentActivities()
})
</script>

<style scoped>
.dashboard-container {
  max-width: 1400px;
  margin: 0 auto;
}

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

.header-actions {
  display: flex;
  gap: var(--space-4);
}

.btn-primary-glow, .btn-secondary-glow {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-3) var(--space-6);
  border-radius: var(--radius-lg);
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  border: none;
}

.btn-primary-glow {
  background: var(--color-primary);
  color: white;
  box-shadow: 0 0 15px var(--color-primary-glow);
}

.btn-primary-glow:hover {
  transform: translateY(-2px);
  box-shadow: 0 0 25px var(--color-primary-glow);
}

.btn-secondary-glow {
  background: rgba(255, 255, 255, 0.1);
  color: var(--color-text-primary);
  border: 1px solid var(--color-border-glass);
  backdrop-filter: blur(4px);
}

.btn-secondary-glow:hover {
  background: rgba(255, 255, 255, 0.2);
  border-color: var(--color-primary-light);
}

.btn-icon {
  width: 20px;
  height: 20px;
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: var(--space-6);
  margin-bottom: var(--space-8);
}

.stat-card {
  padding: var(--space-6);
  position: relative;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  min-height: 160px;
  transition: transform 0.3s ease, border-color 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-5px);
  border-color: var(--color-primary-light);
}

.stat-icon-wrapper {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: var(--space-4);
}

.primary-glow { background: rgba(139, 92, 246, 0.15); color: var(--color-primary); }
.success-glow { background: rgba(16, 185, 129, 0.15); color: var(--color-success); }
.warning-glow { background: rgba(245, 158, 11, 0.15); color: var(--color-warning); }
.accent-glow { background: rgba(6, 182, 212, 0.15); color: var(--color-accent); }

.stat-icon {
  width: 24px;
  height: 24px;
}

.stat-value {
  font-family: 'Space Grotesk', sans-serif;
  font-size: 3rem;
  font-weight: 700;
  line-height: 1;
  margin-bottom: var(--space-1);
  background: linear-gradient(to right, #fff, #94a3b8);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-label {
  color: var(--color-text-secondary);
  font-weight: 500;
}

.stat-trend {
  position: absolute;
  top: var(--space-6);
  right: var(--space-6);
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: var(--text-sm);
  font-weight: 600;
  padding: 4px 8px;
  border-radius: var(--radius-full);
  background: rgba(255, 255, 255, 0.05);
}

.stat-trend.positive { color: var(--color-success); }
.stat-trend.neutral { color: var(--color-text-muted); }
.trend-icon { width: 16px; height: 16px; }

/* Dashboard Grid Layout */
.dashboard-grid-layout {
  display: grid;
  grid-template-columns: 1.5fr 1fr;
  gap: var(--space-6);
}

.dashboard-section {
  padding: var(--space-6);
}

.section-title {
  font-size: var(--text-xl);
  margin-bottom: var(--space-6);
  color: var(--color-text-primary);
}

/* Quick Actions */
.quick-actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: var(--space-4);
}

.action-card {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--color-border-glass);
  border-radius: var(--radius-lg);
  padding: var(--space-5);
  cursor: pointer;
  transition: all 0.3s ease;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-3);
}

.action-card:hover {
  background: rgba(255, 255, 255, 0.08);
  transform: translateY(-3px);
  border-color: var(--color-primary);
}

.action-icon-wrapper {
  width: 48px;
  height: 48px;
  background: var(--color-bg-tertiary);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-primary);
  margin-bottom: var(--space-2);
}

.action-icon {
  width: 24px;
  height: 24px;
}

.action-card h3 {
  font-size: var(--text-base);
  font-weight: 600;
  margin: 0;
}

.action-card p {
  font-size: var(--text-xs);
  color: var(--color-text-muted);
  margin: 0;
  line-height: 1.4;
}

/* Recent Activity */
.activity-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.activity-item {
  display: flex;
  gap: var(--space-4);
  padding-bottom: var(--space-4);
  border-bottom: 1px solid var(--color-border-glass);
}

.activity-item:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.activity-status-indicator {
  width: 4px;
  border-radius: var(--radius-full);
  background: var(--color-text-muted);
  flex-shrink: 0;
}

.activity-status-indicator.success { background: var(--color-success); box-shadow: 0 0 10px var(--color-success); }
.activity-status-indicator.error { background: var(--color-error); box-shadow: 0 0 10px var(--color-error); }
.activity-status-indicator.processing { background: var(--color-accent); box-shadow: 0 0 10px var(--color-accent); }

.activity-content {
  flex: 1;
}

.activity-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-1);
}

.activity-header h4 {
  font-size: var(--text-sm);
  font-weight: 600;
  margin: 0;
}

.activity-time {
  font-size: var(--text-xs);
  color: var(--color-text-muted);
}

.activity-content p {
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
  margin: 0;
}

.empty-state {
  text-align: center;
  color: var(--color-text-muted);
  padding: var(--space-8);
  font-style: italic;
}

/* Responsive */
@media (max-width: 1024px) {
  .dashboard-grid-layout {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--space-4);
  }
  
  .header-actions {
    width: 100%;
  }
  
  .btn-primary-glow, .btn-secondary-glow {
    flex: 1;
    justify-content: center;
  }
}
</style>