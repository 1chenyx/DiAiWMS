import { ElMessageBox } from 'element-plus'

export interface ConfirmOptions {
  title?: string
  message?: string
  confirmButtonText?: string
  cancelButtonText?: string
  type?: 'success' | 'warning' | 'info' | 'error'
}

export function useConfirm() {
  const confirm = async (
    message: string,
    options: ConfirmOptions = {}
  ): Promise<boolean> => {
    const {
      title = '提示',
      confirmButtonText = '确定',
      cancelButtonText = '取消',
      type = 'warning'
    } = options

    try {
      await ElMessageBox.confirm(message, title, {
        confirmButtonText,
        cancelButtonText,
        type
      })
      return true
    } catch {
      return false
    }
  }

  const confirmDelete = async (itemName?: string): Promise<boolean> => {
    const message = itemName 
      ? `确定要删除${itemName}吗？`
      : '确定要删除吗？'
    return confirm(message, { title: '警告', type: 'warning' })
  }

  const confirmAction = async (actionName: string): Promise<boolean> => {
    const message = `确定要${actionName}吗？`
    return confirm(message, { title: '提示', type: 'info' })
  }

  return {
    confirm,
    confirmDelete,
    confirmAction
  }
}
