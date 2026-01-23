<template>
  <div class="billing-container">
    <!-- Background Decoration -->
    <div class="bg-decoration">
      <div class="glow-orb orb-1"></div>
      <div class="glow-orb orb-2"></div>
    </div>

    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h1 class="page-title">计费统计</h1>
        <p class="page-description">查看 AI 服务使用情况和成本分析</p>
      </div>
      <div class="header-actions">
        <button class="glass-button" @click="downloadReport">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="btn-icon">
            <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M7 10l5 5 5-5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M12 15V3" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          导出报告
        </button>
        <button class="glass-button primary" @click="managePaymentMethods">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="btn-icon">
            <rect x="1" y="4" width="22" height="16" rx="2" ry="2" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M1 10h22" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          支付方式
        </button>
      </div>
    </div>

    <!-- Summary Cards -->
    <div class="summary-grid">
      <div class="glass-card summary-card summary-primary">
        <div class="card-glow-effect"></div>
        <div class="summary-icon">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 2v20M17 5H9.5a3.5 3.5 0 000 7h5a3.5 3.5 0 000-7z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <div class="summary-content">
          <div class="summary-value">${{ totalCost.toFixed(2) }}</div>
          <div class="stat-label">总成本</div>
          <div class="summary-trend trend-up">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M23 6l-9.5 9.5-5-5L1 18" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <span>+{{ costTrend }}%</span>
          </div>
        </div>
      </div>

      <div class="glass-card summary-card summary-accent">
        <div class="card-glow-effect"></div>
        <div class="summary-icon">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M13 2L3 14h9l-1 8 10-12-9-4z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <div class="summary-content">
          <div class="summary-value">{{ totalTokens.toLocaleString() }}</div>
          <div class="summary-label">总代币</div>
          <div class="stat-label">本月使用</div>
        </div>
      </div>

      <div class="glass-card summary-card summary-success">
        <div class="card-glow-effect"></div>
        <div class="summary-icon">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M22 11.08V12a10 10 0 11-5.93-9.14" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M22 4L12 14.01l-3-3" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <div class="summary-content">
          <div class="summary-value">{{ totalExecutions.toLocaleString() }}</div>
          <div class="summary-label">总执行次数</div>
          <div class="summary-sub">全部时间</div>
        </div>
      </div>

      <div class="glass-card summary-card summary-warning">
        <div class="card-glow-effect"></div>
        <div class="summary-icon">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <div class="summary-content">
          <div class="summary-value">{{ activeQuotas }}</div>
          <div class="summary-label">活动配额</div>
          <div class="summary-sub">{{ pendingAlerts }} 警报</div>
        </div>
      </div>
    </div>

    <div class="dashboard-grid">
      <!-- Usage Chart -->
      <div class="glass-card chart-card">
        <div class="card-header">
          <h2 class="card-title">使用趋势</h2>
          <div class="card-actions">
            <button
              class="filter-btn"
              :class="{ active: timeRange === 'week' }"
              @click="timeRange = 'week'"
            >
              周
            </button>
            <button
              class="filter-btn"
              :class="{ active: timeRange === 'month' }"
              @click="timeRange = 'month'"
            >
              月
            </button>
            <button
              class="filter-btn"
              :class="{ active: timeRange === 'year' }"
              @click="timeRange = 'year'"
            >
              年
            </button>
          </div>
        </div>

        <div class="chart-container" ref="chartContainer">
          <!-- Placeholder for chart -->
          <div class="chart-placeholder">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="placeholder-icon">
              <path d="M3 3v18h18" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M18.7 8l-5.1 5.2-2.8-2.7L7 14.3" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <p>Usage chart will be rendered here</p>
            <small>Integrate with ECharts or Chart.js</small>
          </div>
        </div>
      </div>

      <!-- Cost Breakdown -->
      <div class="glass-card breakdown-card">
        <div class="card-header">
          <h2 class="card-title">按代理统计成本</h2>
          <button class="view-all-btn" @click="viewAllBreakdown">
            查看全部
          </button>
        </div>

        <div class="breakdown-list">
          <div
            v-for="(agent, index) in agentBreakdown.slice(0, 5)"
            :key="agent.agent_name"
            class="breakdown-item glass-panel"
          >
            <div class="breakdown-info">
              <div class="breakdown-rank">{{ index + 1 }}</div>
              <div class="breakdown-name">{{ agent.agent_name }}</div>
            </div>
            <div class="breakdown-stats">
              <div class="breakdown-cost">${{ agent.cost.toFixed(2) }}</div>
              <div class="breakdown-executions">{{ agent.executions }} 次执行</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Alerts Section -->
    <div class="glass-card alerts-card">
      <div class="card-header">
        <h2 class="card-title">使用警报</h2>
        <span class="alert-count">{{ alerts.length }} 警报</span>
      </div>

      <div class="alerts-list" v-if="alerts.length > 0">
        <div
          v-for="alert in alerts"
          :key="alert.id"
          class="alert-item glass-panel"
          :class="`alert-${alert.severity}`"
        >
          <div class="alert-icon">
            <svg v-if="alert.severity === 'high'" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M12 9v4M12 17h.01" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <svg v-else viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M13 2L3 14h9l-1 8 10-12-9-4z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <div class="alert-content">
            <div class="alert-header">
              <span class="alert-type">{{ alert.usage_type === 'monthly' ? '月度' : '每日' }}使用量</span>
              <span class="alert-time">{{ formatDate(alert.created_at) }}</span>
            </div>
            <div class="alert-message">{{ alert.alert_message }}</div>
            <div class="alert-stats">
              <span class="alert-usage">${{ alert.current_usage.toFixed(2) }} / ${{ alert.quota }}</span>
              <span class="alert-percentage" :class="getPercentageClass(alert.percentage)">
                {{ alert.percentage }}%
              </span>
            </div>
          </div>
          <button class="alert-action" @click="dismissAlert(alert.id)" aria-label="关闭警报">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M18 6L6 18M6 6l12 12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </button>
        </div>
      </div>

      <div v-else class="no-alerts">
        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        <h3>无活动警报</h3>
        <p>您的使用量在正常范围内</p>
      </div>
    </div>

    <!-- Quota Management -->
    <div class="glass-card quota-card">
      <div class="card-header">
        <h2 class="card-title">配额管理</h2>
        <button class="glass-button primary" @click="increaseQuota">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="btn-icon">
            <path d="M12 5v14M5 12h14" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          增加配额
        </button>
      </div>

      <div class="quota-list">
        <div
          v-for="quota in quotas"
          :key="quota.type"
          class="quota-item glass-panel"
        >
          <div class="quota-info">
            <div class="quota-name">{{ quota.name }}</div>
            <div class="quota-description">{{ quota.description }}</div>
          </div>
          <div class="quota-progress">
            <div class="progress-bar">
              <div
                class="progress-fill"
                :class="getProgressClass(quota.percentage)"
                :style="{ width: `${quota.percentage}%` }"
              ></div>
            </div>
            <div class="quota-stats">
              <span class="quota-used">{{ quota.used.toLocaleString() }}</span>
              <span class="quota-total">/ {{ quota.total.toLocaleString() }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import axios from '@/api/index'

const timeRange = ref('month')
const dashboard = ref({
  total_executions: 0,
  total_tokens: 0,
  total_cost: 0,
  monthly_cost: 0,
  active_quotas: 0,
  pending_alerts: 0
})

const agentBreakdown = ref([])
const alerts = ref([])
const quotas = ref([])

// 加载使用统计
async function loadUsageStats() {
  try {
    const response = await axios.get('/v1/Billing/usage')
    if (response.data && response.data.code === 200) {
      const data = response.data.data
      dashboard.value.total_executions = data.total_executions || 0
      dashboard.value.total_tokens = data.total_tokens || 0
      dashboard.value.total_cost = data.total_cost || 0
    }
  } catch (error) {
    console.error('Failed to load usage stats:', error)
  }
}

// 加载代理成本分解
async function loadAgentBreakdown() {
  try {
    const response = await axios.get('/v1/Billing/agent-breakdown')
    if (response.data && response.data.code === 200) {
      agentBreakdown.value = response.data.data || []
    }
  } catch (error) {
    console.error('Failed to load agent breakdown:', error)
  }
}

// 加载警报
async function loadAlerts() {
  try {
    const response = await axios.get('/v1/Billing/alerts')
    if (response.data && response.data.code === 200) {
      alerts.value = response.data.data || []
      dashboard.value.pending_alerts = alerts.value.length
    }
  } catch (error) {
    console.error('Failed to load alerts:', error)
  }
}

// 加载配额
async function loadQuotas() {
  try {
    const response = await axios.get('/v1/Billing/quotas')
    if (response.data && response.data.code === 200) {
      const quotaData = response.data.data || []
      dashboard.value.active_quotas = quotaData.length
      
      // 转换配额数据格式
      quotas.value = quotaData.map(quota => ({
        name: quota.quota_type === 'budget' ? '月度预算' : 
              quota.quota_type === 'tokens' ? '令牌配额' : 'API 调用',
        description: quota.description || '',
        used: quota.current_usage || 0,
        total: quota.quota_limit || 0,
        type: quota.quota_type
      }))
    }
  } catch (error) {
    console.error('Failed to load quotas:', error)
  }
}

const totalCost = computed(() => dashboard.value.total_cost)
const totalTokens = computed(() => dashboard.value.total_tokens)
const totalExecutions = computed(() => dashboard.value.total_executions)
const activeQuotas = computed(() => dashboard.value.active_quotas)
const pendingAlerts = computed(() => dashboard.value.pending_alerts)
const costTrend = computed(() => 12.5)

function formatDate(dateString) {
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

function getPercentageClass(percentage) {
  if (percentage >= 90) return 'percentage-critical'
  if (percentage >= 75) return 'percentage-warning'
  return 'percentage-normal'
}

function getProgressClass(percentage) {
  if (percentage >= 90) return 'progress-critical'
  if (percentage >= 75) return 'progress-warning'
  return 'progress-normal'
}

async function downloadReport() {
  try {
    ElMessage.info('正在生成使用报告...')
    const response = await axios.get('/v1/Billing/usage', {
      params: { format: 'csv' },
      responseType: 'blob'
    })
    
    // 创建下载链接
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `usage-report-${new Date().toISOString().split('T')[0]}.csv`)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    
    ElMessage.success('报告下载成功')
  } catch (error) {
    console.error('Failed to download report:', error)
    ElMessage.error('下载报告失败')
  }
}

function managePaymentMethods() {
  ElMessage.info('支付方式管理功能即将推出')
  // 未来可以打开支付方式管理对话框
}

function viewAllBreakdown() {
  // 显示所有代理的成本明细
  if (agentBreakdown.value.length === 0) {
    ElMessage.warning('暂无成本数据')
    return
  }
  ElMessage.info('显示完整成本明细')
  // 未来可以打开详细视图对话框或跳转到详细页面
}

async function increaseQuota() {
  try {
    // 简单示例：增加配额
    ElMessage.info('配额增加功能即将推出')
    // 未来可以打开配额增加表单对话框
  } catch (error) {
    console.error('Failed to increase quota:', error)
    ElMessage.error('增加配额失败')
  }
}

async function dismissAlert(alertId) {
  try {
    await axios.delete(`/v1/Billing/alerts/${alertId}`)
    alerts.value = alerts.value.filter(a => a.id !== alertId)
    dashboard.value.pending_alerts = alerts.value.length
    ElMessage.success('警报已关闭')
  } catch (error) {
    console.error('Failed to dismiss alert:', error)
    ElMessage.error('关闭警报失败')
  }
}

// 页面加载时获取所有数据
onMounted(() => {
  loadUsageStats()
  loadAgentBreakdown()
  loadAlerts()
  loadQuotas()
})
</script>

<style scoped>
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

.glass-button {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--color-border-glass);
  color: var(--color-text-primary);
  padding: var(--space-2) var(--space-4);
  border-radius: var(--radius-lg);
  font-weight: var(--font-medium);
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.glass-button:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: var(--color-text-secondary);
}

