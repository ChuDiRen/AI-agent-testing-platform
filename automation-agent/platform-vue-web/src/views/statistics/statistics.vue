<template>
  <div class="statistics-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1 class="page-title">数据统计</h1>
      <p class="page-subtitle">实时监控测试数据和执行情况</p>
    </div>

    <!-- 数据卡片区域 -->
    <div class="stats-cards">
      <div class="stat-card">
        <div class="card-icon primary">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <div class="card-content">
          <div class="card-label">总用例数</div>
          <div class="card-value">1,234</div>
          <div class="card-trend positive">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <span>12.5%</span>
          </div>
        </div>
      </div>

      <div class="stat-card">
        <div class="card-icon success">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <div class="card-content">
          <div class="card-label">通过率</div>
          <div class="card-value">95.8%</div>
          <div class="card-trend positive">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <span>2.3%</span>
          </div>
        </div>
      </div>

      <div class="stat-card">
        <div class="card-icon warning">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <div class="card-content">
          <div class="card-label">执行次数</div>
          <div class="card-value">8,567</div>
          <div class="card-trend positive">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <span>8.1%</span>
          </div>
        </div>
      </div>

      <div class="stat-card">
        <div class="card-icon error">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <div class="card-content">
          <div class="card-label">失败用例</div>
          <div class="card-value">52</div>
          <div class="card-trend negative">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M13 17h8m0 0V9m0 8l-8-8-4 4-6-6" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <span>-5.2%</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 图表区域 -->
    <div class="charts-section">
      <div class="chart-card">
        <div class="chart-header">
          <h3 class="chart-title">执行趋势</h3>
          <div class="chart-actions">
            <button class="chart-btn active">周</button>
            <button class="chart-btn">月</button>
            <button class="chart-btn">年</button>
          </div>
        </div>
        <div class="chart-body">
          <div ref="trendChart" class="chart-container"></div>
        </div>
      </div>

      <div class="chart-card">
        <div class="chart-header">
          <h3 class="chart-title">用例分布</h3>
        </div>
        <div class="chart-body">
          <div ref="pieChart" class="chart-container"></div>
        </div>
      </div>
    </div>

    <!-- 最近执行记录 -->
    <div class="recent-section">
      <div class="section-header">
        <h3 class="section-title">最近执行</h3>
        <a href="#" class="section-link">查看全部</a>
      </div>
      <div class="recent-list">
        <div class="recent-item" v-for="i in 5" :key="i">
          <div class="item-icon success">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M5 13l4 4L19 7" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <div class="item-content">
            <div class="item-title">API 接口测试计划 #{{ i }}</div>
            <div class="item-meta">执行时间: 2026-01-17 10:30:00</div>
          </div>
          <div class="item-badge success">通过</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import * as echarts from 'echarts';

const trendChart = ref(null);
const pieChart = ref(null);

onMounted(() => {
  initTrendChart();
  initPieChart();
});

const initTrendChart = () => {
  if (!trendChart.value) return;
  
  const chart = echarts.init(trendChart.value);
  const option = {
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(255, 255, 255, 0.95)',
      borderColor: '#E2E8F0',
      textStyle: { color: '#1E293B' }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      top: '10%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
      axisLine: { lineStyle: { color: '#E2E8F0' } },
      axisLabel: { color: '#64748B' }
    },
    yAxis: {
      type: 'value',
      axisLine: { lineStyle: { color: '#E2E8F0' } },
      axisLabel: { color: '#64748B' },
      splitLine: { lineStyle: { color: '#F1F5F9' } }
    },
    series: [
      {
        name: '执行次数',
        type: 'line',
        smooth: true,
        data: [120, 132, 101, 134, 90, 230, 210],
        itemStyle: { color: '#2563EB' },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(37, 99, 235, 0.3)' },
              { offset: 1, color: 'rgba(37, 99, 235, 0.05)' }
            ]
          }
        }
      }
    ]
  };
  chart.setOption(option);
  
  window.addEventListener('resize', () => chart.resize());
};

const initPieChart = () => {
  if (!pieChart.value) return;
  
  const chart = echarts.init(pieChart.value);
  const option = {
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(255, 255, 255, 0.95)',
      borderColor: '#E2E8F0',
      textStyle: { color: '#1E293B' }
    },
    legend: {
      bottom: '5%',
      left: 'center',
      textStyle: { color: '#64748B' }
    },
    series: [
      {
        name: '用例状态',
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: false,
          position: 'center'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 20,
            fontWeight: 'bold'
          }
        },
        labelLine: {
          show: false
        },
        data: [
          { value: 1048, name: '通过', itemStyle: { color: '#10B981' } },
          { value: 735, name: '失败', itemStyle: { color: '#EF4444' } },
          { value: 580, name: '跳过', itemStyle: { color: '#F59E0B' } },
          { value: 484, name: '待执行', itemStyle: { color: '#94A3B8' } }
        ]
      }
    ]
  };
  chart.setOption(option);
  
  window.addEventListener('resize', () => chart.resize());
};
</script>

