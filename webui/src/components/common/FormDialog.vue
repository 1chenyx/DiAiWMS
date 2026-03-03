<template>
  <el-dialog
    v-model="visible"
    :title="title"
    :width="width"
    :close-on-click-modal="false"
    @close="handleClose"
  >
    <el-form 
      ref="formRef" 
      :model="formData" 
      :rules="rules" 
      :label-width="labelWidth"
    >
      <slot name="form"></slot>
    </el-form>
    
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="loading">
          确定
        </el-button>
      </span>
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
.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>