.glass-button.primary {
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-dark) 100%);
  border: none;
  color: white;
  box-shadow: 0 4px 15px rgba(139, 92, 246, 0.3);
}

.glass-button.primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(139, 92, 246, 0.5);
}

.billing-container {
  max-width: var(--container-xl);
  margin: 0 auto;
  padding: var(--space-6);
}

/* Page Header */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: var(--space-4);
  margin-bottom: var(--space-8);
}

.page-title {
  font-size: var(--text-4xl);
  font-weight: var(--font-bold);
  color: var(--color-text-primary);
  margin: 0 0 var(--space-2);
  text-shadow: 0 0 20px rgba(var(--color-primary-rgb), 0.3);
}

.page-description {
  font-size: var(--text-base);
  color: var(--color-text-secondary);
  margin: 0;
}

.header-actions {
  display: flex;
  gap: var(--space-3);
  align-items: center;
}

.btn-icon {
  width: 18px;
  height: 18px;
  margin-right: var(--space-2);
}

/* Summary Grid */
.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: var(--space-6);
  margin-bottom: var(--space-8);
}

.summary-card {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  padding: var(--space-6);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.summary-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.2);
}

.card-glow-effect {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: radial-gradient(circle at top right, rgba(255, 255, 255, 0.1), transparent 70%);
  opacity: 0;
  transition: opacity 0.3s ease;
  pointer-events: none;
}

