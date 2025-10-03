// Copyright (c) 2025 左岚. All rights reserved.
/**
 * 测试用例状态管理
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'
import {
  getTestCaseList,
  getTestCase,
  createTestCase,
  updateTestCase,
  deleteTestCase,
  executeTestCase,
  type TestCase,
  type TestCaseListParams
} from '@/api/testcase'
import { ElMessage } from 'element-plus'

export const useTestCaseStore = defineStore('testcase', () => {
  // State
  const testCases = ref<TestCase[]>([])
  const currentTestCase = ref<TestCase | null>(null)
  const total = ref(0)
  const loading = ref(false)

  // Actions
  async function fetchTestCaseList(params: TestCaseListParams = {}) {
    try {
      loading.value = true
      const response = await getTestCaseList(params)
      
      if (response.code === 200 && response.data) {
        testCases.value = response.data.items
        total.value = response.data.total
      }
    } catch (error) {
      console.error('Fetch test case list error:', error)
      ElMessage.error('获取测试用例列表失败')
    } finally {
      loading.value = false
    }
  }

  async function fetchTestCase(id: number) {
    try {
      loading.value = true
      const response = await getTestCase(id)
      
      if (response.code === 200 && response.data) {
        currentTestCase.value = response.data
        return response.data
      }
    } catch (error) {
      console.error('Fetch test case error:', error)
      ElMessage.error('获取测试用例详情失败')
    } finally {
      loading.value = false
    }
  }

  async function createTestCaseAction(data: Partial<TestCase>) {
    try {
      loading.value = true
      const response = await createTestCase(data)
      
      if (response.code === 200) {
        ElMessage.success('创建测试用例成功')
        return true
      }
      return false
    } catch (error) {
      console.error('Create test case error:', error)
      ElMessage.error('创建测试用例失败')
      return false
    } finally {
      loading.value = false
    }
  }

  async function updateTestCaseAction(id: number, data: Partial<TestCase>) {
    try {
      loading.value = true
      const response = await updateTestCase(id, data)
      
      if (response.code === 200) {
        ElMessage.success('更新测试用例成功')
        return true
      }
      return false
    } catch (error) {
      console.error('Update test case error:', error)
      ElMessage.error('更新测试用例失败')
      return false
    } finally {
      loading.value = false
    }
  }

  async function deleteTestCaseAction(id: number) {
    try {
      loading.value = true
      const response = await deleteTestCase(id)
      
      if (response.code === 200) {
        ElMessage.success('删除测试用例成功')
        // 从列表中移除
        testCases.value = testCases.value.filter(tc => tc.id !== id)
        total.value -= 1
        return true
      }
      return false
    } catch (error) {
      console.error('Delete test case error:', error)
      ElMessage.error('删除测试用例失败')
      return false
    } finally {
      loading.value = false
    }
  }

  async function executeTestCaseAction(id: number) {
    try {
      loading.value = true
      const response = await executeTestCase(id)
      
      if (response.code === 200) {
        ElMessage.success('测试用例执行成功')
        return response.data
      }
      return null
    } catch (error) {
      console.error('Execute test case error:', error)
      ElMessage.error('执行测试用例失败')
      return null
    } finally {
      loading.value = false
    }
  }

  return {
    // State
    testCases,
    currentTestCase,
    total,
    loading,
    // Actions
    fetchTestCaseList,
    fetchTestCase,
    createTestCase: createTestCaseAction,
    updateTestCase: updateTestCaseAction,
    deleteTestCase: deleteTestCaseAction,
    executeTestCase: executeTestCaseAction
  }
})

