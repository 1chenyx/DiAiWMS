import { ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

export interface UseDialogOptions<T> {
  title?: string
  width?: string | number
  defaultData?: () => T
  onSubmit?: (data: T) => Promise<void>
}

export function useDialog<T extends Record<string, any>>(options: UseDialogOptions<T> = {}) {
  const { title = '对话框', width = '600px', defaultData, onSubmit } = options

  const visible = ref(false)
  const loading = ref(false)
  const formData = ref<T>({} as T)
  const dialogTitle = ref(title)

  const open = (data?: Partial<T>, customTitle?: string) => {
    if (data) {
      formData.value = { ...formData.value, ...data }
    } else if (defaultData) {
      formData.value = defaultData()
    }
    if (customTitle) {
      dialogTitle.value = customTitle
    } else {
      dialogTitle.value = title
    }
    visible.value = true
  }

  const close = () => {
    visible.value = false
    formData.value = {} as T
  }

  const submit = async () => {
    if (!onSubmit) return

    loading.value = true
    try {
      await onSubmit(formData.value)
      ElMessage.success('操作成功')
      close()
      return true
    } catch (error: any) {
      ElMessage.error(error.message || '操作失败')
      return false
    } finally {
      loading.value = false
    }
  }

  return {
    visible,
    loading,
    formData,
    dialogTitle,
    width,
    open,
    close,
    submit
  }
}

export interface UseDeleteOptions {
  confirmText?: string
  successText?: string
  errorText?: string
}

export function useDelete(options: UseDeleteOptions = {}) {
  const { 
    confirmText = '确定要删除吗？', 
    successText = '删除成功',
    errorText = '删除失败'
  } = options

  const handleDelete = async (
    deleteFn: () => Promise<void>,
    onSuccess?: () => void
  ) => {
    try {
      await ElMessageBox.confirm(confirmText, '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      })

      await deleteFn()
      ElMessage.success(successText)
      onSuccess?.()
    } catch (error: any) {
      if (error !== 'cancel') {
        ElMessage.error(error.message || errorText)
      }
    }
  }

  return {
    handleDelete
  }
}
