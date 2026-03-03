<template>
  <div class="outbound-receipt-management">
    <el-card shadow="hover">
      <template #header>
        <div class="card-header">
          <span>出库单管理</span>
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon> 创建出库单
          </el-button>
        </div>
      </template>
      
      <div class="search-section">
        <el-form :inline="true" :model="searchForm" class="search-form">
          <el-form-item label="出库单号">
            <el-input v-model="searchForm.receipt_no" placeholder="请输入出库单号" clearable />
          </el-form-item>
          <el-form-item label="出库订单号">
            <el-input v-model="searchForm.order_no" placeholder="请输入出库订单号" clearable />
          </el-form-item>
          <el-form-item label="状态">
            <el-select v-model="searchForm.receipt_status" placeholder="请选择状态" clearable>
              <el-option label="待出库" :value="1" />
              <el-option label="已出库" :value="2" />
              <el-option label="已取消" :value="3" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleSearch">搜索</el-button>
            <el-button @click="resetSearch">重置</el-button>
          </el-form-item>
        </el-form>
      </div>
      
      <el-table :data="receiptList" style="width: 100%" v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="receipt_no" label="出库单号" />
        <el-table-column prop="pick_putaway_no" label="拣货单号" />
        <el-table-column prop="order_no" label="出库订单号" />
        <el-table-column prop="customer_name" label="客户" />
        <el-table-column prop="warehouse_name" label="仓库" />
        <el-table-column prop="total_qty" label="总数量" />
        <el-table-column prop="receipt_status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.receipt_status)">
              {{ getStatusText(scope.row.receipt_status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="outbound_person" label="出库人" />
        <el-table-column prop="outbound_time" label="出库时间" />
        <el-table-column prop="create_time" label="创建时间" />
        <el-table-column label="操作" fixed="right" width="280">
          <template #default="scope">
            <el-button type="primary" size="small" @click="handleViewDetail(scope.row)">
              <el-icon><View /></el-icon> 详情
            </el-button>
            <el-button v-if="scope.row.receipt_status === 1" type="success" size="small" @click="handleCompleteOutbound(scope.row)">
              <el-icon><Check /></el-icon> 完成出库
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
    
    <el-dialog v-model="dialogVisible" title="创建出库单" width="600px">
      <el-form ref="formRef" :model="formData" :rules="formRules" label-width="120px">
        <el-form-item label="拣货单" prop="outbound_pick_putaway_id">
          <el-select v-model="formData.outbound_pick_putaway_id" placeholder="请选择拣货单" style="width: 100%" filterable>
            <el-option 
              v-for="pp in pickPutawayList" 
              :key="pp.id" 
              :label="`${pp.pick_putaway_no} - ${pp.order_no}`" 
              :value="pp.id" 
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmit" :loading="submitting">确定</el-button>
        </span>
      </template>
    </el-dialog>
    
    <el-dialog v-model="detailDialogVisible" title="出库单详情" width="1000px">
      <div class="receipt-detail" v-if="selectedReceipt">
        <el-descriptions :column="2" border class="receipt-header">
          <el-descriptions-item label="出库单号">{{ selectedReceipt.receipt_no }}</el-descriptions-item>
          <el-descriptions-item label="状态">{{ getStatusText(selectedReceipt.receipt_status) }}</el-descriptions-item>
          <el-descriptions-item label="拣货单号">{{ selectedReceipt.pick_putaway_no }}</el-descriptions-item>
          <el-descriptions-item label="出库订单号">{{ selectedReceipt.order_no }}</el-descriptions-item>
          <el-descriptions-item label="客户">{{ selectedReceipt.customer_name }}</el-descriptions-item>
          <el-descriptions-item label="仓库">{{ selectedReceipt.warehouse_name }}</el-descriptions-item>
          <el-descriptions-item label="总数量">{{ selectedReceipt.total_qty }}</el-descriptions-item>
          <el-descriptions-item label="出库人">{{ selectedReceipt.outbound_person }}</el-descriptions-item>
          <el-descriptions-item label="出库时间">{{ selectedReceipt.outbound_time }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ selectedReceipt.create_time }}</el-descriptions-item>
        </el-descriptions>
        
        <div v-if="selectedReceipt.items && selectedReceipt.items.length > 0">
          <h4>商品明细</h4>
          <el-table :data="selectedReceipt.items" style="width: 100%" border>
            <el-table-column prop="sku_code" label="SKU编码" />
            <el-table-column prop="sku_name" label="SKU名称" />
            <el-table-column prop="spu_name" label="SPU名称" />
            <el-table-column prop="qty" label="数量" />
            <el-table-column prop="location_name" label="库位" />
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
import { Plus, View, Delete, Check } from '@element-plus/icons-vue'
import { ElMessageBox, ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { outboundReceiptService, type OutboundReceiptViewModel, type OutboundReceiptCreate } from '@/services/outboundReceiptService'
import { outboundPickPutawayService, type OutboundPickPutawayViewModel } from '@/services/outboundPickPutawayService'
import { useUserStore } from '@/store/user'

const loading = ref(false)
const submitting = ref(false)

const searchForm = reactive({
  receipt_no: '',
  order_no: '',
  receipt_status: undefined as number | undefined
})

const pagination = reactive({
  page_index: 1,
  page_size: 10,
  total: 0
})

const receiptList = ref<OutboundReceiptViewModel[]>([])
const pickPutawayList = ref<OutboundPickPutawayViewModel[]>([])

const dialogVisible = ref(false)
const formRef = ref<FormInstance>()
const formData = reactive({
  outbound_pick_putaway_id: undefined as number | undefined
})

const formRules = reactive<FormRules>({
  outbound_pick_putaway_id: [{ required: true, message: '请选择拣货单', trigger: 'change' }]
})

const detailDialogVisible = ref(false)
const selectedReceipt = ref<OutboundReceiptViewModel | null>(null)
const userStore = useUserStore()

const fetchReceiptList = async () => {
  loading.value = true
  try {
    const result = await outboundReceiptService.getPage({
      page_index: pagination.page_index,
      page_size: pagination.page_size,
      receipt_no: searchForm.receipt_no || undefined,
      order_no: searchForm.order_no || undefined,
      receipt_status: searchForm.receipt_status
    })
    receiptList.value = result.rows
    pagination.total = result.totals
  } catch (error: any) {
    ElMessage.error(error.message || '获取出库单列表失败')
  } finally {
    loading.value = false
  }
}

const fetchPickPutawayList = async () => {
  try {
    const result = await outboundPickPutawayService.getPage({
      page_index: 1,
      page_size: 1000,
      pick_putaway_status: 3
    })
    pickPutawayList.value = result.rows
  } catch (error: any) {
    console.error('获取拣货单列表失败:', error)
  }
}

const handleSearch = () => {
  pagination.page_index = 1
  fetchReceiptList()
}

const resetSearch = () => {
  searchForm.receipt_no = ''
  searchForm.order_no = ''
  searchForm.receipt_status = undefined
  pagination.page_index = 1
  fetchReceiptList()
}

const handleSizeChange = (size: number) => {
  pagination.page_size = size
  fetchReceiptList()
}

const handleCurrentChange = (current: number) => {
  pagination.page_index = current
  fetchReceiptList()
}

const handleAdd = () => {
  formData.outbound_pick_putaway_id = undefined
  dialogVisible.value = true
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    submitting.value = true
    
    await outboundReceiptService.create({
      outbound_pick_putaway_id: formData.outbound_pick_putaway_id!
    })
    
    ElMessage.success('创建成功')
    dialogVisible.value = false
    fetchReceiptList()
  } catch (error: any) {
    ElMessage.error(error.message || '操作失败')
  } finally {
    submitting.value = false
  }
}

const handleViewDetail = async (row: OutboundReceiptViewModel) => {
  try {
    const result = await outboundReceiptService.getById(row.id)
    selectedReceipt.value = result
    detailDialogVisible.value = true
  } catch (error: any) {
    ElMessage.error(error.message || '获取详情失败')
  }
}

const handleCompleteOutbound = async (row: OutboundReceiptViewModel) => {
  try {
    await ElMessageBox.confirm('确定要完成出库吗？此操作将扣减库存。', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await outboundReceiptService.completeOutbound(
      row.id,
      userStore.userInfo?.username || '系统用户'
    )
    
    ElMessage.success('完成出库成功')
    fetchReceiptList()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '操作失败')
    }
  }
}

const handleDelete = async (id: number) => {
  try {
    await ElMessageBox.confirm('确定要删除这个出库单吗？', '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await outboundReceiptService.delete(id)
    ElMessage.success('删除成功')
    fetchReceiptList()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '删除失败')
    }
  }
}

const getStatusType = (status: number) => {
  switch (status) {
    case 1: return 'info'
    case 2: return 'success'
    case 3: return 'danger'
    default: return ''
  }
}

const getStatusText = (status: number) => {
  switch (status) {
    case 1: return '待出库'
    case 2: return '已出库'
    case 3: return '已取消'
    default: return ''
  }
}

onMounted(() => {
  fetchReceiptList()
  fetchPickPutawayList()
})
</script>

<style scoped>
.outbound-receipt-management { padding: 20px }
.card-header { display: flex; justify-content: space-between; align-items: center }
.search-section { margin-bottom: 20px }
.search-form { display: flex; flex-wrap: wrap }
.pagination { margin-top: 20px; display: flex; justify-content: flex-end }
.dialog-footer { display: flex; justify-content: flex-end; gap: 10px }
.receipt-detail { padding: 10px 0 }
.receipt-header { margin-bottom: 20px }
.receipt-detail h4 { margin: 20px 0 15px 0; font-size: 16px; color: #303133 }
</style>
