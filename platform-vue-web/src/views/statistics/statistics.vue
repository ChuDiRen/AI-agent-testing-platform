<template>
    <div class="statistics-container">
        <!-- 头部欢迎区域 -->
        <div class="welcome-section">
            <div class="welcome-content">
                <h1>
                    <el-icon><DataAnalysis /></el-icon>
                    系统总览
                </h1>
                <p>欢迎使用 AI Agent 接口测试平台</p>
                <p class="time">{{ currentTime }}</p>
            </div>
            <div class="welcome-image">
                <div class="wave wave1"></div>
                <div class="wave wave2"></div>
            </div>
        </div>

        <!-- 统计卡片 -->
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-icon projects">
                    <el-icon><FolderOpened /></el-icon>
                </div>
                <div class="stat-content">
                    <h3>测试项目</h3>
                    <p class="stat-number">{{ stats.projectCount }}</p>
                    <span class="stat-label">个项目</span>
                </div>
            </div>

            <div class="stat-card">
                <div class="stat-icon apis">
                    <el-icon><Connection /></el-icon>
                </div>
                <div class="stat-content">
                    <h3>接口管理</h3>
                    <p class="stat-number">{{ stats.apiCount }}</p>
                    <span class="stat-label">个接口</span>
                </div>
            </div>

            <div class="stat-card">
                <div class="stat-icon tests">
                    <el-icon><CollectionTag /></el-icon>
                </div>
                <div class="stat-content">
                    <h3>测试用例</h3>
                    <p class="stat-number">{{ stats.testcaseCount }}</p>
                    <span class="stat-label">个用例</span>
                </div>
            </div>

            <div class="stat-card">
                <div class="stat-icon ai">
                    <el-icon><ChatDotRound /></el-icon>
                </div>
                <div class="stat-content">
                    <h3>AI模型</h3>
                    <p class="stat-number">{{ stats.aiModelCount }}</p>
                    <span class="stat-label">个模型</span>
                </div>
            </div>
        </div>

        <!-- 功能介绍 -->
        <div class="features-section">
            <h2>核心功能</h2>
            <el-row :gutter="20">
                <el-col :xs="24" :sm="12" :md="8">
                    <div class="feature-card">
                        <div class="feature-number">1</div>
                        <h3>智能测试生成</h3>
                        <p>基于AI的智能测试用例生成，支持API、Web、App三种类型测试</p>
                    </div>
                </el-col>
                <el-col :xs="24" :sm="12" :md="8">
                    <div class="feature-card">
                        <div class="feature-number">2</div>
                        <h3>完整接口管理</h3>
                        <p>支持接口定义、分组管理、YAML格式配置和版本控制</p>
                    </div>
                </el-col>
                <el-col :xs="24" :sm="12" :md="8">
                    <div class="feature-card">
                        <div class="feature-number">3</div>
                        <h3>强大测试引擎</h3>
                        <p>基于Pytest的高性能测试执行引擎，支持关键字驱动和数据驱动测试</p>
                    </div>
                </el-col>
            </el-row>
        </div>

        <!-- 平台统计 -->
        <div class="platform-stats">
            <el-row :gutter="20">
                <el-col :xs="24" :sm="12" :md="6">
                    <div class="mini-stat">
                        <div class="mini-number">{{ stats.successRate }}%</div>
                        <div class="mini-label">测试成功率</div>
                    </div>
                </el-col>
                <el-col :xs="24" :sm="12" :md="6">
                    <div class="mini-stat">
                        <div class="mini-number">{{ stats.totalTests }}</div>
                        <div class="mini-label">累计执行测试</div>
                    </div>
                </el-col>
                <el-col :xs="24" :sm="12" :md="6">
                    <div class="mini-stat">
                        <div class="mini-number">{{ stats.avgTime }}ms</div>
                        <div class="mini-label">平均执行时间</div>
                    </div>
                </el-col>
                <el-col :xs="24" :sm="12" :md="6">
                    <div class="mini-stat">
                        <div class="mini-number">{{ stats.users }}</div>
                        <div class="mini-label">活跃用户</div>
                    </div>
                </el-col>
            </el-row>
        </div>

        <!-- 执行趋势与耗时趋势 -->
        <div class="charts-section">
            <el-row :gutter="20">
                <!-- 执行趋势图 -->
                <el-col :xs="24" :md="12">
                    <div class="chart-card">
                        <div class="chart-header">
                            <h3>
                                <el-icon><TrendCharts /></el-icon>
                                执行趋势（最近5次）
                            </h3>
                            <el-button size="small" @click="loadExecutionTrend">
                                <el-icon><Refresh /></el-icon>
                            </el-button>
                        </div>
                        <div class="chart-content" v-loading="trendLoading">
                            <div v-if="executionTrend.length === 0" class="no-data">
                                <el-empty description="暂无执行记录" :image-size="80" />
                            </div>
                            <div v-else class="trend-list">
                                <div v-for="(item, index) in executionTrend" :key="index" class="trend-item">
                                    <div class="trend-info">
                                        <span class="trend-time">{{ item.create_time }}</span>
                                        <span class="trend-name" :title="item.test_name">{{ item.test_name }}</span>
                                    </div>
                                    <div class="trend-status">
                                        <el-tag :type="getStatusType(item.status)" size="small">
                                            {{ getStatusText(item.status) }}
                                        </el-tag>
                                        <span class="trend-time-cost" v-if="item.response_time">
                                            {{ item.response_time }}ms
                                        </span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </el-col>

                <!-- 耗时趋势图 -->
                <el-col :xs="24" :md="12">
                    <div class="chart-card">
                        <div class="chart-header">
                            <h3>
                                <el-icon><Timer /></el-icon>
                                耗时趋势（最近10次）
                            </h3>
                            <el-button size="small" @click="loadTimeTrend">
                                <el-icon><Refresh /></el-icon>
                            </el-button>
                        </div>
                        <div class="chart-content" v-loading="timeLoading">
                            <div v-if="timeTrend.length === 0" class="no-data">
                                <el-empty description="暂无耗时数据" :image-size="80" />
                            </div>
                            <div v-else>
                                <div class="time-stats">
                                    <div class="time-stat-item">
                                        <span class="label">平均耗时</span>
                                        <span class="value">{{ timeStats.avg_time }}ms</span>
                                    </div>
                                    <div class="time-stat-item">
                                        <span class="label">最大耗时</span>
                                        <span class="value warning">{{ timeStats.max_time }}ms</span>
                                    </div>
                                    <div class="time-stat-item">
                                        <span class="label">最小耗时</span>
                                        <span class="value success">{{ timeStats.min_time }}ms</span>
                                    </div>
                                </div>
                                <div class="time-bars">
                                    <div v-for="(item, index) in timeTrend" :key="index" class="time-bar-item">
                                        <span class="time-label">{{ item.create_time }}</span>
                                        <el-progress 
                                            :percentage="getTimePercentage(item.response_time)" 
                                            :color="getTimeColor(item.response_time)"
                                            :stroke-width="12"
                                            :show-text="false"
                                        />
                                        <span class="time-value">{{ item.response_time }}ms</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </el-col>
            </el-row>
        </div>

        <!-- 失败TOP5与每日统计 -->
        <div class="charts-section">
            <el-row :gutter="20">
                <!-- 失败TOP5 -->
                <el-col :xs="24" :md="12">
                    <div class="chart-card">
                        <div class="chart-header">
                            <h3>
                                <el-icon><WarningFilled /></el-icon>
                                失败TOP5（近30天）
                            </h3>
                            <el-button size="small" @click="loadFailedTop5">
                                <el-icon><Refresh /></el-icon>
                            </el-button>
                        </div>
                        <div class="chart-content" v-loading="failedLoading">
                            <div v-if="failedTop5.length === 0" class="no-data">
                                <el-empty description="暂无失败记录，太棒了！" :image-size="80" />
                            </div>
                            <div v-else class="failed-list">
                                <div v-for="(item, index) in failedTop5" :key="index" class="failed-item">
                                    <div class="failed-rank" :class="'rank-' + (index + 1)">
                                        {{ index + 1 }}
                                    </div>
                                    <div class="failed-info">
                                        <div class="failed-name" :title="item.test_name">{{ item.test_name }}</div>
                                        <div class="failed-error" :title="item.last_error">{{ item.last_error || '无错误信息' }}</div>
                                    </div>
                                    <div class="failed-count">
                                        <el-tag type="danger" size="small">{{ item.count }}次</el-tag>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </el-col>

                <!-- 每日统计 -->
                <el-col :xs="24" :md="12">
                    <div class="chart-card">
                        <div class="chart-header">
                            <h3>
                                <el-icon><Calendar /></el-icon>
                                每日执行统计（近7天）
                            </h3>
                            <el-button size="small" @click="loadDailyStats">
                                <el-icon><Refresh /></el-icon>
                            </el-button>
                        </div>
                        <div class="chart-content" v-loading="dailyLoading">
                            <div v-if="dailyStats.length === 0" class="no-data">
                                <el-empty description="暂无每日统计数据" :image-size="80" />
                            </div>
                            <div v-else class="daily-chart">
                                <div v-for="(item, index) in dailyStats" :key="index" class="daily-bar">
                                    <div class="daily-date">{{ formatDate(item.date) }}</div>
                                    <div class="daily-bar-container">
                                        <div class="bar-stack">
                                            <div 
                                                class="bar-passed" 
                                                :style="{ width: getDailyBarWidth(item.passed, item.total) }"
                                                :title="'通过: ' + item.passed"
                                            ></div>
                                            <div 
                                                class="bar-failed" 
                                                :style="{ width: getDailyBarWidth(item.failed, item.total) }"
                                                :title="'失败: ' + item.failed"
                                            ></div>
                                        </div>
                                    </div>
                                    <div class="daily-count">{{ item.total }}</div>
                                </div>
                                <div class="daily-legend">
                                    <span class="legend-item"><span class="dot passed"></span>通过</span>
                                    <span class="legend-item"><span class="dot failed"></span>失败</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </el-col>
            </el-row>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { 
    DataAnalysis, 
    TrendCharts, Timer, WarningFilled, Calendar, Refresh
} from '@element-plus/icons-vue'
import { getOverview, getExecutionTrend, getTimeTrend, getFailedTop5, getDailyStats } from './statistics.js'

