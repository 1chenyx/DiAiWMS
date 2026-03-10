<template>
  <el-tag :type="tagType" :size="size" :effect="effect">
    {{ statusText }}
  </el-tag>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface StatusMap {
  [key: number]: string
}

interface StatusTypeMap {
  [key: number]: 'success' | 'warning' | 'info' | 'danger' | 'primary' | ''
}

interface Props {
  status: number
  statusMap: StatusMap
  typeMap?: StatusTypeMap
  size?: 'large' | 'default' | 'small'
  effect?: 'dark' | 'light' | 'plain'
}

const props = withDefaults(defineProps<Props>(), {
  size: 'default',
  effect: 'light'
})

const tagType = computed(() => {
  if (props.typeMap) {
    return props.typeMap[props.status] || ''
  }
  
  const defaultTypeMap: StatusTypeMap = {
    0: 'info',
    1: 'warning',
    2: 'success',
    3: 'primary',
    4: 'danger',
    5: 'danger'
  }
  return defaultTypeMap[props.status] || ''
})

const statusText = computed(() => {
  return props.statusMap[props.status] || '未知'
})
</script>