.summary-card:hover .card-glow-effect {
  opacity: 1;
}

.summary-primary {
  border-left: 4px solid var(--color-primary);
}

.summary-accent {
  border-left: 4px solid var(--color-accent);
}

.summary-success {
  border-left: 4px solid var(--color-success);
}

.summary-warning {
  border-left: 4px solid var(--color-warning);
}

.summary-icon {
  width: 56px;
  height: 56px;
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  flex-shrink: 0;
  box-shadow: inset 0 0 12px rgba(0, 0, 0, 0.2);
}

.summary-primary .summary-icon {
  color: var(--color-primary);
  background: rgba(var(--color-primary-rgb), 0.1);
  border-color: rgba(var(--color-primary-rgb), 0.2);
}

.summary-accent .summary-icon {
  color: var(--color-accent);
  background: rgba(var(--color-accent-rgb), 0.1);
  border-color: rgba(var(--color-accent-rgb), 0.2);
}

.summary-success .summary-icon {
  color: var(--color-success);
  background: rgba(var(--color-success-rgb), 0.1);
  border-color: rgba(var(--color-success-rgb), 0.2);
}

.summary-warning .summary-icon {
  color: var(--color-warning);
  background: rgba(var(--color-warning-rgb), 0.1);
  border-color: rgba(var(--color-warning-rgb), 0.2);
}