const currentTime = ref('')
const loading = ref(false)

// 统计数据
const stats = ref({
    projectCount: 0,
    apiCount: 0,
    testcaseCount: 0,
    aiModelCount: 0,
    successRate: 0,
    totalTests: 0,
    avgTime: 0,
    users: 0
})

// 图表数据
const executionTrend = ref([])
const timeTrend = ref([])
const timeStats = ref({ avg_time: 0, max_time: 0, min_time: 0 })
const failedTop5 = ref([])
const dailyStats = ref([])

// 加载状态
const trendLoading = ref(false)
const timeLoading = ref(false)
const failedLoading = ref(false)
const dailyLoading = ref(false)

// 加载统计数据
const loadStats = async () => {
    loading.value = true
    try {
        const res = await getOverview()
        if (res.data.code === 200 && res.data.data) {
            const data = res.data.data
            stats.value.projectCount = data.projectCount || 0
            stats.value.apiCount = data.apiCount || 0
            stats.value.testcaseCount = data.testcaseCount || 0
            stats.value.totalTests = data.totalTests || 0
            stats.value.successRate = data.successRate || 0
            stats.value.avgTime = data.avgTime || 0
            stats.value.aiModelCount = data.planCount || 0
        }
    } catch (error) {
        console.error('加载统计数据失败:', error)
    } finally {
        loading.value = false
    }
}

