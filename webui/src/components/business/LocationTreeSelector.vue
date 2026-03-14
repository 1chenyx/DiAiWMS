<template>
  <el-select
    v-model="selectedValue"
    :placeholder="placeholder"
    :filterable="filterable"
    :disabled="disabled"
    :clearable="clearable"
    style="width: 100%"
    @change="handleChange"
  >
    <el-option
      v-for="node in flatTreeData"
      :key="node.id"
      :label="node.label"
      :value="node.id"
      :disabled="node.disabled"
    >
      <div 
        class="tree-node" 
        :style="{ paddingLeft: (node.level * 20) + 'px' }"
        @click="handleNodeClick(node, $event)"
      >
        <span v-if="node.children && node.children.length > 0" class="expand-icon" @click.stop="toggleExpand(node.id)">
          {{ expandedNodes.has(node.id) ? '▼' : '▶' }}
        </span>
        <span class="node-label">{{ node.label }}</span>
      </div>
    </el-option>
  </el-select>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
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
const flatTreeData = ref<any[]>([])
const expandedNodes = ref<Set<number>>(new Set())

interface FlatNode {
  id: number
  label: string
  level: number
  disabled: boolean
  nodeType: number
  children?: any[]
  parentId?: number
}

const flattenTree = (nodes: any[], level: number = 0, parentId?: number): FlatNode[] => {
  const result: FlatNode[] = []
  for (const node of nodes) {
    const isDisabled = props.nodeType ? node.node_type !== props.nodeType : false
    const flatNode: FlatNode = {
      id: node.id,
      label: node.node_name,
      level,
      disabled: isDisabled,
      nodeType: node.node_type,
      children: node.children,
      parentId
    }
    result.push(flatNode)
    
    if (node.children && node.children.length > 0 && expandedNodes.value.has(node.id)) {
      result.push(...flattenTree(node.children, level + 1, node.id))
    }
  }
  return result
}

const toggleExpand = (nodeId: number) => {
  if (expandedNodes.value.has(nodeId)) {
    expandedNodes.value.delete(nodeId)
  } else {
    expandedNodes.value.add(nodeId)
  }
  updateFlatTreeData()
}

const updateFlatTreeData = () => {
  flatTreeData.value = flattenTree(treeData.value)
}

const handleNodeClick = (node: FlatNode, event: Event) => {
  if (node.children && node.children.length > 0) {
    event.stopPropagation()
    toggleExpand(node.id)
  }
}

const fetchTreeData = async () => {
  if (!props.warehouseId) return
  
  try {
    const result = await warehouseLocationService.getTreeByWarehouse(props.warehouseId)
    treeData.value = [result]
    updateFlatTreeData()
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
  if (value && treeData.value.length > 0) {
    const locationInfo = findLocationInfo(treeData.value, value)
    
    if (locationInfo && props.nodeType && locationInfo.node_type !== props.nodeType) {
      ElMessage.warning('请选择三级库位')
      selectedValue.value = undefined
      emit('update:modelValue', undefined)
      emit('change', undefined, null)
      return
    }
    
    emit('update:modelValue', value)
    
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
    emit('update:modelValue', value)
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

<style scoped>
.tree-node {
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: 4px 0;
}

.expand-icon {
  margin-right: 4px;
  font-size: 12px;
  color: #909399;
  width: 12px;
  text-align: center;
}

.node-label {
  flex: 1;
}
</style>
