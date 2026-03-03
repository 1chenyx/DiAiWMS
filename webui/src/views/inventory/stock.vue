<template>
  <div class="stock-management">
    <el-card shadow="hover">
      <template #header>
        <div class="card-header">
          <span>库存查询</span>
        </div>
      </template>
      
      <!-- 搜索区域 -->
      <div class="search-section">
        <el-form :inline="true" :model="searchForm" class="search-form">
          <el-form-item label="SKU ID">
            <el-input v-model="searchForm.sku_id" placeholder="请输入SKU ID" clearable />
          </el-form-item>
          <el-form-item label="货位ID">
            <el-input v-model="searchForm.goods_location_id" placeholder="请输入货位ID" clearable />
          </el-form-item>
          <el-form-item label="是否冻结">
            <el-select v-model="searchForm.is_freeze" placeholder="请选择" clearable>
              <el-option label="否" :value="false" />
              <el-option label="是" :value="true" />
            </el-select>
          </el-form-item>
          <el-form-item label="货主ID">
            <el-input v-model="searchForm.goods_owner_id" placeholder="请输入货主ID" clearable />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleSearch">搜索</el-button>
            <el-button @click="resetSearch">重置</el-button>
          </el-form-item>
        </el-form>
      </div>
      
      <!-- 库存列表 -->
      <el-table :data="stockList" style="width: 100%" v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="sku_code" label="SKU编码" />
        <el-table-column prop="sku_name" label="SKU名称" />
        <el-table-column prop="warehouse_name" label="仓库" />
        <el-table-column prop="location_code" label="库位编码" />
        <el-table-column prop="goods_owner_name" label="货主" />
        <el-table-column prop="qty" label="库存数量" />
        <el-table-column prop="qty_available" label="可用数量" />
        <el-table-column prop="qty_frozen" label="冻结数量" />
        <el-table-column prop="is_freeze" label="是否冻结" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.is_freeze ? 'danger' : 'success'">
              {{ scope.row.is_freeze ? '是' : '否' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="batch_no" label="批次号" />
        <el-table-column prop="create_time" label="创建时间" />
        <el-table-column label="操作" fixed="right">
          <template #default="scope">
            <el-button type="primary" size="small" @click="handleViewDetail(scope.row)">
              <el-icon><View /></el-icon> 详情
            </el-button>
            <el-button 
              :type="scope.row.is_freeze ? 'success' : 'warning'" 
              size="small" 
              @click="handleToggleFreeze(scope.row)"
            >
              {{ scope.row.is_freeze ? '解冻' : '冻结' }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页 -->
      <div class="pagination">
        <el-pagination
          v-model:current-page="pagination.page_index"
          v-model:page-size="pagination.page_size"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="pagination.total"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>
    
    <!-- 库存详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="库存详情"
      width="600px"
    >
      <el-descriptions :column="2" border v-if="selectedStock">
        <el-descriptions-item label="SKU编码">{{ selectedStock.sku_code }}</el-descriptions-item>
        <el-descriptions-item label="SKU名称">{{ selectedStock.sku_name }}</el-descriptions-item>
        <el-descriptions-item label="仓库">{{ selectedStock.warehouse_name }}</el-descriptions-item>
        <el-descriptions-item label="库位编码">{{ selectedStock.location_code }}</el-descriptions-item>
        <el-descriptions-item label="货主">{{ selectedStock.goods_owner_name }}</el-descriptions-item>
        <el-descriptions-item label="库存数量">{{ selectedStock.qty }}</el-descriptions-item>
        <el-descriptions-item label="可用数量">{{ selectedStock.qty_available }}</el-descriptions-item>
        <el-descriptions-item label="冻结数量">{{ selectedStock.qty_frozen }}</el-descriptions-item>
        <el-descriptions-item label="是否冻结">
          <el-tag :type="selectedStock.is_freeze ? 'danger' : 'success'">
            {{ selectedStock.is_freeze ? '是' : '否' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="批次号">{{ selectedStock.batch_no }}</el-descriptions-item>
        <el-descriptions-item label="创建时间" :span="2">{{ selectedStock.create_time }}</el-descriptions-item>
        <el-descriptions-item label="更新时间" :span="2">{{ selectedStock.update_time }}</el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="detailDialogVisible = false">关闭</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { View } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { stockService, type Stock, type StockPageParams } from '@/services/stockService'

const loading = ref(false)

const searchForm = reactive({
  sku_id: '',
  goods_location_id: '',
  is_freeze: undefined as boolean | undefined,
  goods_owner_id: ''
})

const pagination = reactive({
  page_index: 1,
  page_size: 10,
  total: 0
})

const stockList = ref<Stock[]>([])

const detailDialogVisible = ref(false)
const selectedStock = ref<Stock | null>(null)

const fetchStockList = async () => {
  loading.value = true
  try {
    const params: StockPageParams = {
      page_index: pagination.page_index,
      page_size: pagination.page_size
    }
    
    if (searchForm.sku_id) {
      params.sku_id = parseInt(searchForm.sku_id)
    }
    if (searchForm.goods_location_id) {
      params.goods_location_id = parseInt(searchForm.goods_location_id)
    }
    if (searchForm.is_freeze !== undefined) {
      params.is_freeze = searchForm.is_freeze
    }
    if (searchForm.goods_owner_id) {
      params.goods_owner_id = parseInt(searchForm.goods_owner_id)
    }
    
    const result = await stockService.getPage(params)
    stockList.value = result.data
    pagination.total = result.totals
  } catch (error: any) {
    ElMessage.error(error.message || '获取库存列表失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.page_index = 1
  fetchStockList()
}

const resetSearch = () => {
  searchForm.sku_id = ''
  searchForm.goods_location_id = ''
  searchForm.is_freeze = undefined
  searchForm.goods_owner_id = ''
  pagination.page_index = 1
  fetchStockList()
}

const handleSizeChange = (size: number) => {
  pagination.page_size = size
  fetchStockList()
}

const handleCurrentChange = (current: number) => {
  pagination.page_index = current
  fetchStockList()
}

const handleViewDetail = async (row: Stock) => {
  try {
    const result = await stockService.getById(row.id)
    selectedStock.value = result
    detailDialogVisible.value = true
  } catch (error: any) {
    ElMessage.error(error.message || '获取详情失败')
  }
}

const handleToggleFreeze = async (row: Stock) => {
  const action = row.is_freeze ? '解冻' : '冻结'
  try {
    await ElMessageBox.confirm(`确定要${action}这个库存吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await stockService.update(row.id, { is_freeze: !row.is_freeze })
    ElMessage.success(`${action}成功`)
    fetchStockList()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || `${action}失败`)
    }
  }
}

onMounted(() => {
  fetchStockList()
})
</script>

<style scoped>
.stock-management {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.search-section {
  margin-bottom: 20px;
}

.search-form {
  display: flex;
  flex-wrap: wrap;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>