// 加载执行趋势
const loadExecutionTrend = async () => {
    trendLoading.value = true
    try {
        const res = await getExecutionTrend({ limit: 5 })
        if (res.data.code === 200 && res.data.data) {
            executionTrend.value = res.data.data.trend || []
        }
    } catch (error) {
        console.error('加载执行趋势失败:', error)
    } finally {
        trendLoading.value = false
    }
}

// 加载耗时趋势
const loadTimeTrend = async () => {
    timeLoading.value = true
    try {
        const res = await getTimeTrend({ limit: 10 })
        if (res.data.code === 200 && res.data.data) {
            timeTrend.value = res.data.data.trend || []
            timeStats.value = {
                avg_time: res.data.data.avg_time || 0,
                max_time: res.data.data.max_time || 0,
                min_time: res.data.data.min_time || 0
            }
        }
    } catch (error) {
        console.error('加载耗时趋势失败:', error)
    } finally {
        timeLoading.value = false
    }
}

// 加载失败TOP5
const loadFailedTop5 = async () => {
    failedLoading.value = true
    try {
        const res = await getFailedTop5({ days: 30 })
        if (res.data.code === 200 && res.data.data) {
            failedTop5.value = res.data.data.top5 || []
        }
    } catch (error) {
        console.error('加载失败TOP5失败:', error)
    } finally {
        failedLoading.value = false
    }
}

