import { Confirm, Message } from '@/utils/message'

/**
 * 删除确认组合式函数
 * 用于统一处理删除操作的二次确认
 */
export function useDeleteConfirm() {
  /**
   * 执行删除操作（带确认）
   * @param {Function} deleteFunc - 删除函数
   * @param {string} confirmMessage - 确认消息
   * @param {string} successMessage - 成功消息
   * @param {Function} callback - 删除成功后的回调函数
   */
  const confirmDelete = async (
    deleteFunc,
    confirmMessage = '此操作将永久删除该数据，是否继续？',
    successMessage = '删除成功',
    callback = null
  ) => {
    try {
      // 显示确认对话框
      const confirmed = await Confirm.delete(confirmMessage)
      
      if (!confirmed) {
        return false
      }

      // 执行删除操作
      const result = await deleteFunc()
      
      // 显示成功消息
      Message.success(successMessage)
      
      // 执行回调
      if (callback && typeof callback === 'function') {
        callback(result)
      }
      
      return true
    } catch (error) {
      Message.error('删除失败：' + (error.message || '未知错误'))
      return false
    }
  }

  /**
   * 批量删除确认
   * @param {Function} deleteFunc - 删除函数
   * @param {number} count - 删除数量
   * @param {Function} callback - 删除成功后的回调函数
   */
  const confirmBatchDelete = async (
    deleteFunc,
    count,
    callback = null
  ) => {
    const confirmMessage = `确定要删除选中的 ${count} 条数据吗？此操作不可恢复！`
    const successMessage = `成功删除 ${count} 条数据`
    
    return await confirmDelete(deleteFunc, confirmMessage, successMessage, callback)
  }

  return {
    confirmDelete,
    confirmBatchDelete
  }
}