<style scoped>
.statistics-page {
  padding: 2rem;
  background: var(--color-bg-primary);
  min-height: calc(100vh - 70px);
}

/* 页面标题 */
.page-header {
  margin-bottom: 2rem;
}

.page-title {
  font-family: var(--font-heading);
  font-size: var(--text-3xl);
  font-weight: 700;
  color: var(--color-text-primary);
  margin-bottom: 0.5rem;
}

.page-subtitle {
  font-size: var(--text-base);
  color: var(--color-text-muted);
}

/* 数据卡片 */
.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: white;
  border-radius: var(--radius-lg);
  padding: 1.5rem;
  display: flex;
  gap: 1rem;
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--color-border);
  transition: all var(--transition-base);
}

.stat-card:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}

.card-icon {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.card-icon svg {
  width: 24px;
  height: 24px;
  color: white;
}

.card-icon.primary {
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-light) 100%);
}

.card-icon.success {
  background: linear-gradient(135deg, #10B981 0%, #34D399 100%);
}

.card-icon.warning {
  background: linear-gradient(135deg, #F59E0B 0%, #FBBF24 100%);
}

.card-icon.error {
  background: linear-gradient(135deg, #EF4444 0%, #F87171 100%);
}

.card-content {
  flex: 1;
}

.card-label {
  font-size: var(--text-sm);
  color: var(--color-text-muted);
  margin-bottom: 0.5rem;
}

.card-value {
  font-family: var(--font-heading);
  font-size: var(--text-3xl);
  font-weight: 700;
  color: var(--color-text-primary);
  margin-bottom: 0.5rem;
}

.card-trend {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: var(--text-sm);
  font-weight: 500;
}

.card-trend svg {
  width: 16px;
  height: 16px;
}

.card-trend.positive {
  color: var(--color-success);
}

.card-trend.negative {
  color: var(--color-error);
}

/* 图表区域 */
.charts-section {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.chart-card {
  background: white;
  border-radius: var(--radius-lg);
  padding: 1.5rem;
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--color-border);
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.chart-title {
  font-family: var(--font-heading);
  font-size: var(--text-lg);
  font-weight: 600;
  color: var(--color-text-primary);
}

.chart-actions {
  display: flex;
  gap: 0.5rem;
}

.chart-btn {
  padding: 0.5rem 1rem;
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
  background: transparent;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-base);
}

.chart-btn:hover {
  background: var(--color-bg-hover);
}

.chart-btn.active {
  background: var(--color-primary);
  color: white;
  border-color: var(--color-primary);
}

.chart-container {
  width: 100%;
  height: 300px;
}

/* 最近执行 */
.recent-section {
  background: white;
  border-radius: var(--radius-lg);
  padding: 1.5rem;
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--color-border);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.section-title {
  font-family: var(--font-heading);
  font-size: var(--text-lg);
  font-weight: 600;
  color: var(--color-text-primary);
}

.section-link {
  font-size: var(--text-sm);
  color: var(--color-primary);
  text-decoration: none;
  transition: color var(--transition-base);
}

.section-link:hover {
  color: var(--color-primary-dark);
}

.recent-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.recent-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  border-radius: var(--radius-md);
  transition: background var(--transition-base);
}

.recent-item:hover {
  background: var(--color-bg-hover);
}

.item-icon {
  width: 40px;
  height: 40px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.item-icon svg {
  width: 20px;
  height: 20px;
  color: white;
}

.item-icon.success {
  background: var(--color-success);
}

.item-content {
  flex: 1;
}

.item-title {
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--color-text-primary);
  margin-bottom: 0.25rem;
}

.item-meta {
  font-size: var(--text-xs);
  color: var(--color-text-muted);
}

.item-badge {
  padding: 0.25rem 0.75rem;
  font-size: var(--text-xs);
  font-weight: 500;
  border-radius: var(--radius-full);
}

.item-badge.success {
  background: rgba(16, 185, 129, 0.1);
  color: var(--color-success);
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .charts-section {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .statistics-page {
    padding: 1rem;
  }
  
  .stats-cards {
    grid-template-columns: 1fr;
  }
}
</style>