// 加载每日统计
const loadDailyStats = async () => {
    dailyLoading.value = true
    try {
        const res = await getDailyStats(7)
        if (res.data.code === 200 && res.data.data) {
            dailyStats.value = res.data.data.daily_stats || []
        }
    } catch (error) {
        console.error('加载每日统计失败:', error)
    } finally {
        dailyLoading.value = false
    }
}

// 辅助函数
const getStatusType = (status) => {
    const map = {
        'passed': 'success',
        'success': 'success',
        'completed': 'success',
        'failed': 'danger',
        'error': 'danger',
        'running': 'warning',
        'pending': 'info'
    }
    return map[status] || 'info'
}

const getStatusText = (status) => {
    const map = {
        'passed': '通过',
        'success': '成功',
        'completed': '完成',
        'failed': '失败',
        'error': '错误',
        'running': '执行中',
        'pending': '等待中'
    }
    return map[status] || status
}

const getTimePercentage = (time) => {
    if (!time || timeStats.value.max_time === 0) return 0
    return Math.min(100, (time / timeStats.value.max_time) * 100)
}

const getTimeColor = (time) => {
    if (!time) return '#909399'
    const avg = timeStats.value.avg_time
    if (time <= avg * 0.8) return '#67C23A'
    if (time <= avg * 1.2) return '#409EFF'
    return '#E6A23C'
}

const formatDate = (dateStr) => {
    if (!dateStr) return ''
    const parts = dateStr.split('-')
    if (parts.length === 3) {
        return `${parts[1]}/${parts[2]}`
    }
    return dateStr
}

const getDailyBarWidth = (value, total) => {
    if (!total || total === 0) return '0%'
    return `${(value / total) * 100}%`
}

// 更新时间
const updateTime = () => {
    const now = new Date()
    const options = {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    }
    currentTime.value = now.toLocaleString('zh-CN', options)
}

onMounted(() => {
    updateTime()
    setInterval(updateTime, 1000)
    loadStats()
    loadExecutionTrend()
    loadTimeTrend()
    loadFailedTop5()
    loadDailyStats()
})
</script>

<style scoped>
.statistics-container {
    padding: 24px;
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    min-height: calc(100vh - 64px);
}

/* 欢迎区域 */
.welcome-section {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 12px;
    padding: 40px;
    margin-bottom: 32px;
    color: white;
    position: relative;
    overflow: hidden;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
}

.welcome-content h1 {
    font-size: 36px;
    margin: 0 0 16px 0;
    display: flex;
    align-items: center;
    gap: 12px;
}

.welcome-content p {
    font-size: 16px;
    margin: 8px 0;
    opacity: 0.9;
}

.welcome-content .time {
    font-size: 14px;
    opacity: 0.8;
    margin-top: 16px;
}

.welcome-image {
    position: relative;
    width: 200px;
    height: 120px;
    opacity: 0.2;
}

