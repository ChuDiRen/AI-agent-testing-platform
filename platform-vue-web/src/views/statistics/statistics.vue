<template>
    <div class="statistics-container">
        <!-- 头部欢迎区域 -->
        <div class="welcome-section">
            <div class="welcome-content">
                <h1>
                    <el-icon><DataAnalysis /></el-icon>
                    大熊AI代码生成器
                </h1>
                <p>智能化代码生成与系统管理平台</p>
                <p class="time">{{ currentTime }}</p>
            </div>
            <div class="welcome-image">
                <div class="wave wave1"></div>
                <div class="wave wave2"></div>
            </div>
        </div>

        <!-- 核心功能模块 -->
        <div class="modules-section">
            <h2>
                <el-icon><Grid /></el-icon>
                核心功能模块
            </h2>
            <el-row :gutter="20">
                <el-col :xs="24" :sm="12" :md="8" :lg="6">
                    <div class="module-card system" @click="navigateTo('/system')">
                        <div class="module-icon">
                            <el-icon><Setting /></el-icon>
                        </div>
                        <div class="module-content">
                            <h3>系统管理</h3>
                            <p>用户、角色、菜单、部门管理</p>
                            <div class="module-stats">
                                <span>{{ stats.userCount }} 用户</span>
                                <span>{{ stats.roleCount }} 角色</span>
                            </div>
                        </div>
                    </div>
                </el-col>
                
                <el-col :xs="24" :sm="12" :md="8" :lg="6">
                    <div class="module-card generator" @click="navigateTo('/generator')">
                        <div class="module-icon">
                            <el-icon><Document /></el-icon>
                        </div>
                        <div class="module-content">
                            <h3>代码生成</h3>
                            <p>智能代码生成与配置管理</p>
                            <div class="module-stats">
                                <span>{{ stats.tableCount }} 表配置</span>
                                <span>{{ stats.genCount }} 生成记录</span>
                            </div>
                        </div>
                    </div>
                </el-col>


            </el-row>
        </div>

        <!-- 平台统计概览 -->
        <div class="overview-section">
            <el-row :gutter="20">
                <el-col :xs="24" :md="16">
                    <div class="stats-panel">
                        <h3>
                            <el-icon><TrendCharts /></el-icon>
                            平台数据概览
                        </h3>
                        <div class="stats-grid">
                            <div class="stat-item">
                                <div class="stat-number">{{ stats.totalProjects }}</div>
                                <div class="stat-label">测试项目</div>
                            </div>
                            <div class="stat-item">
                                <div class="stat-number">{{ stats.totalTests }}</div>
                                <div class="stat-label">执行测试</div>
                            </div>
                            <div class="stat-item">
                                <div class="stat-number">{{ stats.successRate }}%</div>
                                <div class="stat-label">成功率</div>
                            </div>
                            <div class="stat-item">
                                <div class="stat-number">{{ stats.avgTime }}ms</div>
                                <div class="stat-label">平均耗时</div>
                            </div>
                        </div>
                    </div>
                </el-col>
                
                <el-col :xs="24" :md="8">
                    <div class="quick-actions">
                        <h3>
                            <el-icon><Lightning /></el-icon>
                            快速操作
                        </h3>
                        <div class="action-list">
                            <el-button type="primary" @click="navigateTo('/generator/table')" class="action-btn">
                                <el-icon><Plus /></el-icon>
                                新建代码生成
                            </el-button>
                            <el-button type="success" @click="navigateTo('/generator/table')" class="action-btn">
                                <el-icon><FolderAdd /></el-icon>
                                新建表配置
                            </el-button>
                            <el-button type="warning" @click="navigateTo('/system/role')" class="action-btn">
                                <el-icon><UserFilled /></el-icon>
                                角色管理
                            </el-button>
                        </div>
                    </div>
                </el-col>
            </el-row>
        </div>

        <!-- 最近活动 -->
        <div class="activity-section">
            <el-row :gutter="20">
                <el-col :xs="24" :md="12">
                    <div class="activity-panel">
                        <div class="panel-header">
                            <h3>
                                <el-icon><Clock /></el-icon>
                                最近系统操作
                            </h3>
                            <el-button size="small" @click="loadRecentTests">
                                <el-icon><Refresh /></el-icon>
                            </el-button>
                        </div>
                        <div class="activity-content" v-loading="testsLoading">
                            <div v-if="recentTests.length === 0" class="no-data">
                                <el-empty description="暂无操作记录" :image-size="60" />
                            </div>
                            <div v-else class="activity-list">
                                <div v-for="(test, index) in recentTests" :key="index" class="activity-item">
                                    <div class="activity-icon" :class="getTestStatusClass(test.status)">
                                        <el-icon><CollectionTag /></el-icon>
                                    </div>
                                    <div class="activity-info">
                                        <div class="activity-title">{{ test.name }}</div>
                                        <div class="activity-time">{{ test.create_time }}</div>
                                    </div>
                                    <div class="activity-status">
                                        <el-tag :type="getStatusType(test.status)" size="small">
                                            {{ getStatusText(test.status) }}
                                        </el-tag>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </el-col>

                <el-col :xs="24" :md="12">
                    <div class="activity-panel">
                        <div class="panel-header">
                            <h3>
                                <el-icon><Document /></el-icon>
                                代码生成记录
                            </h3>
                            <el-button size="small" @click="loadRecentGens">
                                <el-icon><Refresh /></el-icon>
                            </el-button>
                        </div>
                        <div class="activity-content" v-loading="gensLoading">
                            <div v-if="recentGens.length === 0" class="no-data">
                                <el-empty description="暂无生成记录" :image-size="60" />
                            </div>
                            <div v-else class="activity-list">
                                <div v-for="(gen, index) in recentGens" :key="index" class="activity-item">
                                    <div class="activity-icon generator">
                                        <el-icon><EditPen /></el-icon>
                                    </div>
                                    <div class="activity-info">
                                        <div class="activity-title">{{ gen.table_name }}</div>
                                        <div class="activity-time">{{ gen.create_time }}</div>
                                    </div>
                                    <div class="activity-status">
                                        <el-tag type="success" size="small">已生成</el-tag>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </el-col>
            </el-row>
        </div>

        <!-- 系统信息 -->
        <div class="system-info">
            <el-row :gutter="20">
                <el-col :xs="24" :md="8">
                    <div class="info-card">
                        <h4>
                            <el-icon><Monitor /></el-icon>
                            系统信息
                        </h4>
                        <div class="info-list">
                            <div class="info-item">
                                <span class="label">平台版本</span>
                                <span class="value">v2.0.0</span>
                            </div>
                            <div class="info-item">
                                <span class="label">在线用户</span>
                                <span class="value">{{ stats.onlineUsers }}</span>
                            </div>
                            <div class="info-item">
                                <span class="label">运行时间</span>
                                <span class="value">{{ systemUptime }}</span>
                            </div>
                        </div>
                    </div>
                </el-col>

                <el-col :xs="24" :md="8">
                    <div class="info-card">
                        <h4>
                            <el-icon><Cpu /></el-icon>
                            性能指标
                        </h4>
                        <div class="info-list">
                            <div class="info-item">
                                <span class="label">CPU 使用率</span>
                                <span class="value">{{ systemStats.cpu }}%</span>
                            </div>
                            <div class="info-item">
                                <span class="label">内存使用</span>
                                <span class="value">{{ systemStats.memory }}%</span>
                            </div>
                            <div class="info-item">
                                <span class="label">磁盘使用</span>
                                <span class="value">{{ systemStats.disk }}%</span>
                            </div>
                        </div>
                    </div>
                </el-col>

                <el-col :xs="24" :md="8">
                    <div class="info-card">
                        <h4>
                            <el-icon><Link /></el-icon>
                            快速链接
                        </h4>
                        <div class="link-list">
                            <el-link @click="navigateTo('/system/menu')" underline="never">
                                <el-icon><Menu /></el-icon>
                                菜单管理
                            </el-link>
                            <el-link @click="navigateTo('/generator/history')" underline="never">
                                <el-icon><Tickets /></el-icon>
                                生成历史
                            </el-link>
                            <el-link href="/docs" target="_blank" underline="never">
                                <el-icon><Document /></el-icon>
                                API 文档
                            </el-link>
                        </div>
                    </div>
                </el-col>
            </el-row>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { 
    DataAnalysis, Grid, Setting, Document,
    TrendCharts, Lightning, Plus, FolderAdd, UserFilled,
    Clock, Refresh, CollectionTag, EditPen, Monitor, Cpu, 
    Link, Menu, Tickets
} from '@element-plus/icons-vue'
import { getOverview } from './statistics.js'

