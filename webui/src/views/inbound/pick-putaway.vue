<template>
  <div class="inbound-pick-putaway-management">
    <el-card shadow="hover">
      <template #header>
        <div class="card-header">
          <span>入库拣货上架管理</span>
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon> 创建拣货上架单
          </el-button>
        </div>
      </template>
      
      <div class="search-section">
        <el-form :inline="true" :model="searchForm" class="search-form">
          <el-form-item label="拣货上架单号">
            <el-input v-model="searchForm.pick_putaway_no" placeholder="请输入拣货上架单号" clearable />
          </el-form-item>
          <el-form-item label="入库订单号">
            <el-input v-model="searchForm.order_no" placeholder="请输入入库订单号" clearable />
          </el-form-item>
          <el-form-item label="状态">
            <el-select v-model="searchForm.pick_putaway_status" placeholder="请选择状态" clearable>
              <el-option label="待上架" :value="1" />
              <el-option label="上架中" :value="2" />
              <el-option label="已上架" :value="3" />
              <el-option label="已取消" :value="4" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleSearch">搜索</el-button>
            <el-button @click="resetSearch">重置</el-button>
          </el-form-item>
        </el-form>
      </div>
      
      <el-table :data="pickPutawayList" style="width: 100%" v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="pick_putaway_no" label="拣货上架单号" />
        <el-table-column prop="order_no" label="入库订单号" />
        <el-table-column prop="supplier_name" label="供应商" />
        <el-table-column prop="warehouse_name" label="仓库" />
        <el-table-column prop="total_qty" label="总数量" />
        <el-table-column prop="total_picked_qty" label="已拣货数量" />
        <el-table-column prop="total_putaway_qty" label="已上架数量" />
        <el-table-column prop="pick_putaway_status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.pick_putaway_status)">
              {{ getStatusText(scope.row.pick_putaway_status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="putaway_person" label="上架人" />
        <el-table-column prop="create_time" label="创建时间" />
        <el-table-column label="操作" fixed="right" width="280">
          <template #default="scope">
            <el-button type="primary" size="small" @click="handleViewDetail(scope.row)">
              <el-icon><View /></el-icon> 详情
            </el-button>
            <el-button v-if="scope.row.pick_putaway_status === 1" type="success" size="small" @click="handleStartPutaway(scope.row)">
              <el-icon><Select /></el-icon> 开始上架
            </el-button>
            <el-button v-if="scope.row.pick_putaway_status === 2" type="success" size="small" @click="handleCompletePutaway(scope.row)">
              <el-icon><Check /></el-icon> 完成上架
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
    
    <el-dialog v-model="dialogVisible" title="创建拣货上架单" width="600px">
      <el-form ref="formRef" :model="formData" :rules="formRules" label-width="120px">
        <el-form-item label="入库订单" prop="inbound_order_id">
          <el-select v-model="formData.inbound_order_id" placeholder="请选择入库订单" style="width: 100%" filterable>
            <el-option 
              v-for="order in orderList" 
              :key="order.id" 
              :label="`${order.order_no} - ${order.supplier_name}`" 
              :value="order.id" 
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
    
    <el-dialog v-model="detailDialogVisible" title="拣货上架单详情" width="1000px">
      <div class="pick-putaway-detail" v-if="selectedPickPutaway">
        <el-descriptions :column="2" border class="pick-putaway-header">
          <el-descriptions-item label="拣货上架单号">{{ selectedPickPutaway.pick_putaway_no }}</el-descriptions-item>
          <el-descriptions-item label="状态">{{ getStatusText(selectedPickPutaway.pick_putaway_status) }}</el-descriptions-item>
          <el-descriptions-item label="入库订单号">{{ selectedPickPutaway.order_no }}</el-descriptions-item>
          <el-descriptions-item label="供应商">{{ selectedPickPutaway.supplier_name }}</el-descriptions-item>
          <el-descriptions-item label="仓库">{{ selectedPickPutaway.warehouse_name }}</el-descriptions-item>
          <el-descriptions-item label="上架人">{{ selectedPickPutaway.putaway_person }}</el-descriptions-item>
          <el-descriptions-item label="总数量">{{ selectedPickPutaway.total_qty }}</el-descriptions-item>
          <el-descriptions-item label="已上架数量">{{ selectedPickPutaway.total_putaway_qty }}</el-descriptions-item>
          <el-descriptions-item label="上架时间">{{ selectedPickPutaway.putaway_time }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ selectedPickPutaway.create_time }}</el-descriptions-item>
        </el-descriptions>
        
        <div v-if="selectedPickPutaway.items && selectedPickPutaway.items.length > 0">
          <h4>商品明细</h4>
          <el-table :data="selectedPickPutaway.items" style="width: 100%" border>
            <el-table-column prop="sku_code" label="SKU编码" />
            <el-table-column prop="sku_name" label="SKU名称" />
            <el-table-column prop="spu_name" label="SPU名称" />
            <el-table-column prop="qty" label="应上架数量" />
            <el-table-column prop="picked_qty" label="已拣货数量" />
            <el-table-column prop="putaway_qty" label="已上架数量" />
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
import { Plus, View, Delete, Select, Check } from '@element-plus/icons-vue'
import { ElMessageBox, ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { inboundPickPutawayService, type InboundPickPutawayViewModel, type InboundPickPutawayCreate } from '@/services/inboundPickPutawayService'
import { inboundOrderService, type InboundOrderViewModel } from '@/services/inboundOrderService'
import { useUserStore } from '@/store/user'

const loading = ref(false)
const submitting = ref(false)

const searchForm = reactive({
  pick_putaway_no: '',
  order_no: '',
  pick_putaway_status: undefined as number | undefined
})

const pagination = reactive({
  page_index: 1,
  page_size: 10,
  total: 0
})

const pickPutawayList = ref<InboundPickPutawayViewModel[]>([])
const orderList = ref<InboundOrderViewModel[]>([])

const dialogVisible = ref(false)
const formRef = ref<FormInstance>()
const formData = reactive({
  inbound_order_id: undefined as number | undefined
})

const formRules = reactive<FormRules>({
  inbound_order_id: [{ required: true, message: '请选择入库订单', trigger: 'change' }]
})

const detailDialogVisible = ref(false)
const selectedPickPutaway = ref<InboundPickPutawayViewModel | null>(null)
const userStore = useUserStore()

const fetchPickPutawayList = async () => {
  loading.value = true
  try {
    const result = await inboundPickPutawayService.getPage({
      page_index: pagination.page_index,
      page_size: pagination.page_size,
      pick_putaway_no: searchForm.pick_putaway_no || undefined,
      order_no: searchForm.order_no || undefined,
      pick_putaway_status: searchForm.pick_putaway_status
    })
    pickPutawayList.value = result.rows
    pagination.total = result.totals
  } catch (error: any) {
    ElMessage.error(error.message || '获取拣货上架单列表失败')
  } finally {
    loading.value = false
  }
}

const fetchOrderList = async () => {
  try {
    const result = await inboundOrderService.getPage({
      page_index: 1,
      page_size: 1000,
      order_status: 1
    })
    orderList.value = result.rows
  } catch (error: any) {
    console.error('获取入库订单列表失败:', error)
  }
}

const handleSearch = () => {
  pagination.page_index = 1
  fetchPickPutawayList()
}

const resetSearch = () => {
  searchForm.pick_putaway_no = ''
  searchForm.order_no = ''
  searchForm.pick_putaway_status = undefined
  pagination.page_index = 1
  fetchPickPutawayList()
}

const handleSizeChange = (size: number) => {
  pagination.page_size = size
  fetchPickPutawayList()
}

const handleCurrentChange = (current: number) => {
  pagination.page_index = current
  fetchPickPutawayList()
}

const handleAdd = () => {
  formData.inbound_order_id = undefined
  dialogVisible.value = true
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    submitting.value = true
    
    await inboundPickPutawayService.create({
      inbound_order_id: formData.inbound_order_id!
    })
    
    ElMessage.success('创建成功')
    dialogVisible.value = false
    fetchPickPutawayList()
  } catch (error: any) {
    ElMessage.error(error.message || '操作失败')
  } finally {
    submitting.value = false
  }
}

const handleViewDetail = async (row: InboundPickPutawayViewModel) => {
  try {
    const result = await inboundPickPutawayService.getById(row.id)
    selectedPickPutaway.value = result
    detailDialogVisible.value = true
  } catch (error: any) {
    ElMessage.error(error.message || '获取详情失败')
  }
}

const handleStartPutaway = async (row: InboundPickPutawayViewModel) => {
  try {
    await ElMessageBox.confirm('确定要开始上架吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'info'
    })
    
    await inboundPickPutawayService.startPutaway(
      row.id,
      userStore.userInfo?.id || 0,
      userStore.userInfo?.username || '系统用户'
    )
    
    ElMessage.success('开始上架成功')
    fetchPickPutawayList()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '操作失败')
    }
  }
}

