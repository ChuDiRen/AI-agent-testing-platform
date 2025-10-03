// Copyright (c) 2025 左岚. All rights reserved.
/**
 * 测试报告 Store
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'
import type {
  TestReport,
  ReportListParams,
  ReportCreateData,
  ReportUpdateData,
  ReportStatistics
} from '@/api/report'
import {
  getReportList,
  getReportDetail,
  createReport,
  updateReport,
  deleteReport,
  getReportStatistics
} from '@/api/report'

export const useReportStore = defineStore('report', () => {
  // 状态
  const reports = ref<TestReport[]>([])
  const currentReport = ref<TestReport | null>(null)
  const statistics = ref<ReportStatistics | null>(null)
  const total = ref(0)
  const loading = ref(false)

  /**
   * 获取测试报告列表
   */
  const fetchReports = async (params: ReportListParams = {}) => {
    loading.value = true
    try {
      const response = await getReportList(params)
      if (response.data.code === 200) {
        reports.value = response.data.data.reports
        total.value = response.data.data.total
        return true
      }
      return false
    } catch (error) {
      console.error('获取测试报告列表失败:', error)
      return false
    } finally {
      loading.value = false
    }
  }

  /**
   * 获取测试报告详情
   */
  const fetchReportDetail = async (id: number) => {
    loading.value = true
    try {
      const response = await getReportDetail(id)
      if (response.data.code === 200) {
        currentReport.value = response.data.data
        return true
      }
      return false
    } catch (error) {
      console.error('获取测试报告详情失败:', error)
      return false
    } finally {
      loading.value = false
    }
  }

  /**
   * 创建测试报告
   */
  const addReport = async (data: ReportCreateData) => {
    loading.value = true
    try {
      const response = await createReport(data)
      if (response.data.code === 200) {
        return true
      }
      return false
    } catch (error) {
      console.error('创建测试报告失败:', error)
      return false
    } finally {
      loading.value = false
    }
  }

  /**
   * 更新测试报告
   */
  const modifyReport = async (id: number, data: ReportUpdateData) => {
    loading.value = true
    try {
      const response = await updateReport(id, data)
      if (response.data.code === 200) {
        return true
      }
      return false
    } catch (error) {
      console.error('更新测试报告失败:', error)
      return false
    } finally {
      loading.value = false
    }
  }

  /**
   * 删除测试报告
   */
  const removeReport = async (id: number) => {
    loading.value = true
    try {
      const response = await deleteReport(id)
      if (response.data.code === 200) {
        return true
      }
      return false
    } catch (error) {
      console.error('删除测试报告失败:', error)
      return false
    } finally {
      loading.value = false
    }
  }

  /**
   * 获取统计信息
   */
  const fetchStatistics = async () => {
    loading.value = true
    try {
      const response = await getReportStatistics()
      if (response.data.code === 200) {
        statistics.value = response.data.data
        return true
      }
      return false
    } catch (error) {
      console.error('获取统计信息失败:', error)
      return false
    } finally {
      loading.value = false
    }
  }

  return {
    // 状态
    reports,
    currentReport,
    statistics,
    total,
    loading,
    // 方法
    fetchReports,
    fetchReportDetail,
    addReport,
    modifyReport,
    removeReport,
    fetchStatistics
  }
})