.summary-icon svg {
  width: 28px;
  height: 28px;
}

.summary-content {
  flex: 1;
}

.summary-value {
  font-size: var(--text-3xl);
  font-weight: var(--font-bold);
  margin-bottom: var(--space-1);
  color: var(--color-text-primary);
  text-shadow: 0 0 10px rgba(0, 0, 0, 0.3);
}

.summary-label {
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--color-text-secondary);
  margin-bottom: var(--space-1);
}

.stat-label {
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--color-text-secondary);
}

.summary-sub {
  font-size: var(--text-xs);
  color: var(--color-text-muted);
}

.summary-trend {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-size: var(--text-sm);
  font-weight: var(--font-semibold);
}

.trend-up {
  color: var(--color-success);
}

.trend-down {
  color: var(--color-error);
}

.trend-up svg,
.trend-down svg {
  width: 16px;
  height: 16px;
}

/* Dashboard Grid */
.dashboard-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: var(--space-6);
  margin-bottom: var(--space-8);
}

/* Card Styles */
.card-header {
  padding: var(--space-6);
  border-bottom: 1px solid var(--color-border-glass);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  font-size: var(--text-lg);
  font-weight: var(--font-bold);
  color: var(--color-text-primary);
  margin: 0;
}

.card-actions {
  display: flex;
  gap: var(--space-2);
}

.filter-btn {
  padding: var(--space-2) var(--space-4);
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--color-text-secondary);
  background: transparent;
  border: 1px solid var(--color-border-glass);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all 0.2s ease-out;
}

.filter-btn:hover {
  color: var(--color-primary);
  border-color: var(--color-primary);
  background: rgba(var(--color-primary-rgb), 0.1);
}

.filter-btn.active {
  background: var(--color-primary);
  color: white;
  border-color: var(--color-primary);
  box-shadow: 0 0 10px rgba(var(--color-primary-rgb), 0.4);
}

