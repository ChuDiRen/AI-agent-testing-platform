// Copyright (c) 2025 左岚. All rights reserved.
/**
 * 全局加载状态管理
 */
import { ref } from 'vue'
import { ElLoading } from 'element-plus'
import type { LoadingInstance } from 'element-plus/es/components/loading/src/loading'

const globalLoading = ref(false)
let loadingInstance: LoadingInstance | null = null

export function useLoading() {
  /**
   * 显示全局加载
   */
  const showLoading = (text: string = '加载中...') => {
    globalLoading.value = true
    loadingInstance = ElLoading.service({
      lock: true,
      text,
      background: 'rgba(0, 0, 0, 0.7)'
    })
  }

  /**
   * 隐藏全局加载
   */
  const hideLoading = () => {
    globalLoading.value = false
    if (loadingInstance) {
      loadingInstance.close()
      loadingInstance = null
    }
  }

  /**
   * 异步操作包装器
   */
  const withLoading = async <T>(
    fn: () => Promise<T>,
    loadingText?: string
  ): Promise<T> => {
    showLoading(loadingText)
    try {
      return await fn()
    } finally {
      hideLoading()
    }
  }

  return {
    globalLoading,
    showLoading,
    hideLoading,
    withLoading
  }
}

