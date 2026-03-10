<template>
  <div class="inbound-receipt-management">
    <el-card shadow="hover">
      <template #header>
        <div class="card-header">
          <span>入库单管理</span>
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon> 创建入库单
          </el-button>
        </div>
      </template>
      
      <div class="search-section">
        <el-form :inline="true" :model="searchForm" class="search-form">
          <el-form-item label="入库单号">
            <el-input v-model="searchForm.receipt_no" placeholder="请输入入库单号" clearable />
          </el-form-item>
          <el-form-item label="入库订单号">
            <el-input v-model="searchForm.order_no" placeholder="请输入入库订单号" clearable />
          </el-form-item>
          <el-form-item label="状态">
            <el-select v-model="searchForm.receipt_status" placeholder="请选择状态" clearable>
              <el-option label="待入库" :value="0" />
              <el-option label="已入库" :value="1" />
              <el-option label="已取消" :value="2" />
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
        <el-table-column prop="receipt_no" label="入库单号" />
        <el-table-column prop="pick_putaway_no" label="拣货上架单号" />
        <el-table-column prop="order_no" label="入库订单号" />
        <el-table-column prop="supplier_name" label="供应商" />
        <el-table-column prop="warehouse_name" label="仓库" />
        <el-table-column prop="total_qty" label="总数量" />
        <el-table-column prop="receipt_status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.receipt_status)">
              {{ getStatusText(scope.row.receipt_status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="inbound_person" label="入库人" />
        <el-table-column prop="inbound_time" label="入库时间">
          <template #default="scope">
            {{ formatTimestamp(scope.row.inbound_time) }}
          </template>
        </el-table-column>
        <el-table-column prop="create_time" label="创建时间">
          <template #default="scope">
            {{ formatTimestamp(scope.row.create_time) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" fixed="right" width="280">
          <template #default="scope">
            <el-button type="primary" size="small" @click="handleViewDetail(scope.row)">
              <el-icon><View /></el-icon> 详情
            </el-button>
            <el-button v-if="scope.row.receipt_status === 0" type="success" size="small" @click="handleCompleteInbound(scope.row)">
              <el-icon><Check /></el-icon> 完成入库
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
    
    <el-dialog v-model="dialogVisible" title="创建入库单" width="600px">
      <el-form ref="formRef" :model="formData" :rules="formRules" label-width="120px">
        <el-form-item label="拣货上架单" prop="inbound_pick_putaway_id">
          <el-select v-model="formData.inbound_pick_putaway_id" placeholder="请选择拣货上架单" style="width: 100%" filterable>
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
    
    <el-dialog v-model="detailDialogVisible" title="入库单详情" width="1000px">
      <div class="receipt-detail" v-if="selectedReceipt">
        <el-descriptions :column="2" border class="receipt-header">
          <el-descriptions-item label="入库单号">{{ selectedReceipt.receipt_no }}</el-descriptions-item>
          <el-descriptions-item label="状态">{{ getStatusText(selectedReceipt.receipt_status) }}</el-descriptions-item>
          <el-descriptions-item label="拣货上架单号">{{ selectedReceipt.pick_putaway_no }}</el-descriptions-item>
          <el-descriptions-item label="入库订单号">{{ selectedReceipt.order_no }}</el-descriptions-item>
          <el-descriptions-item label="供应商">{{ selectedReceipt.supplier_name }}</el-descriptions-item>
          <el-descriptions-item label="仓库">{{ selectedReceipt.warehouse_name }}</el-descriptions-item>
          <el-descriptions-item label="总数量">{{ selectedReceipt.total_qty }}</el-descriptions-item>
          <el-descriptions-item label="入库人">{{ selectedReceipt.inbound_person }}</el-descriptions-item>
          <el-descriptions-item label="入库时间">{{ formatTimestamp(selectedReceipt.inbound_time) }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ formatTimestamp(selectedReceipt.create_time) }}</el-descriptions-item>
        </el-descriptions>
        
        <div v-if="selectedReceipt.items && selectedReceipt.items.length > 0">
          <h4>商品明细</h4>
          <el-table :data="selectedReceipt.items" style="width: 100%" border>
            <el-table-column prop="sku_code" label="SKU编码" />
            <el-table-column prop="sku_name" label="SKU名称" />
            <el-table-column prop="spu_name" label="SPU名称" />
            <el-table-column prop="qty" label="数量" />
            <el-table-column prop="batch_no" label="批次号" />
            <el-table-column prop="production_date" label="生产日期">
              <template #default="scope">
                {{ scope.row.production_date ? formatTimestamp(scope.row.production_date) : '-' }}
              </template>
            </el-table-column>
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
import { inboundReceiptService, type InboundReceiptViewModel } from '@/services/inboundReceiptService'
import { inboundPickPutawayService, type InboundPickPutawayViewModel } from '@/services/inboundPickPutawayService'
import { useUserStore } from '@/store/user'
import { formatTimestamp } from '@/utils/format'

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

const receiptList = ref<InboundReceiptViewModel[]>([])
const pickPutawayList = ref<InboundPickPutawayViewModel[]>([])

const dialogVisible = ref(false)
const formRef = ref<FormInstance>()
const formData = reactive({
  inbound_pick_putaway_id: undefined as number | undefined
})

const formRules = reactive<FormRules>({
  inbound_pick_putaway_id: [{ required: true, message: '请选择拣货上架单', trigger: 'change' }]
})

const detailDialogVisible = ref(false)
const selectedReceipt = ref<InboundReceiptViewModel | null>(null)
const userStore = useUserStore()

const fetchReceiptList = async () => {
  loading.value = true
  try {
    const result = await inboundReceiptService.getPage({
      page_index: pagination.page_index,
      page_size: pagination.page_size,
      receipt_no: searchForm.receipt_no || undefined,
      order_no: searchForm.order_no || undefined,
      receipt_status: searchForm.receipt_status
    })
    receiptList.value = result.rows || []
    pagination.total = result.totals
  } catch (error: any) {
    ElMessage.error(error.message || '获取入库单列表失败')
  } finally {
    loading.value = false
  }
}

const fetchPickPutawayList = async () => {
  try {
    const result = await inboundPickPutawayService.getPage({
      page_index: 1,
      page_size: 1000,
      pick_putaway_status: 2
    })
    pickPutawayList.value = result.rows || []
  } catch (error: any) {
    console.error('获取拣货上架单列表失败:', error)
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
  formData.inbound_pick_putaway_id = undefined
  dialogVisible.value = true
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    submitting.value = true
    
    await inboundReceiptService.create({
      inbound_pick_putaway_id: formData.inbound_pick_putaway_id!,
      inbound_person: userStore.userInfo?.user_name || '系统用户'
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

const handleViewDetail = async (row: InboundReceiptViewModel) => {
  try {
    const result = await inboundReceiptService.getById(row.id)
    selectedReceipt.value = result
    detailDialogVisible.value = true
  } catch (error: any) {
    ElMessage.error(error.message || '获取详情失败')
  }
}

const handleCompleteInbound = async (row: InboundReceiptViewModel) => {
  try {
    await ElMessageBox.confirm('确定要完成入库吗？此操作将增加库存。', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await inboundReceiptService.completeInbound(
      row.id,
      userStore.userInfo?.user_name || '系统用户'
    )
    
    ElMessage.success('完成入库成功')
    fetchReceiptList()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '操作失败')
    }
  }
}

const handleDelete = async (id: number) => {
  try {
    await ElMessageBox.confirm('确定要删除这个入库单吗？', '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await inboundReceiptService.delete(id)
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
    case 0: return 'info'
    case 1: return 'success'
    case 2: return 'danger'
    default: return ''
  }
}

const getStatusText = (status: number) => {
  switch (status) {
    case 0: return '待入库'
    case 1: return '已入库'
    case 2: return '已取消'
    default: return ''
  }
}

onMounted(() => {
  fetchReceiptList()
  fetchPickPutawayList()
})
</script>

<style scoped>
.inbound-receipt-management { padding: 20px }
.card-header { display: flex; justify-content: space-between; align-items: center }
.search-section { margin-bottom: 20px }
.search-form { display: flex; flex-wrap: wrap }
.pagination { margin-top: 20px; display: flex; justify-content: flex-end }
.dialog-footer { display: flex; justify-content: flex-end; gap: 10px }
.receipt-detail { padding: 10px 0 }
.receipt-header { margin-bottom: 20px }
.receipt-detail h4 { margin: 20px 0 15px 0; font-size: 16px; color: #303133 }
</style>