const router = useRouter()
const currentTime = ref('')
const loading = ref(false)

// 统计数据
const stats = ref({
    // 系统管理
    userCount: 0,
    roleCount: 0,
    menuCount: 0,
    deptCount: 0,
    
    // 代码生成
    tableCount: 0,
    genCount: 0,
    
    // 平台统计
    totalProjects: 0,
    totalTests: 0,
    successRate: 0,
    avgTime: 0,
    onlineUsers: 0
})

// 系统信息
const systemUptime = ref('0天0小时')
const systemStats = ref({
    cpu: 0,
    memory: 0,
    disk: 0
})

// 最近活动
const recentTests = ref([])
const recentGens = ref([])
const testsLoading = ref(false)
const gensLoading = ref(false)

// 导航到指定页面
const navigateTo = (path) => {
    router.push(path)
}

// 加载统计数据
const loadStats = async () => {
    loading.value = true
    try {
        const res = await getOverview()
        if (res.data.code === 200 && res.data.data) {
            const data = res.data.data
            // 更新统计数据
            stats.value = {
                ...stats.value,
                totalProjects: data.projectCount || 0,
                totalTests: data.totalTests || 0,
                successRate: data.successRate || 0,
                avgTime: data.avgTime || 0,
                userCount: data.userCount || 5,
                roleCount: data.roleCount || 3,
                tableCount: data.tableCount || 12,
                genCount: data.genCount || 8,
                onlineUsers: data.onlineUsers || 3
            }
        }
    } catch (error) {
        console.error('加载统计数据失败:', error)
        // 设置默认值
        stats.value = {
            userCount: 5,
            roleCount: 3,
            menuCount: 15,
            deptCount: 4,
            tableCount: 12,
            genCount: 8,
            totalProjects: 6,
            totalTests: 156,
            successRate: 92,
            avgTime: 245,
            onlineUsers: 3
        }
    } finally {
        loading.value = false
    }
}

