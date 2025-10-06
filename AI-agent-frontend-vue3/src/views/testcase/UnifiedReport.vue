<!-- Copyright (c) 2025 左岚. All rights reserved. -->
<template>
  <div class="unified-report-container">
    <!-- 页面标题 -->
    <el-page-header :content="pageTitle" class="page-header" />

    <!-- 搜索栏 -->
    <el-card class="search-card">
      <el-form :inline="true" :model="searchForm">
        <el-form-item label="报告名称">
          <el-input
            v-model="searchForm.keyword"
            placeholder="请输入报告名称"
            clearable
            style="width: 200px"
          />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="全部" clearable style="width: 120px">
            <el-option label="生成中" value="generating" />
            <el-option label="已完成" value="completed" />
            <el-option label="失败" value="failed" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch" :icon="Search">搜索</el-button>
          <el-button @click="handleReset" :icon="Refresh">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 报告列表 -->
    <el-card class="table-card">
      <el-table
        v-loading="loading"
        :data="reports"
        border
        stripe
        style="width: 100%"
      >
        <el-table-column prop="report_id" label="ID" width="80" />
        <el-table-column prop="name" label="报告名称" min-width="200" />
        <el-table-column label="类型" width="120">
          <template #default>
            <el-tag :type="getTypeColor(testType)">{{ testTypeMap[testType] }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ statusMap[row.status] || row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="统计" width="200">
          <template #default="{ row }">
            <span style="color: #67c23a">通过: {{ row.passed_cases || 0 }}</span> /
            <span style="color: #f56c6c">失败: {{ row.failed_cases || 0 }}</span> /
            <span style="color: #909399">总计: {{ row.total_cases || 0 }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="pass_rate" label="通过率" width="100">
          <template #default="{ row }">
            {{ (row.pass_rate * 100).toFixed(1) }}%
          </template>
        </el-table-column>
        <el-table-column prop="duration" label="执行时长" width="120">
          <template #default="{ row }">
            {{ row.duration ? row.duration.toFixed(2) + 's' : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="handleView(row)">查看</el-button>
            <el-button link type="success" size="small" @click="handleExport(row)">导出</el-button>
            <el-button link type="danger" size="small" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.page_size"
        :page-sizes="[10, 20, 50, 100]"
        :total="total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSearch"
        @current-change="handleSearch"
        style="margin-top: 20px; justify-content: flex-end"
      />
    </el-card>

    <!-- 报告详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="报告详情"
      width="900px"
      :close-on-click-modal="false"
    >
      <div v-if="currentReport" class="report-detail">
        <!-- 基本信息 -->
        <el-descriptions title="基本信息" :column="2" border>
          <el-descriptions-item label="报告名称">{{ currentReport.name }}</el-descriptions-item>
          <el-descriptions-item label="报告状态">
            <el-tag :type="getStatusType(currentReport.status)">
              {{ statusMap[currentReport.status] }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="开始时间">
            {{ currentReport.start_time || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="结束时间">
            {{ currentReport.end_time || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="执行时长">
            {{ currentReport.duration ? currentReport.duration.toFixed(2) + 's' : '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">
            {{ currentReport.created_at }}
          </el-descriptions-item>
        </el-descriptions>

        <!-- 统计信息 -->
        <el-descriptions title="统计信息" :column="3" border class="stat-desc">
          <el-descriptions-item label="总用例数">
            <el-statistic :value="currentReport.total_cases || 0" />
          </el-descriptions-item>
          <el-descriptions-item label="通过数">
            <el-statistic :value="currentReport.passed_cases || 0" value-style="color: #67c23a" />
          </el-descriptions-item>
          <el-descriptions-item label="失败数">
            <el-statistic :value="currentReport.failed_cases || 0" value-style="color: #f56c6c" />
          </el-descriptions-item>
          <el-descriptions-item label="跳过数">
            <el-statistic :value="currentReport.skipped_cases || 0" />
          </el-descriptions-item>
          <el-descriptions-item label="通过率">
            <el-statistic :value="(currentReport.pass_rate * 100).toFixed(1)" suffix="%" />
          </el-descriptions-item>
          <el-descriptions-item label="执行率">
            <el-statistic :value="(currentReport.execution_rate * 100).toFixed(1)" suffix="%" />
          </el-descriptions-item>
        </el-descriptions>

        <!-- 数据可视化图表 -->
        <div class="charts-section">
          <el-row :gutter="20">
            <el-col :span="12">
              <el-card shadow="hover">
                <template #header>
                  <div class="card-header">
                    <span>测试结果分布</span>
                  </div>
                </template>
                <div ref="pieChartRef" style="width: 100%; height: 300px"></div>
              </el-card>
            </el-col>
            <el-col :span="12">
              <el-card shadow="hover">
                <template #header>
                  <div class="card-header">
                    <span>通过率趋势</span>
                  </div>
                </template>
                <div ref="barChartRef" style="width: 100%; height: 300px"></div>
              </el-card>
            </el-col>
          </el-row>
        </div>

        <!-- 报告描述 -->
        <el-descriptions v-if="currentReport.description" title="报告描述" :column="1" border>
          <el-descriptions-item>
            {{ currentReport.description }}
          </el-descriptions-item>
        </el-descriptions>

        <!-- 报告摘要 -->
        <el-descriptions v-if="currentReport.summary" title="报告摘要" :column="1" border>
          <el-descriptions-item>
            <pre class="summary-content">{{ currentReport.summary }}</pre>
          </el-descriptions-item>
        </el-descriptions>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Refresh } from '@element-plus/icons-vue'
import request from '@/api/request'
import * as echarts from 'echarts'

// Props
const props = defineProps<{
  testType: 'api' | 'web' | 'app'
}>()

// 页面标题
const testTypeMap: Record<string, string> = {
  api: 'API',
  web: 'WEB',
  app: 'APP'
}

const pageTitle = computed(() => `${testTypeMap[props.testType]}测试报告`)

// 状态映射
const statusMap: Record<string, string> = {
  generating: '生成中',
  completed: '已完成',
  failed: '失败',
  archived: '已归档'
}

// 状态
const loading = ref(false)
const reports = ref<any[]>([])
const total = ref(0)
const detailDialogVisible = ref(false)
const currentReport = ref<any>(null)

// 图表refs
const pieChartRef = ref<HTMLElement>()
const barChartRef = ref<HTMLElement>()
let pieChart: echarts.ECharts | null = null
let barChart: echarts.ECharts | null = null

// 搜索表单
const searchForm = reactive({
  keyword: '',
  status: ''
})

// 分页
const pagination = reactive({
  page: 1,
  page_size: 20
})

// 获取类型颜色
const getTypeColor = (type: string) => {
  const colors: Record<string, string> = {
    api: 'primary',
    web: 'success',
    app: 'warning'
  }
  return colors[type] || 'info'
}

// 获取状态类型
const getStatusType = (status: string) => {
  const types: Record<string, any> = {
    generating: 'warning',
    completed: 'success',
    failed: 'danger',
    archived: 'info'
  }
  return types[status] || ''
}

// 加载报告列表
const loadReports = async () => {
  loading.value = true
  try {
    const response = await request({
      url: '/api/v1/reports/',
      method: 'get',
      params: {
        page: pagination.page,
        page_size: pagination.page_size,
        ...searchForm
      }
    })

    if (response.data) {
      reports.value = response.data.items || []
      total.value = response.data.total || 0
    }
  } catch (error: any) {
    ElMessage.error(error.message || '加载失败')
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  pagination.page = 1
  loadReports()
}

// 重置
const handleReset = () => {
  searchForm.keyword = ''
  searchForm.status = ''
  handleSearch()
}

// 查看详情
const handleView = async (row: any) => {
  try {
    const response = await request({
      url: `/api/v1/reports/${row.report_id}`,
      method: 'get'
    })

    if (response.data) {
      currentReport.value = response.data
      detailDialogVisible.value = true
      
      // 等待对话框渲染完成后初始化图表
      await nextTick()
      initCharts()
    }
  } catch (error: any) {
    ElMessage.error(error.message || '加载报告详情失败')
  }
}

// 初始化图表
const initCharts = () => {
  if (!currentReport.value) return
  
  // 初始化饼图
  if (pieChartRef.value) {
    pieChart = echarts.init(pieChartRef.value)
    const pieOption = {
      title: {
        text: '测试结果',
        left: 'center',
        top: 10,
        textStyle: {
          fontSize: 14
        }
      },
      tooltip: {
        trigger: 'item',
        formatter: '{b}: {c} ({d}%)'
      },
      legend: {
        bottom: 10,
        left: 'center'
      },
      series: [
        {
          name: '测试结果',
          type: 'pie',
          radius: ['40%', '70%'],
          avoidLabelOverlap: false,
          itemStyle: {
            borderRadius: 10,
            borderColor: '#fff',
            borderWidth: 2
          },
          label: {
            show: true,
            formatter: '{b}\n{c}个'
          },
          emphasis: {
            label: {
              show: true,
              fontSize: 16,
              fontWeight: 'bold'
            }
          },
          data: [
            { 
              value: currentReport.value.passed_cases || 0, 
              name: '通过',
              itemStyle: { color: '#67c23a' }
            },
            { 
              value: currentReport.value.failed_cases || 0, 
              name: '失败',
              itemStyle: { color: '#f56c6c' }
            },
            { 
              value: currentReport.value.skipped_cases || 0, 
              name: '跳过',
              itemStyle: { color: '#909399' }
            }
          ]
        }
      ]
    }
    pieChart.setOption(pieOption)
  }
  
  // 初始化柱状图
  if (barChartRef.value) {
    barChart = echarts.init(barChartRef.value)
    const barOption = {
      title: {
        text: '用例统计',
        left: 'center',
        top: 10,
        textStyle: {
          fontSize: 14
        }
      },
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'shadow'
        }
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        data: ['通过', '失败', '跳过', '总计'],
        axisLabel: {
          interval: 0,
          rotate: 0
        }
      },
      yAxis: {
        type: 'value',
        minInterval: 1
      },
      series: [
        {
          name: '数量',
          type: 'bar',
          data: [
            {
              value: currentReport.value.passed_cases || 0,
              itemStyle: { color: '#67c23a' }
            },
            {
              value: currentReport.value.failed_cases || 0,
              itemStyle: { color: '#f56c6c' }
            },
            {
              value: currentReport.value.skipped_cases || 0,
              itemStyle: { color: '#909399' }
            },
            {
              value: currentReport.value.total_cases || 0,
              itemStyle: { color: '#409eff' }
            }
          ],
          label: {
            show: true,
            position: 'top',
            formatter: '{c}个'
          },
          barWidth: '60%'
        }
      ]
    }
    barChart.setOption(barOption)
  }
  
  // 监听窗口大小变化
  window.addEventListener('resize', handleResize)
}

// 处理窗口大小变化
const handleResize = () => {
  pieChart?.resize()
  barChart?.resize()
}

// 销毁图表
const destroyCharts = () => {
  pieChart?.dispose()
  barChart?.dispose()
  pieChart = null
  barChart = null
  window.removeEventListener('resize', handleResize)
}

// 导出报告
const handleExport = async (row: any) => {
  // 显示导出格式选择
  ElMessageBox.confirm(
    '请选择导出格式',
    '导出报告',
    {
      distinguishCancelAndClose: true,
      confirmButtonText: 'PDF',
      cancelButtonText: 'Excel',
      type: 'info'
    }
  )
    .then(async () => {
      // 导出PDF
      try {
        const { exportReportFile } = await import('@/api/report')
        await exportReportFile(row.report_id, 'pdf')
        ElMessage.success('PDF导出成功')
      } catch (error: any) {
        console.error('导出PDF失败:', error)
        ElMessage.error(error.message || 'PDF导出失败')
      }
    })
    .catch(async (action) => {
      if (action === 'cancel') {
        // 导出Excel
        try {
          const { exportReportFile } = await import('@/api/report')
          await exportReportFile(row.report_id, 'excel')
          ElMessage.success('Excel导出成功')
        } catch (error: any) {
          console.error('导出Excel失败:', error)
          ElMessage.error(error.message || 'Excel导出失败')
        }
      }
    })
}

// 删除报告
const handleDelete = async (row: any) => {
  try {
    await ElMessageBox.confirm('确定要删除这个报告吗？', '提示', {
      type: 'warning'
    })

    await request({
      url: `/api/v1/reports/${row.report_id}`,
      method: 'delete'
    })

    ElMessage.success('删除成功')
    loadReports()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '删除失败')
    }
  }
}

// 初始化
onMounted(() => {
  loadReports()
})
</script>

<style scoped lang="scss">
.unified-report-container {
  padding: 20px;

  .page-header {
    margin-bottom: 20px;
  }

  .search-card {
    margin-bottom: 20px;
  }

  .table-card {
    :deep(.el-pagination) {
      display: flex;
    }
  }

  .report-detail {
    .el-descriptions {
      margin-bottom: 20px;
    }

    .stat-desc {
      :deep(.el-descriptions__cell) {
        text-align: center;
      }
    }

    .charts-section {
      margin: 20px 0;

      .card-header {
        font-weight: 600;
        font-size: 14px;
      }
    }

    .summary-content {
      white-space: pre-wrap;
      word-wrap: break-word;
      margin: 0;
      font-family: monospace;
      font-size: 13px;
      line-height: 1.5;
    }
  }
}
</style>

