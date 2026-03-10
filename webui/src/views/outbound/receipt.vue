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
              <el-option v-for="(label, value) in OutboundReceiptStatusMap" :key="value" :label="label" :value="value" />
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
            <StatusTag :status="scope.row.receipt_status" :status-map="OutboundReceiptStatusMap" :type-map="OutboundReceiptStatusTypeMap" />
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
            <el-button v-if="scope.row.receipt_status === OutboundReceiptStatus.PENDING" type="success" size="small" @click="handleCompleteOutbound(scope.row)">
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
          :page-sizes="PAGE_SIZES"
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
          <el-descriptions-item label="状态">
            <StatusTag :status="selectedReceipt.receipt_status" :status-map="OutboundReceiptStatusMap" :type-map="OutboundReceiptStatusTypeMap" />
          </el-descriptions-item>
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
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { outboundReceiptService, type OutboundReceiptViewModel } from '@/services/outboundReceiptService'
import { outboundPickPutawayService, type OutboundPickPutawayViewModel } from '@/services/outboundPickPutawayService'
import { useUserStore } from '@/store/user'
import { usePagination } from '@/composables/usePagination'
import { useConfirm } from '@/composables/useConfirm'
import { StatusTag } from '@/components/business'
import { OutboundReceiptStatus, OutboundReceiptStatusMap, OutboundReceiptStatusTypeMap, OutboundPickPutawayStatus, PAGE_SIZES } from '@/constants'

const loading = ref(false)
const submitting = ref(false)

const searchForm = reactive({
  receipt_no: '',
  order_no: '',
  receipt_status: undefined as number | undefined
})

const { pagination, handleSizeChange, handleCurrentChange, setTotal } = usePagination()
const { confirmDelete, confirm } = useConfirm()

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
const selectedReceipt = ref<any>(null)
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
    receiptList.value = result.rows || []
    setTotal(result.totals)
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
      pick_putaway_status: OutboundPickPutawayStatus.COMPLETED
    })
    pickPutawayList.value = result.rows || []
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
  const confirmed = await confirm('确定要完成出库吗？此操作将扣减库存。', { title: '提示', type: 'warning' })
  if (!confirmed) return
  
  try {
    await outboundReceiptService.completeOutbound(
      row.id,
      userStore.userInfo?.user_name || '系统用户'
    )
    
    ElMessage.success('完成出库成功')
    fetchReceiptList()
  } catch (error: any) {
    ElMessage.error(error.message || '操作失败')
  }
}

const handleDelete = async (id: number) => {
  const confirmed = await confirmDelete('这个出库单')
  if (!confirmed) return
  
  try {
    await outboundReceiptService.delete(id)
    ElMessage.success('删除成功')
    fetchReceiptList()
  } catch (error: any) {
    ElMessage.error(error.message || '删除失败')
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
