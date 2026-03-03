import { ref } from 'vue'
import { ElMessage } from 'element-plus'

export interface UseFormOptions<T> {
  defaultData?: () => T
  validate?: (data: T) => boolean | Promise<boolean>
  submit?: (data: T) => Promise<void>
}

export function useForm<T extends Record<string, any>>(options: UseFormOptions<T> = {}) {
  const { defaultData, validate, submit } = options

  const formData = ref<T>({} as T)
  const loading = ref(false)
  const errors = ref<Record<string, string>>({})

  const reset = () => {
    if (defaultData) {
      formData.value = defaultData()
    } else {
      formData.value = {} as T
    }
    errors.value = {}
  }

  const setField = (key: keyof T, value: any) => {
    formData.value[key] = value
    if (errors.value[key as string]) {
      delete errors.value[key as string]
    }
  }

  const setFields = (data: Partial<T>) => {
    Object.assign(formData.value, data)
    Object.keys(data).forEach(key => {
      if (errors.value[key]) {
        delete errors.value[key]
      }
    })
  }

  const validateForm = async (): Promise<boolean> => {
    errors.value = {}
    
    if (validate) {
      try {
        const isValid = await validate(formData.value)
        if (!isValid) {
          return false
        }
      } catch (error: any) {
        if (error.errors) {
          errors.value = error.errors
        } else {
          ElMessage.error(error.message || '验证失败')
        }
        return false
      }
    }
    
    return true
  }

  const handleSubmit = async (onSuccess?: () => void) => {
    if (!submit) return false

    const isValid = await validateForm()
    if (!isValid) return false

    loading.value = true
    try {
      await submit(formData.value)
      ElMessage.success('提交成功')
      onSuccess?.()
      return true
    } catch (error: any) {
      ElMessage.error(error.message || '提交失败')
      return false
    } finally {
      loading.value = false
    }
  }

  return {
    formData,
    loading,
    errors,
    reset,
    setField,
    setFields,
    validateForm,
    handleSubmit
  }
}
