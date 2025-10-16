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

        <!-- 快速导航 -->
        <div class="quick-nav-section">
            <h2>快速导航</h2>
            <div class="nav-grid">
                <div class="nav-item" @click="navigateTo('/ApiProjectList')">
                    <div class="nav-icon projects">
                        <el-icon><FolderOpened /></el-icon>
                    </div>
                    <h4>项目管理</h4>
                    <p>创建和管理测试项目</p>
                </div>

                <div class="nav-item" @click="navigateTo('/ApiInfoList')">
                    <div class="nav-icon apis">
                        <el-icon><Connection /></el-icon>
                    </div>
                    <h4>接口管理</h4>
                    <p>定义和编辑测试接口</p>
                </div>

                <div class="nav-item" @click="navigateTo('/test-cases')">
                    <div class="nav-icon tests">
                        <el-icon><CollectionTag /></el-icon>
                    </div>
                    <h4>测试用例</h4>
                    <p>编写和执行测试用例</p>
                </div>

                <div class="nav-item" @click="navigateTo('/ai-chat')">
                    <div class="nav-icon ai">
                        <el-icon><ChatDotRound /></el-icon>
                    </div>
                    <h4>AI测试助手</h4>
                    <p>使用AI生成测试用例</p>
                </div>

                <div class="nav-item" @click="navigateTo('/ai-models')">
                    <div class="nav-icon config">
                        <el-icon><Setting /></el-icon>
                    </div>
                    <h4>AI模型配置</h4>
                    <p>管理AI模型和API密钥</p>
                </div>

                <div class="nav-item" @click="navigateTo('/userList')">
                    <div class="nav-icon user">
                        <el-icon><User /></el-icon>
                    </div>
                    <h4>用户管理</h4>
                    <p>管理系统用户和权限</p>
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
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { DataAnalysis, FolderOpened, Connection, CollectionTag, ChatDotRound, Setting, User } from '@element-plus/icons-vue'

const router = useRouter()
const currentTime = ref('')

// 统计数据
const stats = ref({
    projectCount: 8,
    apiCount: 42,
    testcaseCount: 156,
    aiModelCount: 10,
    successRate: 95,
    totalTests: 1230,
    avgTime: 450,
    users: 15
})

// 导航函数
const navigateTo = (path) => {
    router.push(path)
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

/* 快速导航 */
.quick-nav-section {
    margin-bottom: 32px;
}

.quick-nav-section h2,
.features-section h2 {
    font-size: 24px;
    color: #333;
    margin: 0 0 20px 0;
    display: flex;
    align-items: center;
    gap: 12px;
}

.quick-nav-section h2::before,
.features-section h2::before {
    content: '';
    width: 4px;
    height: 24px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 2px;
}

.nav-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 16px;
}

.nav-item {
    background: white;
    border-radius: 12px;
    padding: 24px;
    text-align: center;
    cursor: pointer;
    transition: all 0.3s ease;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.nav-item:hover {
    transform: translateY(-8px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
}

.nav-icon {
    width: 64px;
    height: 64px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 28px;
    color: white;
    margin: 0 auto 12px;
}

.nav-icon.projects {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.nav-icon.apis {
    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.nav-icon.tests {
    background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.nav-icon.ai {
    background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
}

.nav-icon.config {
    background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

.nav-icon.user {
    background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
}

.nav-item h4 {
    font-size: 16px;
    color: #333;
    margin: 12px 0 8px 0;
}

.nav-item p {
    font-size: 12px;
    color: #999;
    margin: 0;
}

/* 功能介绍 */
.features-section {
    background: white;
    border-radius: 12px;
    padding: 32px;
    margin-bottom: 32px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
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

    .nav-grid {
        grid-template-columns: repeat(2, 1fr);
    }

    .features-section {
        padding: 20px;
    }
}
</style>
