import { ElMessage, ElNotification } from 'element-plus'

export type NotifyType = 'success' | 'error' | 'warning' | 'info'

function toText(message: unknown): string {
  if (typeof message === 'string') return message
  if (message instanceof Error) return message.message
  try {
    return JSON.stringify(message)
  } catch {
    return String(message)
  }
}

const notify = {
  success(message: unknown) {
    ElMessage.success(toText(message))
  },
  error(message: unknown) {
    ElMessage.error(toText(message))
  },
  warning(message: unknown) {
    ElMessage.warning(toText(message))
  },
  info(message: unknown) {
    ElMessage.info(toText(message))
  },
  // 可选：桌面右上角通知
  banner(message: unknown, type: NotifyType = 'info', title = '提示') {
    ElNotification({
      title,
      message: toText(message),
      type
    })
  }
}

export default notify 