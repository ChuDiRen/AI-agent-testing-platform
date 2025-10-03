// Copyright (c) 2025 左岚. All rights reserved.
/**
 * 部门管理状态
 * 适配 FastAPI RBAC 权限系统
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'
import {
  getDepartmentList,
  createDepartment,
  updateDepartment,
  deleteDepartment,
  getDepartmentDetail,
  type Department,
  type DepartmentCreateData,
  type DepartmentUpdateData
} from '@/api/department'
import { ElMessage } from 'element-plus'

export const useDepartmentStore = defineStore('department', () => {
  // State
  const departments = ref<Department[]>([])
  const loading = ref(false)
  const currentDepartment = ref<Department | null>(null)

  // Actions
  async function fetchDepartmentList() {
    try {
      loading.value = true
      const response = await getDepartmentList()
      
      if (response.success && response.data) {
        departments.value = response.data
      }
    } catch (error) {
      console.error('获取部门列表失败:', error)
      ElMessage.error('获取部门列表失败')
    } finally {
      loading.value = false
    }
  }

  async function fetchDepartmentDetail(deptId: number) {
    try {
      loading.value = true
      const response = await getDepartmentDetail(deptId)
      
      if (response.success && response.data) {
        currentDepartment.value = response.data
        return response.data
      }
      return null
    } catch (error) {
      console.error('获取部门详情失败:', error)
      ElMessage.error('获取部门详情失败')
      return null
    } finally {
      loading.value = false
    }
  }

  async function createDepartmentAction(data: DepartmentCreateData) {
    try {
      loading.value = true
      const response = await createDepartment(data)
      
      if (response.success) {
        ElMessage.success(response.message || '创建部门成功')
        return true
      } else {
        ElMessage.error(response.message || '创建部门失败')
        return false
      }
    } catch (error: any) {
      console.error('创建部门失败:', error)
      ElMessage.error(error.message || '创建部门失败')
      return false
    } finally {
      loading.value = false
    }
  }

  async function updateDepartmentAction(deptId: number, data: DepartmentUpdateData) {
    try {
      loading.value = true
      const response = await updateDepartment(deptId, data)
      
      if (response.success) {
        ElMessage.success(response.message || '更新部门成功')
        return true
      } else {
        ElMessage.error(response.message || '更新部门失败')
        return false
      }
    } catch (error: any) {
      console.error('更新部门失败:', error)
      ElMessage.error(error.message || '更新部门失败')
      return false
    } finally {
      loading.value = false
    }
  }

  async function deleteDepartmentAction(deptId: number) {
    try {
      loading.value = true
      const response = await deleteDepartment(deptId)
      
      if (response.success) {
        ElMessage.success(response.message || '删除部门成功')
        departments.value = departments.value.filter(d => d.dept_id !== deptId)
        return true
      } else {
        ElMessage.error(response.message || '删除部门失败')
        return false
      }
    } catch (error: any) {
      console.error('删除部门失败:', error)
      ElMessage.error(error.message || '删除部门失败')
      return false
    } finally {
      loading.value = false
    }
  }

  return {
    // State
    departments,
    loading,
    currentDepartment,
    // Actions
    fetchDepartmentList,
    fetchDepartmentDetail,
    createDepartment: createDepartmentAction,
    updateDepartment: updateDepartmentAction,
    deleteDepartment: deleteDepartmentAction
  }
})

