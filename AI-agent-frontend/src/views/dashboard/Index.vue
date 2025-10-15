<script setup>
import { onMounted, ref } from 'vue'
import {
  NCard,
  NGrid,
  NGridItem,
  NStatistic,
  NSpin,
  NSpace,
  NTag,
  NButton,
  NDataTable,
  NProgress,
} from 'naive-ui'
import { formatDate, renderIcon } from '@/utils'
import api from '@/api'
import TheIcon from '@/components/icon/TheIcon.vue'

defineOptions({ name: 'Dashboard' })

const loading = ref(false)
const statistics = ref({
  total_agents: 0,
  active_agents: 0,
  total_test_cases: 0,
  total_reports: 0,
  recent_executions: 0,
  success_rate: 0,
  avg_execution_time: 0,
  total_api_calls: 0,
})

const recentReports = ref([])
const agentStatus = ref([])

// 统计卡片配置
const statsCards = [
  {
    label: 'AI代理总数',
    key: 'total_agents',
    icon: 'mdi:robot',
    color: '#18a058',
    prefix: '',
    suffix: '个',
  },
  {
    label: '活跃代理',
    key: 'active_agents',
    icon: 'mdi:robot-happy',
    color: '#2080f0',
    prefix: '',
    suffix: '个',
  },
  {
    label: '测试用例',
    key: 'total_test_cases',
    icon: 'mdi:test-tube',
    color: '#f0a020',
    prefix: '',
    suffix: '个',
  },
  {
    label: '测试报告',
    key: 'total_reports',
    icon: 'mdi:file-chart',
    color: '#d03050',
    prefix: '',
    suffix: '份',
  },
  {
    label: '最近执行',
    key: 'recent_executions',
    icon: 'mdi:play-circle',
    color: '#7c4dff',
    prefix: '',
    suffix: '次',
  },
  {
    label: '成功率',
    key: 'success_rate',
    icon: 'mdi:chart-line',
    color: '#00bfa5',
    prefix: '',
    suffix: '%',
  },
  {
    label: '平均执行时间',
    key: 'avg_execution_time',
    icon: 'mdi:clock-outline',
    color: '#ff6f00',
    prefix: '',
    suffix: 's',
  },
  {
    label: 'API调用总数',
    key: 'total_api_calls',
    icon: 'mdi:api',
    color: '#536dfe',
    prefix: '',
    suffix: '次',
  },
]

// 最近报告表格列
const reportColumns = [
  {
    title: '报告名称',
    key: 'name',
    ellipsis: { tooltip: true },
  },
  {
    title: '测试类型',
    key: 'test_type',
    width: 100,
    render(row) {
      const typeMap = {
        functional: '功能',
        performance: '性能',
        security: '安全',
        ui: 'UI',
        api: 'API',
      }
      return typeMap[row.test_type] || row.test_type
    },
  },
  {
    title: '通过率',
    key: 'pass_rate',
    width: 150,
    render(row) {
      const total = row.total_cases || 0
      const passed = row.passed_cases || 0
      const rate = total > 0 ? Math.round((passed / total) * 100) : 0
      return h(NProgress, {
        type: 'line',
        percentage: rate,
        status: rate >= 90 ? 'success' : rate >= 60 ? 'warning' : 'error',
      })
    },
  },
  {
    title: '创建时间',
    key: 'created_at',
    width: 180,
    render(row) {
      return formatDate(row.created_at)
    },
  },
]

// 代理状态表格列
const agentColumns = [
  {
    title: '代理名称',
    key: 'name',
    ellipsis: { tooltip: true },
  },
  {
    title: '类型',
    key: 'type',
    width: 100,
    render(row) {
      const typeMap = {
        chat: '对话',
        task: '任务',
        workflow: '工作流',
        test: '测试',
      }
      return typeMap[row.type] || row.type
    },
  },
  {
    title: '状态',
    key: 'status',
    width: 100,
    render(row) {
      const statusTagType = {
        active: 'success',
        inactive: 'default',
        error: 'error',
        running: 'info',
      }
      const statusMap = {
        active: '活跃',
        inactive: '停用',
        error: '错误',
        running: '运行中',
      }
      return h(NTag, { type: statusTagType[row.status] || 'default' }, {
        default: () => statusMap[row.status] || row.status
      })
    },
  },
  {
    title: '最后活动时间',
    key: 'last_active',
    width: 180,
    render(row) {
      return formatDate(row.updated_at || row.created_at)
    },
  },
]

