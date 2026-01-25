/**
 * 消息工具函数
 * 封装 Element Plus 的消息和确认对话框
 */
import { ElMessageBox, ElMessage } from 'element-plus'

/**
 * 确认对话框
 */
export const Confirm = {
  /**
   * 删除确认对话框
   * @param {string} message - 确认消息
   * @param {string} title - 对话框标题
   * @returns {Promise<boolean>} 是否确认
   */
  async delete(message, title = '确认删除') {
    try {
      await ElMessageBox.confirm(
        message,
        title,
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning',
        }
      )
      return true
    } catch {
      return false
    }
  },

  /**
   * 通用确认对话框
   * @param {string} message - 确认消息
   * @param {string} title - 对话框标题
   * @param {Object} options - 额外选项
   * @returns {Promise<boolean>} 是否确认
   */
  async confirm(message, title = '确认操作', options = {}) {
    try {
      await ElMessageBox.confirm(
        message,
        title,
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning',
          ...options
        }
      )
      return true
    } catch {
      return false
    }
  }
}

/**
 * 消息提示
 */
export const Message = {
  /**
   * 成功消息
   * @param {string} message - 消息内容
   * @param {Object} options - 额外选项
   */
  success(message, options = {}) {
    ElMessage.success({
      message,
      duration: 3000,
      ...options
    })
  },

  /**
   * 错误消息
   * @param {string} message - 消息内容
   * @param {Object} options - 额外选项
   */
  error(message, options = {}) {
    ElMessage.error({
      message,
      duration: 5000,
      ...options
    })
  },

  /**
   * 警告消息
   * @param {string} message - 消息内容
   * @param {Object} options - 额外选项
   */
  warning(message, options = {}) {
    ElMessage.warning({
      message,
      duration: 4000,
      ...options
    })
  },

  /**
   * 信息消息
   * @param {string} message - 消息内容
   * @param {Object} options - 额外选项
   */
  info(message, options = {}) {
    ElMessage.info({
      message,
      duration: 3000,
      ...options
    })
  },

  /**
   * 加载消息
   * @param {string} message - 消息内容
   * @param {Object} options - 额外选项
   * @returns {Object} 消息实例
   */
  loading(message, options = {}) {
    return ElMessage.loading({
      message,
      duration: 0,
      ...options
    })
  }
}

/**
 * 通知提示
 */
export const Notify = {
  /**
   * 成功通知
   * @param {string} title - 通知标题
   * @param {string} message - 通知内容
   * @param {Object} options - 额外选项
   */
  success(title, message = '', options = {}) {
    ElMessage.success({
      title,
      message,
      duration: 4000,
      ...options
    })
  },

  /**
   * 错误通知
   * @param {string} title - 通知标题
   * @param {string} message - 通知内容
   * @param {Object} options - 额外选项
   */
  error(title, message = '', options = {}) {
    ElMessage.error({
      title,
      message,
      duration: 6000,
      ...options
    })
  },

  /**
   * 警告通知
   * @param {string} title - 通知标题
   * @param {string} message - 通知内容
   * @param {Object} options - 额外选项
   */
  warning(title, message = '', options = {}) {
    ElMessage.warning({
      title,
      message,
      duration: 5000,
      ...options
    })
  },

  /**
   * 信息通知
   * @param {string} title - 通知标题
   * @param {string} message - 通知内容
   * @param {Object} options - 额外选项
   */
  info(title, message = '', options = {}) {
    ElMessage.info({
      title,
      message,
      duration: 4000,
      ...options
    })
  }
}

// 默认导出
export default {
  Confirm,
  Message,
  Notify
}
