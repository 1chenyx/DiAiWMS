<template>
  <el-dialog
    :model-value="visible"
    :title="title"
    :width="width"
    @close="handleClose"
    @update:model-value="handleClose"
  >
    <div class="sku-search">
      <el-input
        v-model="keyword"
        placeholder="请输入SKU编码或名称"
        clearable
        style="width: 300px; margin-right: 10px"
        @keyup.enter="handleSearch"
      />
      <el-button type="primary" @click="handleSearch">搜索</el-button>
    </div>
    
    <el-table
      :data="skuList"
      style="width: 100%; margin-top: 15px"
      v-loading="loading"
      @selection-change="handleSelectionChange"
    >
      <el-table-column type="selection" width="55" />
      <el-table-column prop="sku_code" label="SKU编码" width="150" />
      <el-table-column prop="sku_name" label="SKU名称" width="150" />
      <el-table-column prop="spu_name" label="SPU名称" width="150" />
      <el-table-column prop="bar_code" label="条码" width="120" />
      <el-table-column prop="weight" label="重量" width="80" />
      <el-table-column prop="volume" label="体积" width="80" />
    </el-table>
    
    <div class="pagination">
      <el-pagination
        v-model:current-page="pagination.page_index"
        v-model:page-size="pagination.page_size"
        :page-sizes="pageSizes"
        layout="total, prev, pager, next"
        :total="pagination.total"
        @current-change="handleSearch"
      />
    </div>
    
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button type="primary" @click="handleConfirm">确定选择</el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { skuService, type Sku } from '@/services/skuService'

interface Props {
  visible: boolean
  title?: string
  width?: string | number
  pageSizes?: number[]
}

const props = withDefaults(defineProps<Props>(), {
  title: '选择商品',
  width: '800px',
  pageSizes: () => [10, 20, 50]
})

const emit = defineEmits<{
  'update:visible': [value: boolean]
  'confirm': [skus: Sku[]]
}>()

const keyword = ref('')
const loading = ref(false)
const skuList = ref<Sku[]>([])
const selectedSkus = ref<Sku[]>([])

const pagination = reactive({
  page_index: 1,
  page_size: 10,
  total: 0
})

const fetchSkuList = async () => {
  loading.value = true
  try {
    const result = await skuService.getPage({
      page_index: pagination.page_index,
      page_size: pagination.page_size,
      sku_code: keyword.value || undefined,
      sku_name: keyword.value || undefined
    })
    skuList.value = result.data || []
    pagination.total = result.totals
  } catch (error: any) {
    ElMessage.error(error.message || '获取SKU列表失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.page_index = 1
  fetchSkuList()
}

const handleSelectionChange = (selection: Sku[]) => {
  selectedSkus.value = selection
}

const handleConfirm = () => {
  if (selectedSkus.value.length === 0) {
    ElMessage.warning('请至少选择一个商品')
    return
  }
  emit('confirm', selectedSkus.value)
  handleClose()
}

const handleClose = () => {
  emit('update:visible', false)
  keyword.value = ''
  selectedSkus.value = []
  pagination.page_index = 1
}

watch(() => props.visible, (val) => {
  if (val) {
    fetchSkuList()
  }
})
</script>

<style scoped>
.sku-search {
  display: flex;
  align-items: center;
}

.pagination {
  margin-top: 15px;
  display: flex;
  justify-content: flex-end;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>