async function fetchDashboardData() {
  try {
    loading.value = true
    const [statsData, reportsData, agentsData] = await Promise.all([
      api.getDashboardStatistics(),
      api.getTestReportList({ page: 1, page_size: 5 }),
      api.getAgentList({ page: 1, page_size: 5, status: 'active' }),
    ])

    if (statsData.data) {
      statistics.value = statsData.data
    }

    if (reportsData.data?.items) {
      recentReports.value = reportsData.data.items
    }

    if (agentsData.data?.items) {
      agentStatus.value = agentsData.data.items
    }
  } catch (error) {
    console.error('获取Dashboard数据失败:', error)
    $message.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

function handleRefresh() {
  fetchDashboardData()
}

onMounted(() => {
  fetchDashboardData()
})
</script>

<template>
  <div class="dashboard-container">
    <NSpin :show="loading">
      <NSpace vertical :size="16">
        <!-- 页面标题和刷新按钮 -->
        <div class="flex justify-between items-center mb-4">
          <h2 class="text-2xl font-bold">数据概览</h2>
          <NButton type="primary" @click="handleRefresh">
            <template #icon>
              <TheIcon icon="mdi:refresh" :size="18" />
            </template>
            刷新数据
          </NButton>
        </div>

        <!-- 统计卡片 -->
        <NGrid :x-gap="16" :y-gap="16" :cols="4">
          <NGridItem v-for="stat in statsCards" :key="stat.key">
            <NCard :bordered="false" class="stat-card">
              <div class="flex items-center justify-between">
                <div>
                  <div class="text-gray-500 text-sm mb-2">{{ stat.label }}</div>
                  <NStatistic :value="statistics[stat.key] || 0">
                    <template #prefix>
                      <span class="text-base">{{ stat.prefix }}</span>
                    </template>
                    <template #suffix>
                      <span class="text-base">{{ stat.suffix }}</span>
                    </template>
                  </NStatistic>
                </div>
                <div
                  class="stat-icon"
                  :style="{ backgroundColor: `${stat.color}20`, color: stat.color }"
                >
                  <TheIcon :icon="stat.icon" :size="32" />
                </div>
              </div>
            </NCard>
          </NGridItem>
        </NGrid>

        <!-- 最近测试报告 -->
        <NCard title="最近测试报告" :bordered="false">
          <template #header-extra>
            <NButton text tag="a" href="/#/test/reports">
              查看全部
              <template #icon>
                <TheIcon icon="mdi:arrow-right" :size="16" />
              </template>
            </NButton>
          </template>
          <NDataTable
            :columns="reportColumns"
            :data="recentReports"
            :pagination="false"
            :bordered="false"
          />
        </NCard>

        <!-- 活跃代理 -->
        <NCard title="活跃代理" :bordered="false">
          <template #header-extra>
            <NButton text tag="a" href="/#/agent/list">
              查看全部
              <template #icon>
                <TheIcon icon="mdi:arrow-right" :size="16" />
              </template>
            </NButton>
          </template>
          <NDataTable
            :columns="agentColumns"
            :data="agentStatus"
            :pagination="false"
            :bordered="false"
          />
        </NCard>
      </NSpace>
    </NSpin>
  </div>
</template>

<style scoped>
.dashboard-container {
  padding: 20px;
  background-color: #f5f5f5;
  min-height: calc(100vh - 64px);
}

.stat-card {
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  width: 64px;
  height: 64px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.stat-card:hover .stat-icon {
  transform: scale(1.1);
}
</style>