const handleCompletePutaway = async (row: InboundPickPutawayViewModel) => {
  try {
    await ElMessageBox.confirm('确定要完成上架吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'info'
    })
    
    await inboundPickPutawayService.completePutaway(row.id)
    
    ElMessage.success('完成上架成功')
    fetchPickPutawayList()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '操作失败')
    }
  }
}

const handleDelete = async (id: number) => {
  try {
    await ElMessageBox.confirm('确定要删除这个拣货上架单吗？', '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await inboundPickPutawayService.delete(id)
    ElMessage.success('删除成功')
    fetchPickPutawayList()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '删除失败')
    }
  }
}

const getStatusType = (status: number) => {
  switch (status) {
    case 1: return 'info'
    case 2: return 'warning'
    case 3: return 'success'
    case 4: return 'danger'
    default: return ''
  }
}

const getStatusText = (status: number) => {
  switch (status) {
    case 1: return '待上架'
    case 2: return '上架中'
    case 3: return '已上架'
    case 4: return '已取消'
    default: return ''
  }
}

onMounted(() => {
  fetchPickPutawayList()
  fetchOrderList()
})
</script>

<style scoped>
.inbound-pick-putaway-management { padding: 20px }
.card-header { display: flex; justify-content: space-between; align-items: center }
.search-section { margin-bottom: 20px }
.search-form { display: flex; flex-wrap: wrap }
.pagination { margin-top: 20px; display: flex; justify-content: flex-end }
.dialog-footer { display: flex; justify-content: flex-end; gap: 10px }
.pick-putaway-detail { padding: 10px 0 }
.pick-putaway-header { margin-bottom: 20px }
.pick-putaway-detail h4 { margin: 20px 0 15px 0; font-size: 16px; color: #303133 }
</style>
