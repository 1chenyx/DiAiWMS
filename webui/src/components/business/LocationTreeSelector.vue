<template>
  <el-tree-select
    v-model="selectedValue"
    :data="treeData"
    :props="treeProps"
    :placeholder="placeholder"
    :filterable="filterable"
    :check-strictly="checkStrictly"
    :disabled="disabled"
    :clearable="clearable"
    style="width: 100%"
    @update:model-value="handleChange"
  />
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { warehouseLocationService, type WarehouseLocationTreeNode } from '@/services/warehouseLocationService'

interface Props {
  modelValue?: number
  warehouseId?: number
  placeholder?: string
  filterable?: boolean
  checkStrictly?: boolean
  disabled?: boolean
  clearable?: boolean
  nodeType?: number
}

const props = withDefaults(defineProps<Props>(), {
  placeholder: '请选择库位',
  filterable: true,
  checkStrictly: true,
  disabled: false,
  clearable: true,
  nodeType: 3
})

const emit = defineEmits<{
  'update:modelValue': [value: number | undefined]
  'change': [value: number | undefined, info: LocationInfo | null]
}>()

interface LocationInfo {
  warehouseId: number
  warehouseName: string
  areaId: number
  areaName: string
}

const selectedValue = ref<number | undefined>(props.modelValue)
const treeData = ref<WarehouseLocationTreeNode[]>([])

const treeProps = {
  value: 'id',
  label: 'node_name',
  children: 'children',
  disabled: (data: any) => {
    return props.nodeType ? data.node_type !== props.nodeType : false
  }
}

const fetchTreeData = async () => {
  if (!props.warehouseId) return
  
  try {
    const result = await warehouseLocationService.getTreeByWarehouse(props.warehouseId)
    treeData.value = [result]
  } catch (error) {
    console.error('获取库位树失败:', error)
  }
}

const findLocationInfo = (nodes: any[], id: number, path: any[] = []): any => {
  for (const node of nodes) {
    if (node.id === id) {
      return { ...node, path }
    }
    if (node.children && node.children.length > 0) {
      const result = findLocationInfo(node.children, id, [...path, node])
      if (result) return result
    }
  }
  return null
}

const handleChange = (value: number | undefined) => {
  emit('update:modelValue', value)
  
  if (value && treeData.value.length > 0) {
    const locationInfo = findLocationInfo(treeData.value, value)
    
    if (locationInfo) {
      const path = locationInfo.path || []
      let warehouseId = 0
      let warehouseName = ''
      let areaId = 0
      let areaName = ''
      
      for (const node of path) {
        if (node.node_type === 1) {
          warehouseId = node.id
          warehouseName = node.node_name
        } else if (node.node_type === 2) {
          areaId = node.id
          areaName = node.node_name
        }
      }
      
      emit('change', value, {
        warehouseId,
        warehouseName,
        areaId,
        areaName
      })
    } else {
      emit('change', value, null)
    }
  } else {
    emit('change', value, null)
  }
}

watch(() => props.modelValue, (val) => {
  selectedValue.value = val
})

watch(() => props.warehouseId, () => {
  fetchTreeData()
}, { immediate: true })
</script>
