<template>
  <div class="search-form">
    <el-form :inline="true" :model="formData" class="form-inline">
      <el-form-item 
        v-for="item in items" 
        :key="item.prop" 
        :label="item.label"
      >
        <el-input 
          v-if="item.type === 'input'"
          v-model="formData[item.prop]" 
          :placeholder="item.placeholder || `请输入${item.label}`"
          :clearable="item.clearable !== false"
          @keyup.enter="handleSearch"
        />
        <el-select 
          v-else-if="item.type === 'select'"
          v-model="formData[item.prop]"
          :placeholder="item.placeholder || `请选择${item.label}`"
          :clearable="item.clearable !== false"
          style="width: 200px"
        >
          <el-option 
            v-for="option in item.options" 
            :key="option.value" 
            :label="option.label" 
            :value="option.value"
            :disabled="option.disabled"
          />
        </el-select>
        <el-input-number 
          v-else-if="item.type === 'number'"
          v-model="formData[item.prop]"
          :placeholder="item.placeholder || `请输入${item.label}`"
          :min="0"
          style="width: 200px"
        />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="handleSearch">搜索</el-button>
        <el-button @click="handleReset">重置</el-button>
        <slot name="actions"></slot>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup lang="ts">
import { reactive } from 'vue'
import type { SearchFormItem, SelectOption } from '@/types/common'

interface Props {
  items: SearchFormItem[]
  modelValue: Record<string, any>
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'update:modelValue': [value: Record<string, any>]
  'search': [params: Record<string, any>]
  'reset': []
}>()

const formData = reactive<Record<string, any>>(props.modelValue)

const handleSearch = () => {
  emit('update:modelValue', formData)
  emit('search', formData)
}

const handleReset = () => {
  Object.keys(formData).forEach(key => {
    formData[key] = ''
  })
  emit('update:modelValue', formData)
  emit('reset')
}
</script>

<style scoped>
.search-form {
  padding: 10px 0;
}

.form-inline {
  display: flex;
  flex-wrap: wrap;
}
</style>
