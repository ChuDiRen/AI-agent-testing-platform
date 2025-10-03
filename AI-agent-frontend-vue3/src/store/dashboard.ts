// Copyright (c) 2025 左岚. All rights reserved.
/**
 * 仪表板状态管理
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getDashboardStats, getTrendData, type DashboardStats, type TrendData } from '@/api/dashboard'

export const useDashboardStore = defineStore('dashboard', () => {
  // State
  const stats = ref<DashboardStats>({
    totalCases: 0,
    webCases: 0,
    apiCases: 0,
    appCases: 0
  })

  const trendData = ref<TrendData>({
    timeline: [],
    web: [],
    api: [],
    app: []
  })

  const loading = ref(false)

  // Actions
  async function fetchStats() {
    try {
      loading.value = true
      const response = await getDashboardStats()
      
      if (response.code === 200 && response.data) {
        stats.value = response.data
      }
    } catch (error) {
      console.error('Fetch stats error:', error)
      // 使用模拟数据作为后备
      stats.value = {
        totalCases: 25,
        webCases: 16,
        apiCases: 5,
        appCases: 4
      }
    } finally {
      loading.value = false
    }
  }

  async function fetchTrendData() {
    try {
      loading.value = true
      const response = await getTrendData()
      
      if (response.code === 200 && response.data) {
        trendData.value = response.data
      }
    } catch (error) {
      console.error('Fetch trend data error:', error)
      // 使用模拟数据作为后备
      trendData.value = {
        timeline: ['2024年9月', '2024年11月', '2025年1月', '2025年3月', '2025年5月', '2025年7月'],
        web: [3, 4, 1, 1, 4, 0],
        api: [0, 0, 1, 0, 3, 1],
        app: [0, 0, 0, 2, 2, 0]
      }
    } finally {
      loading.value = false
    }
  }

  async function fetchDashboardData() {
    await Promise.all([fetchStats(), fetchTrendData()])
  }

  return {
    // State
    stats,
    trendData,
    loading,
    // Actions
    fetchStats,
    fetchTrendData,
    fetchDashboardData
  }
})

