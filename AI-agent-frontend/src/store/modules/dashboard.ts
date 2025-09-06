// Copyright (c) 2025 左岚. All rights reserved.
// 仪表盘数据 Store（带TTL缓存）  # 注释
import { defineStore } from 'pinia'
import { DashboardApi, type SystemInfo } from '@/api/modules/dashboard'

interface StatsData { userCount: number; roleCount: number; menuCount: number; deptCount: number }

const STATS_TTL_MS = 30_000  // 统计数据缓存30秒  # 注释
const SYS_TTL_MS = 30_000     // 系统信息缓存30秒  # 注释

export const useDashboardStore = defineStore('dashboard', {
  state: () => ({
    statsData: { userCount: 0, roleCount: 0, menuCount: 0, deptCount: 0 } as StatsData,
    systemInfo: {
      system_version: 'v1.0.0', server_info: 'FastAPI + Vue 3', database_info: 'SQLite', last_login_time: undefined
    } as SystemInfo,
    lastFetched: { stats: 0, sys: 0 },
    loadingStats: false,
    loadingSys: false,
  }),

  actions: {
    async loadStats(force = false) {
      const now = Date.now()
      if (!force && now - this.lastFetched.stats < STATS_TTL_MS) return  // 命中TTL  # 注释
      if (this.loadingStats) return
      try {
        this.loadingStats = true
        const res = await DashboardApi.getStats()
        if (res.success && res.data) {
          this.statsData = {
            userCount: res.data.user_count,
            roleCount: res.data.role_count,
            menuCount: res.data.menu_count,
            deptCount: res.data.department_count
          }
          this.lastFetched.stats = now
        }
      } finally {
        this.loadingStats = false
      }
    },

    async loadSystemInfo(force = false) {
      const now = Date.now()
      if (!force && now - this.lastFetched.sys < SYS_TTL_MS) return  // 命中TTL  # 注释
      if (this.loadingSys) return
      try {
        this.loadingSys = true
        const res = await DashboardApi.getSystemInfo()
        if (res.success && res.data) {
          this.systemInfo = res.data
          this.lastFetched.sys = now
        }
      } finally {
        this.loadingSys = false
      }
    }
  },

  persist: {
    key: 'dashboard-store',
    storage: localStorage,
  }
})