// 加载最近测试
const loadRecentTests = async () => {
    testsLoading.value = true
    try {
        // 模拟数据
        recentTests.value = [
            { name: '用户表代码生成', status: 'success', create_time: '2026-01-09 10:30' },
            { name: '角色权限配置', status: 'success', create_time: '2026-01-09 10:15' },
            { name: '菜单结构优化', status: 'success', create_time: '2026-01-09 09:45' },
            { name: '部门层级调整', status: 'success', create_time: '2026-01-09 09:30' },
            { name: '系统配置更新', status: 'success', create_time: '2026-01-09 09:00' }
        ]
    } catch (error) {
        console.error('加载最近测试失败:', error)
    } finally {
        testsLoading.value = false
    }
}

// 加载最近生成
const loadRecentGens = async () => {
    gensLoading.value = true
    try {
        // 模拟数据
        recentGens.value = [
            { table_name: 'sys_user', create_time: '2026-01-09 11:00' },
            { table_name: 'api_project', create_time: '2026-01-09 10:45' },
            { table_name: 'test_case', create_time: '2026-01-09 10:20' },
            { table_name: 'gen_table', create_time: '2026-01-09 09:55' },
            { table_name: 'sys_menu', create_time: '2026-01-09 09:30' }
        ]
    } catch (error) {
        console.error('加载最近生成失败:', error)
    } finally {
        gensLoading.value = false
    }
}

// 辅助函数
const getStatusType = (status) => {
    const map = {
        'success': 'success',
        'failed': 'danger',
        'running': 'warning',
        'pending': 'info'
    }
    return map[status] || 'info'
}

const getStatusText = (status) => {
    const map = {
        'success': '成功',
        'failed': '失败',
        'running': '执行中',
        'pending': '等待中'
    }
    return map[status] || status
}

const getTestStatusClass = (status) => {
    const map = {
        'success': 'success',
        'failed': 'danger',
        'running': 'warning',
        'pending': 'info'
    }
    return map[status] || 'info'
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

// 更新系统信息
const updateSystemInfo = () => {
    // 模拟系统运行时间
    const startTime = new Date('2026-01-01')
    const now = new Date()
    const diff = now - startTime
    const days = Math.floor(diff / (1000 * 60 * 60 * 24))
    const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60))
    systemUptime.value = `${days}天${hours}小时`
    
    // 模拟系统性能数据
    systemStats.value = {
        cpu: Math.floor(Math.random() * 30) + 20, // 20-50%
        memory: Math.floor(Math.random() * 40) + 30, // 30-70%
        disk: Math.floor(Math.random() * 20) + 40 // 40-60%
    }
}