.wave {
    position: absolute;
    bottom: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: url('data:image/svg+xml,<svg viewBox="0 0 1200 120" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg"><path d="M0,50 Q300,0 600,50 T1200,50 L1200,120 L0,120 Z" fill="white"/></svg>') repeat-x;
    background-size: 200% 100%;
    animation: wave 15s linear infinite;
}

.wave1 {
    animation-delay: 0s;
}

.wave2 {
    animation-delay: 5s;
    bottom: 10px;
    opacity: 0.5;
}

@keyframes wave {
    0% { background-position: 0 0; }
    100% { background-position: 200% 0; }
}

/* 统计卡片网格 */
.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 20px;
    margin-bottom: 32px;
}

.stat-card {
    display: flex;
    align-items: center;
    gap: 20px;
    background: white;
    border-radius: 12px;
    padding: 24px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
    transition: all 0.3s ease;
    cursor: pointer;
}

.stat-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
}

.stat-icon {
    width: 80px;
    height: 80px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 36px;
    color: white;
}

.stat-icon.projects {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.stat-icon.apis {
    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.stat-icon.tests {
    background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.stat-icon.ai {
    background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
}

.stat-content h3 {
    font-size: 14px;
    color: #666;
    margin: 0 0 8px 0;
    font-weight: 600;
}

.stat-number {
    font-size: 32px;
    font-weight: bold;
    color: #333;
    margin: 0;
}

.stat-label {
    font-size: 12px;
    color: #999;
}

/* 功能介绍 */
.features-section {
    background: white;
    border-radius: 12px;
    padding: 32px;
    margin-bottom: 32px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.features-section h2 {
    font-size: 24px;
    color: #333;
    margin: 0 0 20px 0;
    display: flex;
    align-items: center;
    gap: 12px;
}

.features-section h2::before {
    content: '';
    width: 4px;
    height: 24px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 2px;
}

.feature-card {
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    border-radius: 12px;
    padding: 24px;
    text-align: center;
    transition: all 0.3s ease;
}

.feature-card:hover {
    transform: translateY(-4px);
}

.feature-number {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 48px;
    height: 48px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border-radius: 50%;
    font-size: 24px;
    font-weight: bold;
    margin-bottom: 12px;
}

.feature-card h3 {
    font-size: 18px;
    color: #333;
    margin: 12px 0 8px 0;
}

.feature-card p {
    font-size: 14px;
    color: #666;
    line-height: 1.6;
}

/* 平台统计 */
.platform-stats {
    background: white;
    border-radius: 12px;
    padding: 32px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.mini-stat {
    text-align: center;
    padding: 20px;
    border-radius: 12px;
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    transition: all 0.3s ease;
}

.mini-stat:hover {
    transform: translateY(-4px);
}

.mini-number {
    font-size: 32px;
    font-weight: bold;
    color: #667eea;
    margin-bottom: 8px;
}

.mini-label {
    font-size: 14px;
    color: #666;
}

/* 图表区域 */
.charts-section {
    margin-bottom: 32px;
}

.chart-card {
    background: white;
    border-radius: 12px;
    padding: 24px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
    height: 100%;
    min-height: 350px;
}

.chart-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    padding-bottom: 12px;
    border-bottom: 1px solid #eee;
}

.chart-header h3 {
    font-size: 16px;
    color: #333;
    margin: 0;
    display: flex;
    align-items: center;
    gap: 8px;
}

.chart-content {
    min-height: 250px;
}

.no-data {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 200px;
}

/* 执行趋势 */
.trend-list {
    display: flex;
    flex-direction: column;
    gap: 12px;
}

.trend-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 16px;
    background: #f5f7fa;
    border-radius: 8px;
    transition: all 0.3s ease;
}

.trend-item:hover {
    background: #e8f4ff;
}

.trend-info {
    display: flex;
    flex-direction: column;
    gap: 4px;
}

.trend-time {
    font-size: 12px;
    color: #999;
}

.trend-name {
    font-size: 14px;
    color: #333;
    max-width: 200px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.trend-status {
    display: flex;
    align-items: center;
    gap: 12px;
}

.trend-time-cost {
    font-size: 12px;
    color: #666;
}

/* 耗时趋势 */
.time-stats {
    display: flex;
    justify-content: space-around;
    margin-bottom: 20px;
    padding: 16px;
    background: #f5f7fa;
    border-radius: 8px;
}

.time-stat-item {
    text-align: center;
}

.time-stat-item .label {
    display: block;
    font-size: 12px;
    color: #999;
    margin-bottom: 4px;
}

.time-stat-item .value {
    font-size: 18px;
    font-weight: bold;
    color: #409EFF;
}

.time-stat-item .value.warning {
    color: #E6A23C;
}

.time-stat-item .value.success {
    color: #67C23A;
}

.time-bars {
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.time-bar-item {
    display: flex;
    align-items: center;
    gap: 12px;
}

.time-label {
    width: 80px;
    font-size: 12px;
    color: #666;
    text-align: right;
}

.time-bar-item .el-progress {
    flex: 1;
}

.time-value {
    width: 60px;
    font-size: 12px;
    color: #333;
    text-align: right;
}

/* 失败TOP5 */
.failed-list {
    display: flex;
    flex-direction: column;
    gap: 12px;
}

.failed-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px 16px;
    background: #fff5f5;
    border-radius: 8px;
    border-left: 3px solid #F56C6C;
}

.failed-rank {
    width: 28px;
    height: 28px;
    border-radius: 50%;
    background: #F56C6C;
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 14px;
    font-weight: bold;
}

.failed-rank.rank-1 {
    background: #E6A23C;
}

.failed-rank.rank-2 {
    background: #909399;
}

.failed-rank.rank-3 {
    background: #B87333;
}

.failed-info {
    flex: 1;
    min-width: 0;
}

.failed-name {
    font-size: 14px;
    color: #333;
    font-weight: 500;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.failed-error {
    font-size: 12px;
    color: #999;
    margin-top: 4px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.failed-count {
    flex-shrink: 0;
}

/* 每日统计 */
.daily-chart {
    padding: 10px 0;
}

.daily-bar {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 12px;
}

.daily-date {
    width: 50px;
    font-size: 12px;
    color: #666;
    text-align: right;
}

.daily-bar-container {
    flex: 1;
    height: 24px;
    background: #f0f0f0;
    border-radius: 4px;
    overflow: hidden;
}

.bar-stack {
    display: flex;
    height: 100%;
}

.bar-passed {
    background: linear-gradient(135deg, #67C23A 0%, #85ce61 100%);
    height: 100%;
    transition: width 0.3s ease;
}

.bar-failed {
    background: linear-gradient(135deg, #F56C6C 0%, #f78989 100%);
    height: 100%;
    transition: width 0.3s ease;
}

.daily-count {
    width: 40px;
    font-size: 14px;
    color: #333;
    font-weight: 500;
    text-align: right;
}

.daily-legend {
    display: flex;
    justify-content: center;
    gap: 24px;
    margin-top: 16px;
    padding-top: 12px;
    border-top: 1px solid #eee;
}

.legend-item {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 12px;
    color: #666;
}

.legend-item .dot {
    width: 12px;
    height: 12px;
    border-radius: 2px;
}

.legend-item .dot.passed {
    background: #67C23A;
}

.legend-item .dot.failed {
    background: #F56C6C;
}

/* 响应式设计 */
@media (max-width: 768px) {
    .statistics-container {
        padding: 16px;
    }

    .welcome-section {
        flex-direction: column;
        padding: 30px 20px;
    }

    .welcome-content h1 {
        font-size: 28px;
    }

    .welcome-image {
        display: none;
    }

    .stats-grid {
        grid-template-columns: 1fr;
    }

    .stat-card {
        padding: 16px;
    }

    .features-section {
        padding: 20px;
    }

    .chart-card {
        margin-bottom: 20px;
    }

    .time-stats {
        flex-direction: column;
        gap: 12px;
    }
}
</style>