.view-all-btn {
  color: var(--color-primary);
  background: transparent;
  border: none;
  font-size: var(--text-sm);
  font-weight: var(--font-semibold);
  cursor: pointer;
  transition: all 0.2s ease-out;
}

.view-all-btn:hover {
  text-shadow: 0 0 8px rgba(var(--color-primary-rgb), 0.6);
}

/* Chart Card */
.chart-card {
  min-height: 400px;
}

.chart-container {
  padding: var(--space-6);
}

.chart-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  min-height: 300px;
  color: var(--color-text-muted);
}

.placeholder-icon {
  width: 64px;
  height: 64px;
  margin-bottom: var(--space-4);
  opacity: 0.5;
  filter: drop-shadow(0 0 10px rgba(255, 255, 255, 0.1));
}

.chart-placeholder p {
  font-size: var(--text-base);
  margin-bottom: var(--space-2);
}

.chart-placeholder small {
  font-size: var(--text-sm);
  opacity: 0.7;
}

/* Breakdown Card */
.breakdown-list {
  padding: var(--space-4);
  max-height: 400px;
  overflow-y: auto;
}

.breakdown-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-4);
  border-radius: var(--radius-lg);
  margin-bottom: var(--space-2);
  transition: all 0.2s ease-out;
}

.breakdown-item:hover {
  background: rgba(255, 255, 255, 0.08);
  transform: translateX(4px);
  border-color: var(--color-border-hover);
}

.breakdown-info {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.breakdown-rank {
  width: 28px;
  height: 28px;
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-dark) 100%);
  color: white;
  border-radius: var(--radius-full);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--text-sm);
  font-weight: var(--font-bold);
  box-shadow: 0 2px 8px rgba(var(--color-primary-rgb), 0.4);
}

.breakdown-name {
  font-size: var(--text-sm);
  font-weight: var(--font-semibold);
  color: var(--color-text-primary);
}

.breakdown-stats {
  text-align: right;
}

.breakdown-cost {
  font-size: var(--text-lg);
  font-weight: var(--font-bold);
  color: var(--color-text-primary);
  margin-bottom: var(--space-1);
}

.breakdown-executions {
  font-size: var(--text-xs);
  color: var(--color-text-muted);
}

/* Alerts Card */
.alerts-card {
  margin-bottom: var(--space-8);
}

.alert-count {
  padding: var(--space-1) var(--space-3);
  background: rgba(var(--color-error-rgb), 0.2);
  color: var(--color-error);
  border: 1px solid rgba(var(--color-error-rgb), 0.3);
  border-radius: var(--radius-full);
  font-size: var(--text-xs);
  font-weight: var(--font-semibold);
}

.alerts-list {
  padding: var(--space-4);
  max-height: 500px;
  overflow-y: auto;
}

.alert-item {
  display: flex;
  gap: var(--space-4);
  padding: var(--space-4);
  border-radius: var(--radius-lg);
  margin-bottom: var(--space-3);
  border-left: 4px solid transparent;
  transition: all 0.2s ease-out;
}

.alert-item.alert-high {
  border-left-color: var(--color-error);
  background: rgba(var(--color-error-rgb), 0.05);
}

.alert-item.alert-medium {
  border-left-color: var(--color-warning);
  background: rgba(var(--color-warning-rgb), 0.05);
}

.alert-item:hover {
  transform: translateX(4px);
  background: rgba(255, 255, 255, 0.08);
}

.alert-icon {
  width: 40px;
  height: 40px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.05);
  border-radius: var(--radius-lg);
  color: var(--color-error);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.alert-item.alert-medium .alert-icon {
  color: var(--color-warning);
}

.alert-icon svg {
  width: 20px;
  height: 20px;
}

.alert-content {
  flex: 1;
}

.alert-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-2);
}

.alert-type {
  font-size: var(--text-xs);
  font-weight: var(--font-semibold);
  color: var(--color-text-secondary);
  text-transform: uppercase;
}

.alert-time {
  font-size: var(--text-xs);
  color: var(--color-text-muted);
}

.alert-message {
  font-size: var(--text-sm);
  color: var(--color-text-primary);
  margin-bottom: var(--space-2);
  font-weight: var(--font-medium);
}

.alert-stats {
  display: flex;
  gap: var(--space-4);
  align-items: center;
}