onMounted(() => {
    updateTime()
    setInterval(updateTime, 1000)
    updateSystemInfo()
    setInterval(updateSystemInfo, 30000) // 30秒更新一次系统信息
    
    loadStats()
    loadRecentTests()
    loadRecentGens()
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

/* 功能模块区域 */
.modules-section {
    background: white;
    border-radius: 12px;
    padding: 32px;
    margin-bottom: 32px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.modules-section h2 {
    font-size: 24px;
    color: #333;
    margin: 0 0 24px 0;
    display: flex;
    align-items: center;
    gap: 12px;
}

.module-card {
    background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
    border-radius: 12px;
    padding: 24px;
    cursor: pointer;
    transition: all 0.3s ease;
    border: 2px solid transparent;
    height: 100%;
}

.module-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
    border-color: var(--el-color-primary);
}

.module-card.system:hover {
    border-color: #667eea;
}

.module-card.generator:hover {
    border-color: #f093fb;
}

.module-icon {
    width: 60px;
    height: 60px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 28px;
    color: white;
    margin-bottom: 16px;
}

.module-card.system .module-icon {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.module-card.generator .module-icon {
    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.module-content h3 {
    font-size: 18px;
    color: #333;
    margin: 0 0 8px 0;
    font-weight: 600;
}

.module-content p {
    font-size: 14px;
    color: #666;
    margin: 0 0 12px 0;
    line-height: 1.5;
}

.module-stats {
    display: flex;
    gap: 16px;
}

.module-stats span {
    font-size: 12px;
    color: #999;
    background: rgba(0, 0, 0, 0.05);
    padding: 4px 8px;
    border-radius: 4px;
}

/* 概览区域 */
.overview-section {
    margin-bottom: 32px;
}

.stats-panel {
    background: white;
    border-radius: 12px;
    padding: 24px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
    height: 100%;
}

.stats-panel h3 {
    font-size: 18px;
    color: #333;
    margin: 0 0 20px 0;
    display: flex;
    align-items: center;
    gap: 8px;
}

.stats-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 20px;
}

.stat-item {
    text-align: center;
    padding: 16px;
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    border-radius: 8px;
}

.stat-number {
    font-size: 28px;
    font-weight: bold;
    color: #667eea;
    margin-bottom: 4px;
}

.stat-label {
    font-size: 14px;
    color: #666;
}

.quick-actions {
    background: white;
    border-radius: 12px;
    padding: 24px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
    height: 100%;
}

.quick-actions h3 {
    font-size: 18px;
    color: #333;
    margin: 0 0 20px 0;
    display: flex;
    align-items: center;
    gap: 8px;
}

.action-list {
    display: flex;
    flex-direction: column;
    gap: 12px;
}

.action-btn {
    width: 100%;
    justify-content: flex-start;
    gap: 8px;
}

/* 活动区域 */
.activity-section {
    margin-bottom: 32px;
}

.activity-panel {
    background: white;
    border-radius: 12px;
    padding: 24px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
    height: 100%;
}

.panel-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    padding-bottom: 12px;
    border-bottom: 1px solid #eee;
}

.panel-header h3 {
    font-size: 16px;
    color: #333;
    margin: 0;
    display: flex;
    align-items: center;
    gap: 8px;
}

.activity-content {
    min-height: 200px;
}

.no-data {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 150px;
}

.activity-list {
    display: flex;
    flex-direction: column;
    gap: 12px;
}

.activity-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px 16px;
    background: #f5f7fa;
    border-radius: 8px;
    transition: all 0.3s ease;
}

.activity-item:hover {
    background: #e8f4ff;
}

.activity-icon {
    width: 36px;
    height: 36px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 16px;
    color: white;
}

.activity-icon.success {
    background: #67C23A;
}

.activity-icon.danger {
    background: #F56C6C;
}

.activity-icon.warning {
    background: #E6A23C;
}

.activity-icon.info {
    background: #909399;
}

.activity-icon.generator {
    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.activity-info {
    flex: 1;
    min-width: 0;
}

.activity-title {
    font-size: 14px;
    color: #333;
    font-weight: 500;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.activity-time {
    font-size: 12px;
    color: #999;
    margin-top: 2px;
}

.activity-status {
    flex-shrink: 0;
}

/* 系统信息区域 */
.system-info {
    margin-bottom: 32px;
}

.info-card {
    background: white;
    border-radius: 12px;
    padding: 24px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
    height: 100%;
}

.info-card h4 {
    font-size: 16px;
    color: #333;
    margin: 0 0 16px 0;
    display: flex;
    align-items: center;
    gap: 8px;
}

.info-list {
    display: flex;
    flex-direction: column;
    gap: 12px;
}

.info-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 0;
    border-bottom: 1px solid #f0f0f0;
}

.info-item:last-child {
    border-bottom: none;
}

.info-item .label {
    font-size: 14px;
    color: #666;
}

.info-item .value {
    font-size: 14px;
    color: #333;
    font-weight: 500;
}

.link-list {
    display: flex;
    flex-direction: column;
    gap: 12px;
}

.link-list .el-link {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 12px;
    border-radius: 6px;
    transition: all 0.3s ease;
}

.link-list .el-link:hover {
    background: #f5f7fa;
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

    .modules-section {
        padding: 20px;
    }

    .stats-grid {
        grid-template-columns: 1fr;
    }

    .action-list {
        gap: 8px;
    }
}
</style>
