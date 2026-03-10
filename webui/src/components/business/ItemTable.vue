<template>
  <div class="item-table">
    <div class="table-header">
      <h4>{{ title }}</h4>
      <el-button type="primary" size="small" @click="handleAdd">
        <el-icon><Plus /></el-icon> {{ addButtonText }}
      </el-button>
    </div>
    
    <el-table :data="items" style="width: 100%" border>
      <el-table-column prop="sku_code" label="SKU编码" width="150" />
      <el-table-column prop="sku_name" label="SKU名称" width="150" />
      <el-table-column prop="spu_name" label="SPU名称" width="150" />
      <el-table-column prop="qty" label="数量" width="120">
        <template #default="scope">
          <el-input-number
            v-model="scope.row.qty"
            :min="1"
            :max="maxQty"
            size="small"
            style="width: 100%"
            :disabled="readonly"
          />
        </template>
      </el-table-column>
      <el-table-column v-if="showWeight" prop="weight" label="重量" width="100">
        <template #default="scope">
          <el-input-number
            v-model="scope.row.weight"
            :min="0"
            :precision="2"
            size="small"
            style="width: 100%"
            :disabled="readonly"
          />
        </template>
      </el-table-column>
      <el-table-column v-if="showVolume" prop="volume" label="体积" width="100">
        <template #default="scope">
          <el-input-number
            v-model="scope.row.volume"
            :min="0"
            :precision="2"
            size="small"
            style="width: 100%"
            :disabled="readonly"
          />
        </template>
      </el-table-column>
      <el-table-column v-if="!readonly" label="操作" width="80">
        <template #default="scope">
          <el-button type="danger" size="small" @click="handleRemove(scope.$index)">
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup lang="ts">
import { Plus } from '@element-plus/icons-vue'

interface OrderItem {
  spu_id: number
  sku_id: number
  qty: number
  weight?: number
  volume?: number
  sku_code?: string
  sku_name?: string
  spu_name?: string
}

interface Props {
  items: OrderItem[]
  title?: string
  addButtonText?: string
  showWeight?: boolean
  showVolume?: boolean
  readonly?: boolean
  maxQty?: number
}

const props = withDefaults(defineProps<Props>(), {
  title: '商品明细',
  addButtonText: '选择商品',
  showWeight: true,
  showVolume: true,
  readonly: false,
  maxQty: 999999
})

const emit = defineEmits<{
  'add': []
  'remove': [index: number]
  'update:items': [items: OrderItem[]]
}>()

const handleAdd = () => {
  emit('add')
}

const handleRemove = (index: number) => {
  emit('remove', index)
}
</script>

<style scoped>
.item-table {
  margin-top: 20px;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.table-header h4 {
  margin: 0;
  font-size: 16px;
  color: #303133;
}
</style>
