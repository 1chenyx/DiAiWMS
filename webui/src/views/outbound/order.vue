<template>
  <div class="outbound-order-management">
    <el-card shadow="hover">
      <template #header>
        <div class="card-header">
          <span>出库订单管理</span>
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon> 添加出库订单
          </el-button>
        </div>
      </template>
      
      <div class="search-section">
        <el-form :inline="true" :model="searchForm" class="search-form">
          <el-form-item label="订单号">
            <el-input v-model="searchForm.order_no" placeholder="请输入订单号" clearable />
          </el-form-item>
          <el-form-item label="状态">
            <el-select v-model="searchForm.order_status" placeholder="请选择状态" clearable>
              <el-option label="待处理" :value="0" />
              <el-option label="已生成上架单" :value="1" />
              <el-option label="已取消" :value="2" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleSearch">搜索</el-button>
            <el-button @click="resetSearch">重置</el-button>
          </el-form-item>
        </el-form>
      </div>
      
      <el-table :data="orderList" style="width: 100%" v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="order_no" label="订单号" />
        <el-table-column prop="customer_name" label="客户" />
        <el-table-column prop="warehouse_name" label="仓库" />
        <el-table-column prop="total_qty" label="总数量" />
        <el-table-column prop="total_weight" label="总重量" />
        <el-table-column prop="total_volume" label="总体积" />
        <el-table-column prop="order_status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.order_status)">
              {{ getStatusText(scope.row.order_status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="remark" label="备注" />
        <el-table-column prop="create_time" label="创建时间" />
        <el-table-column label="操作" fixed="right" width="200">
          <template #default="scope">
            <el-button type="primary" size="small" @click="handleViewDetail(scope.row)">
              <el-icon><View /></el-icon> 详情
            </el-button>
            <el-button type="danger" size="small" @click="handleDelete(scope.row.id)">
              <el-icon><Delete /></el-icon> 删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
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
    
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="900px">
      <el-form ref="formRef" :model="formData" :rules="formRules" label-width="100px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="客户" prop="customer_id">
              <el-select v-model="formData.customer_id" placeholder="请选择客户" style="width: 100%">
                <el-option 
                  v-for="customer in customerList" 
                  :key="customer.id" 
                  :label="customer.customer_name" 
                  :value="customer.id" 
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="仓库" prop="warehouse_id">
              <el-select v-model="formData.warehouse_id" placeholder="请选择仓库" style="width: 100%">
                <el-option 
                  v-for="warehouse in warehouseList" 
                  :key="warehouse.id" 
                  :label="warehouse.node_name" 
                  :value="warehouse.id" 
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="货主ID" prop="goods_owner_id">
              <el-input-number v-model="formData.goods_owner_id" :min="0" placeholder="请输入货主ID" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="货主名称" prop="goods_owner_name">
              <el-input v-model="formData.goods_owner_name" placeholder="请输入货主名称" clearable />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="备注" prop="remark">
          <el-input v-model="formData.remark" placeholder="请输入备注" type="textarea" />
        </el-form-item>
        
        <div class="items-header">
          <h4>商品明细</h4>
          <el-button type="primary" size="small" @click="openSkuDialog">
            <el-icon><Plus /></el-icon> 选择商品
          </el-button>
        </div>
        <el-table :data="formData.items" style="width: 100%" border>
          <el-table-column prop="sku_code" label="SKU编码" />
          <el-table-column prop="sku_name" label="SKU名称" />
          <el-table-column prop="spu_name" label="SPU名称" />
          <el-table-column prop="qty" label="数量" width="120">
            <template #default="scope">
              <el-input-number v-model="scope.row.qty" :min="1" size="small" style="width: 100%" />
            </template>
          </el-table-column>
          <el-table-column prop="weight" label="重量" width="100">
            <template #default="scope">
              <el-input-number v-model="scope.row.weight" :min="0" :precision="2" size="small" style="width: 100%" />
            </template>
          </el-table-column>
          <el-table-column prop="volume" label="体积" width="100">
            <template #default="scope">
              <el-input-number v-model="scope.row.volume" :min="0" :precision="2" size="small" style="width: 100%" />
            </template>
          </el-table-column>
          <el-table-column prop="price" label="价格" width="100">
            <template #default="scope">
              <el-input-number v-model="scope.row.price" :min="0" :precision="2" size="small" style="width: 100%" placeholder="可选" />
            </template>
          </el-table-column>
          <el-table-column prop="batch_no" label="批次号" width="120">
            <template #default="scope">
              <el-input v-model="scope.row.batch_no" size="small" placeholder="可选" />
            </template>
          </el-table-column>
          <el-table-column prop="goods_location_id" label="库位ID" width="100">
            <template #default="scope">
              <el-input-number v-model="scope.row.goods_location_id" :min="0" size="small" style="width: 100%" placeholder="可选" />
            </template>
          </el-table-column>
          <el-table-column label="操作" width="80">
            <template #default="scope">
              <el-button type="danger" size="small" @click="removeItem(scope.$index)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmit" :loading="submitting">确定</el-button>
        </span>
      </template>
    </el-dialog>
    
    <el-dialog v-model="skuDialogVisible" title="选择商品" width="800px">
      <div class="sku-search">
        <el-input v-model="skuSearchForm.keyword" placeholder="请输入SKU编码或名称" clearable style="width: 300px; margin-right: 10px" />
        <el-button type="primary" @click="searchSku">搜索</el-button>
      </div>
      <el-table 
        :data="skuList" 
        style="width: 100%; margin-top: 15px" 
        v-loading="skuLoading"
        @selection-change="handleSkuSelection"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="sku_code" label="SKU编码" />
        <el-table-column prop="sku_name" label="SKU名称" />
        <el-table-column prop="spu_name" label="SPU名称" />
        <el-table-column prop="bar_code" label="条码" />
      </el-table>
      <div class="sku-pagination">
        <el-pagination
          v-model:current-page="skuPagination.page_index"
          v-model:page-size="skuPagination.page_size"
          :page-sizes="[10, 20, 50]"
          layout="total, prev, pager, next"
          :total="skuPagination.total"
          @current-change="searchSku"
        />
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="skuDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="confirmSkuSelection">确定选择</el-button>
        </span>
      </template>
    </el-dialog>
    
    <el-dialog v-model="detailDialogVisible" title="出库订单详情" width="800px">
      <div class="order-detail" v-if="selectedOrder">
        <el-descriptions :column="2" border class="order-header">
          <el-descriptions-item label="订单号">{{ selectedOrder.order_no }}</el-descriptions-item>
          <el-descriptions-item label="状态">{{ getStatusText(selectedOrder.order_status) }}</el-descriptions-item>
          <el-descriptions-item label="客户">{{ selectedOrder.customer_name }}</el-descriptions-item>
          <el-descriptions-item label="仓库">{{ selectedOrder.warehouse_name }}</el-descriptions-item>
          <el-descriptions-item label="总数量">{{ selectedOrder.total_qty }}</el-descriptions-item>
          <el-descriptions-item label="总重量">{{ selectedOrder.total_weight }}</el-descriptions-item>
          <el-descriptions-item label="总体积">{{ selectedOrder.total_volume }}</el-descriptions-item>
          <el-descriptions-item label="备注">{{ selectedOrder.remark }}</el-descriptions-item>
          <el-descriptions-item label="创建时间" :span="2">{{ selectedOrder.create_time }}</el-descriptions-item>
        </el-descriptions>
        <div v-if="selectedOrder.items && selectedOrder.items.length > 0">
          <h4>商品明细</h4>
          <el-table :data="selectedOrder.items" style="width: 100%" border>
            <el-table-column prop="sku_code" label="SKU编码" />
            <el-table-column prop="sku_name" label="SKU名称" />
            <el-table-column prop="spu_name" label="SPU名称" />
            <el-table-column prop="qty" label="数量" />
            <el-table-column prop="weight" label="重量" />
            <el-table-column prop="volume" label="体积" />
          </el-table>
        </div>
      </div>
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
import { Plus, View, Delete } from '@element-plus/icons-vue'
import { ElMessageBox, ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { outboundOrderService, type OutboundOrderViewModel, type OutboundOrderItem } from '@/services/outboundOrderService'
import { customerService, type Customer } from '@/services/customerService'
import { warehouseLocationService, type WarehouseLocation } from '@/services/warehouseLocationService'
import { skuService, type Sku } from '@/services/skuService'

const loading = ref(false)
const submitting = ref(false)

const searchForm = reactive({
  order_no: '',
  order_status: undefined as number | undefined
})

const pagination = reactive({
  page_index: 1,
  page_size: 10,
  total: 0
})

const orderList = ref<OutboundOrderViewModel[]>([])
const customerList = ref<Customer[]>([])
const warehouseList = ref<WarehouseLocation[]>([])

const dialogVisible = ref(false)
const dialogTitle = ref('添加出库订单')
const formRef = ref<FormInstance>()

interface OrderItemWithSku extends OutboundOrderItem {
  sku_code?: string
  sku_name?: string
  spu_name?: string
  spu_id?: number
}

const formData = reactive({
  id: 0,
  customer_id: undefined as number | undefined,
  customer_name: '',
  warehouse_id: undefined as number | undefined,
  goods_owner_id: 0,
  goods_owner_name: '',
  remark: '',
  items: [] as OrderItemWithSku[]
})

const formRules = reactive<FormRules>({
  customer_id: [{ required: true, message: '请选择客户', trigger: 'change' }],
  warehouse_id: [{ required: true, message: '请选择仓库', trigger: 'change' }]
})

const detailDialogVisible = ref(false)
const selectedOrder = ref<OutboundOrderViewModel | null>(null)

const skuDialogVisible = ref(false)
const skuLoading = ref(false)
const skuList = ref<Sku[]>([])
const skuSearchForm = reactive({ keyword: '' })
const skuPagination = reactive({ page_index: 1, page_size: 10, total: 0 })
const selectedSkus = ref<Sku[]>([])

const fetchOrderList = async () => {
  loading.value = true
  try {
    const result = await outboundOrderService.getPage({
      page_index: pagination.page_index,
      page_size: pagination.page_size,
      order_no: searchForm.order_no || undefined,
      order_status: searchForm.order_status
    })
    orderList.value = result.rows || []
    pagination.total = result.totals
  } catch (error: any) {
    ElMessage.error(error.message || '获取出库订单列表失败')
  } finally {
    loading.value = false
  }
}

const fetchCustomers = async () => {
  try {
    const result = await customerService.getAll()
    customerList.value = result
  } catch (error: any) {
    console.error('获取客户列表失败:', error)
  }
}

const fetchWarehouses = async () => {
  try {
    const result = await warehouseLocationService.getAll(1)
    warehouseList.value = result
  } catch (error: any) {
    console.error('获取仓库列表失败:', error)
  }
}

const handleSearch = () => {
  pagination.page_index = 1
  fetchOrderList()
}

const resetSearch = () => {
  searchForm.order_no = ''
  searchForm.order_status = undefined
  pagination.page_index = 1
  fetchOrderList()
}

const handleSizeChange = (size: number) => {
  pagination.page_size = size
  fetchOrderList()
}

const handleCurrentChange = (current: number) => {
  pagination.page_index = current
  fetchOrderList()
}

const handleAdd = () => {
  dialogTitle.value = '添加出库订单'
  formData.id = 0
  formData.customer_id = undefined
  formData.customer_name = ''
  formData.warehouse_id = undefined
  formData.goods_owner_id = 0
  formData.goods_owner_name = ''
  formData.remark = ''
  formData.items = []
  dialogVisible.value = true
}

const openSkuDialog = () => {
  skuSearchForm.keyword = ''
  skuPagination.page_index = 1
  selectedSkus.value = []
  searchSku()
  skuDialogVisible.value = true
}

const searchSku = async () => {
  skuLoading.value = true
  try {
    const result = await skuService.getPage({
      page_index: skuPagination.page_index,
      page_size: skuPagination.page_size,
      sku_code: skuSearchForm.keyword || undefined,
      sku_name: skuSearchForm.keyword || undefined
    })
    skuList.value = result.data || []
    skuPagination.total = result.totals
  } catch (error: any) {
    ElMessage.error(error.message || '获取SKU列表失败')
  } finally {
    skuLoading.value = false
  }
}

const handleSkuSelection = (selection: Sku[]) => {
  selectedSkus.value = selection
}

const confirmSkuSelection = () => {
  if (selectedSkus.value.length === 0) {
    ElMessage.warning('请至少选择一个商品')
    return
  }
  
  selectedSkus.value.forEach(sku => {
    const exists = formData.items.find(item => item.sku_id === sku.id)
    if (!exists) {
      formData.items.push({
        spu_id: sku.spu_id || 0,
        sku_id: sku.id,
        qty: 1,
        weight: 0,
        volume: 0,
        price: undefined,
        expiry_date: 0,
        batch_no: undefined,
        production_date: undefined,
        goods_location_id: 0,
        sku_code: sku.sku_code,
        sku_name: sku.sku_name,
        spu_name: sku.spu_name
      })
    }
  })
  
  skuDialogVisible.value = false
  ElMessage.success(`已添加 ${selectedSkus.value.length} 个商品`)
}

const removeItem = (index: number) => {
  formData.items.splice(index, 1)
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  if (formData.items.length === 0) {
    ElMessage.warning('请至少添加一个商品明细')
    return
  }
  
  try {
    await formRef.value.validate()
    submitting.value = true
    
    const items = formData.items.map(item => ({
      spu_id: item.spu_id || 0,
      sku_id: item.sku_id,
      qty: item.qty,
      weight: item.weight || 0,
      volume: item.volume || 0,
      price: item.price || undefined,
      expiry_date: item.expiry_date || 0,
      batch_no: item.batch_no || undefined,
      production_date: item.production_date || undefined,
      goods_location_id: item.goods_location_id || 0
    }))
    
    await outboundOrderService.create({
      customer_id: formData.customer_id!,
      customer_name: formData.customer_name || undefined,
      warehouse_id: formData.warehouse_id!,
      goods_owner_id: formData.goods_owner_id || 0,
      goods_owner_name: formData.goods_owner_name || undefined,
      remark: formData.remark,
      items
    })
    
    ElMessage.success('创建成功')
    dialogVisible.value = false
    fetchOrderList()
  } catch (error: any) {
    ElMessage.error(error.message || '操作失败')
  } finally {
    submitting.value = false
  }
}

const handleViewDetail = async (row: OutboundOrderViewModel) => {
  try {
    const result = await outboundOrderService.getById(row.id)
    selectedOrder.value = result
    detailDialogVisible.value = true
  } catch (error: any) {
    ElMessage.error(error.message || '获取详情失败')
  }
}

const handleDelete = async (id: number) => {
  try {
    await ElMessageBox.confirm('确定要删除这个出库订单吗？', '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await outboundOrderService.delete(id)
    ElMessage.success('删除成功')
    fetchOrderList()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '删除失败')
    }
  }
}

const getStatusType = (status: number) => {
  switch (status) {
    case 0: return 'info'
    case 1: return 'warning'
    case 2: return 'danger'
    default: return ''
  }
}

const getStatusText = (status: number) => {
  switch (status) {
    case 0: return '待处理'
    case 1: return '已生成上架单'
    case 2: return '已取消'
    default: return ''
  }
}

onMounted(() => {
  fetchOrderList()
  fetchCustomers()
  fetchWarehouses()
})
</script>

<style scoped>
.outbound-order-management { padding: 20px }
.card-header { display: flex; justify-content: space-between; align-items: center }
.search-section { margin-bottom: 20px }
.search-form { display: flex; flex-wrap: wrap }
.pagination { margin-top: 20px; display: flex; justify-content: flex-end }
.dialog-footer { display: flex; justify-content: flex-end; gap: 10px }
.order-detail { padding: 10px 0 }
.order-header { margin-bottom: 20px }
.items-header { display: flex; justify-content: space-between; align-items: center; margin: 20px 0 15px 0 }
.items-header h4 { margin: 0; font-size: 16px; color: #303133 }
.sku-search { display: flex; align-items: center }
.sku-pagination { margin-top: 15px; display: flex; justify-content: flex-end }
</style>