.alert-usage {
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
  font-weight: var(--font-semibold);
}

.alert-percentage {
  padding: var(--space-1) var(--space-2);
  border-radius: var(--radius-full);
  font-size: var(--text-xs);
  font-weight: var(--font-bold);
}

.percentage-critical {
  background: var(--color-error);
  color: white;
  box-shadow: 0 0 10px rgba(var(--color-error-rgb), 0.4);
}

.percentage-warning {
  background: var(--color-warning);
  color: white;
  box-shadow: 0 0 10px rgba(var(--color-warning-rgb), 0.4);
}

.percentage-normal {
  background: var(--color-success);
  color: white;
  box-shadow: 0 0 10px rgba(var(--color-success-rgb), 0.4);
}

.alert-action {
  width: 32px;
  height: 32px;
  border: none;
  background: transparent;
  color: var(--color-text-muted);
  border-radius: var(--radius-lg);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease-out;
  flex-shrink: 0;
}

.alert-action:hover {
  background: rgba(255, 255, 255, 0.1);
  color: var(--color-error);
}

.alert-action svg {
  width: 16px;
  height: 16px;
}

.no-alerts {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--space-12);
  text-align: center;
  color: var(--color-text-muted);
}

.no-alerts svg {
  width: 64px;
  height: 64px;
  margin-bottom: var(--space-4);
  opacity: 0.5;
  filter: drop-shadow(0 0 10px rgba(255, 255, 255, 0.1));
}

.no-alerts h3 {
  font-size: var(--text-lg);
  font-weight: var(--font-semibold);
  color: var(--color-text-primary);
  margin-bottom: var(--space-2);
}

.no-alerts p {
  font-size: var(--text-sm);
}

/* Quota Card */
.quota-card {
  margin-bottom: var(--space-8);
}

.quota-list {
  padding: var(--space-4);
}

.quota-item {
  padding: var(--space-4);
  border-radius: var(--radius-lg);
  margin-bottom: var(--space-4);
  transition: all 0.2s ease-out;
}

.quota-item:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: var(--color-border-hover);
}

.quota-info {
  margin-bottom: var(--space-3);
}

.quota-name {
  font-size: var(--text-base);
  font-weight: var(--font-bold);
  color: var(--color-text-primary);
  margin-bottom: var(--space-1);
}

.quota-description {
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
}

.quota-progress {
  margin-top: var(--space-3);
}

.progress-bar {
  height: 8px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: var(--radius-full);
  overflow: hidden;
  margin-bottom: var(--space-2);
}

.progress-fill {
  height: 100%;
  border-radius: var(--radius-full);
  transition: width 0.3s ease-out;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.3);
}

.progress-critical {
  background: var(--color-error);
}

.progress-warning {
  background: var(--color-warning);
}

.progress-normal {
  background: var(--color-success);
}

.quota-stats {
  display: flex;
  justify-content: space-between;
  font-size: var(--text-sm);
}

.quota-used {
  color: var(--color-text-primary);
  font-weight: var(--font-semibold);
}

.quota-total {
  color: var(--color-text-muted);
}

/* Responsive */
@media (max-width: 1200px) {
  .dashboard-grid {
    grid-template-columns: 1fr;
  }

  .summary-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: stretch;
  }

  .header-actions {
    flex-wrap: wrap;
  }

  .glass-button {
    width: 100%;
    justify-content: center;
  }

  .summary-grid {
    grid-template-columns: 1fr;
  }

  .breakdown-stats {
    text-align: left;
    margin-top: var(--space-2);
  }
}

@media (max-width: 480px) {
  .page-title {
    font-size: var(--text-3xl);
  }
  
  .billing-container {
    padding: var(--space-4);
  }
}

/* Scrollbar */
.breakdown-list::-webkit-scrollbar,
.alerts-list::-webkit-scrollbar {
  width: 6px;
}

.breakdown-list::-webkit-scrollbar-track,
.alerts-list::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.05);
  border-radius: var(--radius-full);
}

.breakdown-list::-webkit-scrollbar-thumb,
.alerts-list::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
  border-radius: var(--radius-full);
}

.breakdown-list::-webkit-scrollbar-thumb:hover,
.alerts-list::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.3);
}
</style>
