<template>
  <el-dialog
    v-model="visible"
    :title="title"
    :width="width"
    :close-on-click-modal="false"
    class="form-dialog"
    @close="handleClose"
  >
    <el-form 
      ref="formRef" 
      :model="formData" 
      :rules="rules" 
      :label-width="labelWidth"
      class="form-content"
    >
      <slot name="form"></slot>
    </el-form>
    
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose" size="large">
          取消
        </el-button>
        <el-button 
          type="primary" 
          @click="handleSubmit" 
          :loading="loading"
          size="large"
        >
          确定
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'

interface Props {
  visible: boolean
  title: string
  formData: Record<string, any>
  rules?: FormRules
  loading?: boolean
  width?: string | number
  labelWidth?: string
}

const props = withDefaults(defineProps<Props>(), {
  visible: false,
  title: '对话框',
  formData: () => ({}),
  rules: () => ({}),
  loading: false,
  width: '600px',
  labelWidth: '100px'
})

const emit = defineEmits<{
  'update:visible': [value: boolean]
  'update:formData': [value: Record<string, any>]
  'submit': [data: Record<string, any>]
  'close': []
}>()

const formRef = ref<FormInstance>()

const handleClose = () => {
  emit('update:visible', false)
  emit('close')
}

const handleSubmit = async () => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()
    emit('submit', props.formData)
  } catch (error) {
    console.error('表单验证失败:', error)
  }
}

watch(() => props.visible, (val) => {
  if (!val) {
    formRef.value?.resetFields()
  }
})
</script>

<style scoped>
.form-dialog {
  border-radius: var(--radius-xl);
}

:deep(.el-dialog) {
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-modal);
  overflow: hidden;
}

:deep(.el-dialog__header) {
  padding: 24px 32px;
  border-bottom: 1px solid var(--color-border-primary);
  background: var(--color-bg-secondary);
}

:deep(.el-dialog__title) {
  font-size: 20px;
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
}

:deep(.el-dialog__headerbtn) {
  top: 24px;
  right: 32px;
  width: 32px;
  height: 32px;
  border-radius: var(--radius-base);
  transition: all var(--duration-fast) var(--ease-in-out);
}

:deep(.el-dialog__headerbtn:hover) {
  background: var(--color-bg-tertiary);
}

:deep(.el-dialog__body) {
  padding: 32px;
  max-height: 60vh;
  overflow-y: auto;
}

:deep(.el-dialog__footer) {
  padding: 20px 32px;
  border-top: 1px solid var(--color-border-primary);
  background: var(--color-bg-secondary);
}

.form-content {
  width: 100%;
}

:deep(.el-form-item__label) {
  font-weight: var(--font-weight-medium);
  color: var(--color-text-secondary);
}

:deep(.el-input__wrapper),
:deep(.el-select__wrapper),
:deep(.el-textarea__inner) {
  border-radius: var(--radius-base);
  transition: all var(--duration-fast) var(--ease-in-out);
}

:deep(.el-input__wrapper:hover),
:deep(.el-select__wrapper:hover),
:deep(.el-textarea__inner:hover) {
  box-shadow: 0 0 0 1px var(--color-primary) inset;
}

:deep(.el-input__wrapper.is-focus),
:deep(.el-select__wrapper.is-focus),
:deep(.el-textarea__inner:focus) {
  box-shadow: 0 0 0 2px var(--color-primary) inset;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.dialog-footer .el-button {
  min-width: 100px;
  border-radius: var(--radius-base);
  font-weight: var(--font-weight-medium);
}

@media (max-width: 768px) {
  :deep(.el-dialog) {
    width: 90% !important;
    margin-top: 5vh !important;
  }
  
  :deep(.el-dialog__body) {
    padding: 24px 20px;
  }
}
</style>
