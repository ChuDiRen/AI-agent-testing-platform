<template>
  <PageWrapper>
    <div class="workbench">
      <!-- 欢迎区域 -->
      <div class="welcome-section">
        <NCard>
          <div class="welcome-content">
            <div class="welcome-text">
              <h1>欢迎回来，{{ userStore.userInfo?.username || '用户' }}！</h1>
              <p>今天是 {{ currentDate }}，让我们开始高效的工作吧！</p>
              <div class="welcome-stats">
                <NTag type="success" size="small">
                  <template #icon>
                    <Icon name="mdi:clock-outline" />
                  </template>
                  最后登录：{{ lastLoginTime }}
                </NTag>
              </div>
            </div>
            <div class="welcome-avatar">
              <NAvatar
                round
                :size="80"
                :src="userStore.userInfo?.avatar"
                fallback-src="https://avatars.githubusercontent.com/u/54677442?v=4"
              />
            </div>
          </div>
        </NCard>
      </div>

      <!-- 统计卡片 -->
      <div class="stats-section">
        <NGrid :cols="4" :x-gap="16" responsive="screen">
          <NGridItem v-for="stat in stats" :key="stat.title">
            <NCard hoverable class="stat-card-wrapper">
              <div class="stat-card">
                <div class="stat-icon" :style="{ backgroundColor: stat.color + '20', color: stat.color }">
                  <Icon :name="stat.icon" :size="24" />
                </div>
                <div class="stat-content">
                  <div class="stat-value">{{ stat.value }}</div>
                  <div class="stat-title">{{ stat.title }}</div>
                  <div class="stat-trend" :class="stat.trend > 0 ? 'trend-up' : 'trend-down'">
                    <Icon :name="stat.trend > 0 ? 'mdi:trending-up' : 'mdi:trending-down'" :size="16" />
                    {{ Math.abs(stat.trend) }}%
                  </div>
                </div>
              </div>
            </NCard>
          </NGridItem>
        </NGrid>
      </div>

      <!-- 图表和快捷操作 -->
      <NGrid :cols="3" :x-gap="16" responsive="screen">
        <NGridItem :span="2">
          <NCard title="数据概览" class="chart-card">
            <template #header-extra>
              <NButtonGroup size="small">
                <NButton
                  v-for="period in timePeriods"
                  :key="period.value"
                  :type="selectedPeriod === period.value ? 'primary' : 'default'"
                  @click="selectedPeriod = period.value"
                >
                  {{ period.label }}
                </NButton>
              </NButtonGroup>
            </template>
            <div class="chart-container">
              <div class="chart-placeholder">
                <Icon name="mdi:chart-line" :size="48" />
                <p>{{ selectedPeriod }} 数据趋势图</p>
                <NProgress type="line" :percentage="75" />
              </div>
            </div>
          </NCard>
        </NGridItem>

        <NGridItem>
          <NCard title="快捷操作" class="quick-actions-card">
            <NSpace vertical>
              <NButton
                v-for="action in quickActions"
                :key="action.name"
                :type="action.type"
                block
                @click="handleQuickAction(action)"
              >
                <template #icon>
                  <Icon :name="action.icon" />
                </template>
                {{ action.name }}
              </NButton>
            </NSpace>
          </NCard>
        </NGridItem>
      </NGrid>
    </div>
  </PageWrapper>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Icon } from '@iconify/vue'
import { useUserStore } from '@/store'
import { PageWrapper } from '@/components'
import { formatDate } from '@/utils'

defineOptions({ name: '工作台' })

const userStore = useUserStore()
const selectedPeriod = ref('week')

// 当前日期
const currentDate = computed(() => {
  return formatDate(new Date(), 'YYYY年MM月DD日')
})

// 最后登录时间
const lastLoginTime = computed(() => {
  const lastLogin = userStore.userInfo?.last_login
  return lastLogin ? formatDate(new Date(lastLogin), 'MM-DD HH:mm') : '首次登录'
})

// 统计数据
const stats = ref([
  {
    title: '总用户数',
    value: '1,234',
    icon: 'mdi:account-group',
    color: '#18a058',
    trend: 12.5,
  },
  {
    title: '今日访问',
    value: '856',
    icon: 'mdi:eye',
    color: '#2080f0',
    trend: 8.2,
  },
  {
    title: '系统消息',
    value: '23',
    icon: 'mdi:message-text',
    color: '#f0a020',
    trend: -2.1,
  },
  {
    title: '待处理',
    value: '5',
    icon: 'mdi:clipboard-list',
    color: '#d03050',
    trend: -15.3,
  },
])

// 时间周期选项
const timePeriods = [
  { label: '今日', value: 'today' },
  { label: '本周', value: 'week' },
  { label: '本月', value: 'month' },
  { label: '本年', value: 'year' },
]

// 快捷操作
const quickActions = [
  {
    name: '新建用户',
    icon: 'mdi:account-plus',
    type: 'primary',
    action: 'create-user',
  },
  {
    name: '系统设置',
    icon: 'mdi:cog',
    type: 'default',
    action: 'system-settings',
  },
  {
    name: '数据备份',
    icon: 'mdi:database-export',
    type: 'default',
    action: 'backup-data',
  },
  {
    name: '查看日志',
    icon: 'mdi:file-document-outline',
    type: 'default',
    action: 'view-logs',
  },
]

// 处理快捷操作
const handleQuickAction = (action) => {
  window.$message?.info(`执行操作：${action.name}`)
}

// 初始化
onMounted(() => {
  // 可以在这里加载统计数据
})
</script>

<style scoped>
.workbench {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.welcome-section {
  margin-bottom: 20px;
}

.welcome-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px;
}

.welcome-text h1 {
  margin: 0 0 8px 0;
  font-size: 24px;
  font-weight: 600;
  color: var(--text-color-1);
}

.welcome-text p {
  margin: 0 0 12px 0;
  color: var(--text-color-2);
  font-size: 16px;
}

.welcome-stats {
  margin-top: 12px;
}

.stats-section {
  margin-bottom: 20px;
}

.stat-card-wrapper {
  transition: transform 0.2s ease;
}

.stat-card-wrapper:hover {
  transform: translateY(-2px);
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 24px;
  font-weight: 600;
  color: var(--text-color-1);
  margin-bottom: 4px;
}

.stat-title {
  font-size: 14px;
  color: var(--text-color-2);
  margin-bottom: 4px;
}

.stat-trend {
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.trend-up {
  color: #18a058;
}

.trend-down {
  color: #d03050;
}

.chart-card {
  height: 400px;
}

.chart-container {
  height: 320px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.chart-placeholder {
  text-align: center;
  color: var(--text-color-3);
}

.chart-placeholder p {
  margin: 12px 0;
  font-size: 16px;
}

.quick-actions-card {
  height: 400px;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .n-grid-item[span="2"] {
    grid-column: span 3;
  }

  .n-grid-item:last-child {
    grid-column: span 3;
  }
}

@media (max-width: 768px) {
  .welcome-content {
    flex-direction: column;
    gap: 16px;
    align-items: center;
    text-align: center;
  }

  .stats-section .n-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .chart-card,
  .quick-actions-card {
    height: auto;
  }
}

@media (max-width: 480px) {
  .stats-section .n-grid {
    grid-template-columns: 1fr;
  }
}
</style>
