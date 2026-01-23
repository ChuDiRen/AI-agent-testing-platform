import { ElMessage, ElMessageBox, ElNotification } from 'element-plus'

/**
 * 全局消息提示工具
 */
export const Message = {
  /**
   * 成功消息
   * @param {string} message - 消息内容
   * @param {number} duration - 显示时长（毫秒）
   */
  success(message, duration = 3000) {
    ElMessage({
      message: message,
      type: 'success',
      duration: duration,
      showClose: true
    })
  },

  /**
   * 错误消息
   * @param {string} message - 消息内容
   * @param {number} duration - 显示时长（毫秒）
   */
  error(message, duration = 3000) {
    ElMessage({
      message: message,
      type: 'error',
      duration: duration,
      showClose: true
    })
  },

  /**
   * 警告消息
   * @param {string} message - 消息内容
   * @param {number} duration - 显示时长（毫秒）
   */
  warning(message, duration = 3000) {
    ElMessage({
      message: message,
      type: 'warning',
      duration: duration,
      showClose: true
    })
  },

  /**
   * 信息消息
   * @param {string} message - 消息内容
   * @param {number} duration - 显示时长（毫秒）
   */
  info(message, duration = 3000) {
    ElMessage({
      message: message,
      type: 'info',
      duration: duration,
      showClose: true
    })
  },

  /**
   * 通知消息
   * @param {string} title - 标题
   * @param {string} message - 消息内容
   * @param {string} type - 类型 success/warning/info/error
   * @param {number} duration - 显示时长（毫秒）
   */
  notify(title, message, type = 'info', duration = 4500) {
    ElNotification({
      title: title,
      message: message,
      type: type,
      duration: duration
    })
  }
}

/**
 * 确认对话框工具
 */
export const Confirm = {
  /**
   * 删除确认对话框
   * @param {string} message - 确认消息
   * @param {string} title - 对话框标题
   * @returns {Promise} - 返回 Promise，确认返回 true，取消返回 false
   */
  delete(message = '此操作将永久删除该数据，是否继续？', title = '删除确认') {
    return ElMessageBox.confirm(
      message,
      title,
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
        center: true
      }
    ).then(() => {
      return true
    }).catch(() => {
      Message.info('已取消删除')
      return false
    })
  },

  /**
   * 通用确认对话框
   * @param {string} message - 确认消息
   * @param {string} title - 对话框标题
   * @param {string} type - 类型 warning/info/success/error
   * @returns {Promise} - 返回 Promise，确认返回 true，取消返回 false
   */
  show(message, title = '确认', type = 'warning') {
    return ElMessageBox.confirm(
      message,
      title,
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: type,
        center: true
      }
    ).then(() => {
      return true
    }).catch(() => {
      return false
    })
  }
}

export default {
  Message,
  Confirm
}
