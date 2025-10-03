// Copyright (c) 2025 左岚. All rights reserved.
/**
 * 菜单管理状态
 * 适配 FastAPI RBAC 权限系统
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'
import {
  getMenuList,
  getMenuTree,
  createMenu,
  updateMenu,
  deleteMenu,
  getUserMenus,
  type Menu,
  type MenuTree,
  type MenuCreateData,
  type MenuUpdateData
} from '@/api/menu'
import { ElMessage } from 'element-plus'

export const useMenuStore = defineStore('menu', () => {
  // State
  const menus = ref<Menu[]>([])
  const menuTree = ref<MenuTree[]>([])
  const userMenus = ref<Menu[]>([])
  const loading = ref(false)

  // Actions
  async function fetchMenuList() {
    try {
      loading.value = true
      const response = await getMenuList()
      
      if (response.success && response.data) {
        menus.value = response.data
      }
    } catch (error) {
      console.error('获取菜单列表失败:', error)
      ElMessage.error('获取菜单列表失败')
    } finally {
      loading.value = false
    }
  }

  async function fetchMenuTree() {
    try {
      loading.value = true
      const response = await getMenuTree()
      
      if (response.success && response.data) {
        menuTree.value = response.data
      }
    } catch (error) {
      console.error('获取菜单树失败:', error)
      ElMessage.error('获取菜单树失败')
    } finally {
      loading.value = false
    }
  }

  async function fetchUserMenus(userId: number) {
    try {
      loading.value = true
      const response = await getUserMenus(userId)
      
      if (response.success && response.data) {
        userMenus.value = response.data
      }
    } catch (error) {
      console.error('获取用户菜单失败:', error)
      ElMessage.error('获取用户菜单失败')
    } finally {
      loading.value = false
    }
  }

  async function createMenuAction(data: MenuCreateData) {
    try {
      loading.value = true
      const response = await createMenu(data)
      
      if (response.success) {
        ElMessage.success(response.message || '创建菜单成功')
        return true
      } else {
        ElMessage.error(response.message || '创建菜单失败')
        return false
      }
    } catch (error: any) {
      console.error('创建菜单失败:', error)
      ElMessage.error(error.message || '创建菜单失败')
      return false
    } finally {
      loading.value = false
    }
  }

  async function updateMenuAction(menuId: number, data: MenuUpdateData) {
    try {
      loading.value = true
      const response = await updateMenu(menuId, data)
      
      if (response.success) {
        ElMessage.success(response.message || '更新菜单成功')
        return true
      } else {
        ElMessage.error(response.message || '更新菜单失败')
        return false
      }
    } catch (error: any) {
      console.error('更新菜单失败:', error)
      ElMessage.error(error.message || '更新菜单失败')
      return false
    } finally {
      loading.value = false
    }
  }

  async function deleteMenuAction(menuId: number) {
    try {
      loading.value = true
      const response = await deleteMenu(menuId)
      
      if (response.success) {
        ElMessage.success(response.message || '删除菜单成功')
        return true
      } else {
        ElMessage.error(response.message || '删除菜单失败')
        return false
      }
    } catch (error: any) {
      console.error('删除菜单失败:', error)
      ElMessage.error(error.message || '删除菜单失败')
      return false
    } finally {
      loading.value = false
    }
  }

  return {
    // State
    menus,
    menuTree,
    userMenus,
    loading,
    // Actions
    fetchMenuList,
    fetchMenuTree,
    fetchUserMenus,
    createMenu: createMenuAction,
    updateMenu: updateMenuAction,
    deleteMenu: deleteMenuAction
  }
})

