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
              <el-option v-for="(label, value) in PickPutawayStatusMap" :key="value" :label="label" :value="value" />
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
            <StatusTag :status="scope.row.pick_putaway_status" :status-map="PickPutawayStatusMap" :type-map="PickPutawayStatusTypeMap" />
          </template>
        </el-table-column>
        <el-table-column prop="putaway_person" label="上架人" />
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
            <el-button v-if="scope.row.pick_putaway_status === PickPutawayStatus.PENDING" type="success" size="small" @click="handleStartPutaway(scope.row)">
              <el-icon><Select /></el-icon> 开始上架
            </el-button>
            <el-button v-if="scope.row.pick_putaway_status === PickPutawayStatus.IN_PROGRESS" type="success" size="small" @click="handleCompletePutaway(scope.row)">
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
          :page-sizes="PAGE_SIZES"
          layout="total, sizes, prev, pager, next, jumper"
          :total="pagination.total"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>
    
    <el-dialog v-model="dialogVisible" title="创建拣货上架单" width="600px">
      <el-form ref="formRef" :model="formData" :rules="formRules" label-width="120px">
        <el-form-item label="入库订单" prop="inbound_order_ids">
          <el-select 
            v-model="formData.inbound_order_ids" 
            placeholder="请选择入库订单（可多选）" 
            style="width: 100%" 
            filterable 
            multiple
            collapse-tags
            collapse-tags-tooltip
          >
            <el-option 
              v-for="order in orderList" 
              :key="order.id" 
              :label="`${order.order_no} - ${order.supplier_name}`" 
              :value="order.id" 
            />
          </el-select>
        </el-form-item>
        <el-form-item label="备注" prop="remark">
          <el-input 
            v-model="formData.remark" 
            type="textarea" 
            :rows="3" 
            placeholder="请输入备注信息（可选）" 
            maxlength="512"
            show-word-limit
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmit" :loading="submitting">确定</el-button>
        </span>
      </template>
    </el-dialog>
    
    <el-dialog v-model="detailDialogVisible" title="拣货上架单详情" width="1200px">
      <div class="pick-putaway-detail" v-if="selectedPickPutaway">
        <el-descriptions :column="2" border class="pick-putaway-header">
          <el-descriptions-item label="拣货上架单号">{{ selectedPickPutaway.pick_putaway_no }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <StatusTag :status="selectedPickPutaway.pick_putaway_status" :status-map="PickPutawayStatusMap" :type-map="PickPutawayStatusTypeMap" />
          </el-descriptions-item>
          <el-descriptions-item label="入库订单号">{{ selectedPickPutaway.order_no }}</el-descriptions-item>
          <el-descriptions-item label="供应商">{{ selectedPickPutaway.supplier_name }}</el-descriptions-item>
          <el-descriptions-item label="仓库">{{ selectedPickPutaway.warehouse_name }}</el-descriptions-item>
          <el-descriptions-item label="上架人">{{ selectedPickPutaway.putaway_person }}</el-descriptions-item>
          <el-descriptions-item label="总数量">{{ selectedPickPutaway.total_qty }}</el-descriptions-item>
          <el-descriptions-item label="已上架数量">{{ selectedPickPutaway.total_putaway_qty }}</el-descriptions-item>
          <el-descriptions-item label="上架时间">{{ formatTimestamp(selectedPickPutaway.putaway_time) }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ formatTimestamp(selectedPickPutaway.create_time) }}</el-descriptions-item>
        </el-descriptions>
        
        <div v-if="selectedPickPutaway.items && selectedPickPutaway.items.length > 0">
          <h4>商品明细</h4>
          <el-table :data="selectedPickPutaway.items" style="width: 100%" border>
            <el-table-column prop="sku_code" label="SKU编码" width="120" />
            <el-table-column prop="sku_name" label="SKU名称" width="150" />
            <el-table-column prop="spu_name" label="SPU名称" width="150" />
            <el-table-column prop="qty" label="应上架数量" width="100" />
            <el-table-column prop="putaway_qty" label="已上架数量" width="100" />
            <el-table-column prop="batch_no" label="批次号" width="120" />
            <el-table-column prop="production_date" label="生产日期" width="150">
              <template #default="scope">
                {{ scope.row.production_date ? formatTimestamp(scope.row.production_date) : '-' }}
              </template>
            </el-table-column>
            <el-table-column prop="goods_location_code" label="当前库位" width="150" />
            <el-table-column label="选择库位" width="250" v-if="selectedPickPutaway.pick_putaway_status === PickPutawayStatus.IN_PROGRESS">
              <template #default="scope">
                <LocationTreeSelector
                  :key="`location-${selectedPickPutaway.id}-${scope.row.id}`"
                  v-model="scope.row.selected_location_id"
                  :warehouse-id="selectedPickPutaway.warehouse_id"
                  :node-type="3"
                  @change="(val: number | undefined, info: any) => handleLocationChange(scope.row, val, info)"
                />
              </template>
            </el-table-column>
            <el-table-column prop="selected_warehouse_name" label="仓库" width="120" v-if="selectedPickPutaway.pick_putaway_status === PickPutawayStatus.IN_PROGRESS" />
            <el-table-column prop="selected_area_name" label="库区" width="120" v-if="selectedPickPutaway.pick_putaway_status === PickPutawayStatus.IN_PROGRESS" />
            <el-table-column label="本次上架数量" width="120" v-if="selectedPickPutaway.pick_putaway_status === PickPutawayStatus.IN_PROGRESS">
              <template #default="scope">
                <el-input-number
                  v-model="scope.row.putaway_input_qty"
                  :min="1"
                  :max="Math.max(1, scope.row.qty - (scope.row.putaway_qty || 0))"
                  :disabled="scope.row.qty - (scope.row.putaway_qty || 0) <= 0"
                  size="small"
                  style="width: 100%"
                  placeholder="数量"
                />
              </template>
            </el-table-column>
            <el-table-column label="操作" width="100" v-if="selectedPickPutaway.pick_putaway_status === PickPutawayStatus.IN_PROGRESS">
              <template #default="scope">
                <el-button 
                  type="primary" 
                  size="small" 
                  @click="handlePutawayItem(scope.row)"
                  :disabled="!scope.row.selected_location_id || !scope.row.selected_warehouse_id || !scope.row.selected_area_id || !scope.row.putaway_input_qty"
                >
                  确认上架
                </el-button>
              </template>
            </el-table-column>
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
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { inboundPickPutawayService, type InboundPickPutawayViewModel } from '@/services/inboundPickPutawayService'
import { inboundOrderService, type InboundOrderViewModel } from '@/services/inboundOrderService'
import { useUserStore } from '@/store/user'
import { usePagination } from '@/composables/usePagination'
import { useConfirm } from '@/composables/useConfirm'
import { StatusTag, LocationTreeSelector } from '@/components/business'
import { PickPutawayStatus, PickPutawayStatusMap, PickPutawayStatusTypeMap, PAGE_SIZES } from '@/constants'
import { formatTimestamp } from '@/utils/format'

const loading = ref(false)
const submitting = ref(false)

const searchForm = reactive({
  pick_putaway_no: '',
  order_no: '',
  pick_putaway_status: undefined as number | undefined
})

const pickPutawayList = ref<InboundPickPutawayViewModel[]>([])
const orderList = ref<InboundOrderViewModel[]>([])

const dialogVisible = ref(false)
const formRef = ref<FormInstance>()
const formData = reactive({
  inbound_order_ids: [] as number[],
  remark: ''
})

const formRules = reactive<FormRules>({
  inbound_order_ids: [{ required: true, type: 'array', min: 1, message: '请至少选择一个入库订单', trigger: 'change' }]
})

const detailDialogVisible = ref(false)
const selectedPickPutaway = ref<InboundPickPutawayViewModel | null>(null)
const userStore = useUserStore()

const { pagination, handleSizeChange, handleCurrentChange, setTotal } = usePagination({
  onPageChange: () => fetchPickPutawayList()
})
const { confirmDelete, confirmAction } = useConfirm()

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
    pickPutawayList.value = result.rows || []
    setTotal(result.totals)
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
      order_status: 0
    })
    orderList.value = result.rows || []
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

const handleAdd = () => {
  formData.inbound_order_ids = []
  formData.remark = ''
  dialogVisible.value = true
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    submitting.value = true
    
    await inboundPickPutawayService.create({
      inbound_order_ids: formData.inbound_order_ids,
      remark: formData.remark
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
    
    result.items?.forEach((item: any) => {
      item.selected_location_id = undefined
      item.selected_warehouse_id = undefined
      item.selected_warehouse_name = ''
      item.selected_area_id = undefined
      item.selected_area_name = ''
      item.putaway_input_qty = Math.max(1, item.qty - (item.putaway_qty || 0))
    })
    
    selectedPickPutaway.value = result
    detailDialogVisible.value = true
  } catch (error: any) {
    ElMessage.error(error.message || '获取详情失败')
  }
}

const handleStartPutaway = async (row: InboundPickPutawayViewModel) => {
  const confirmed = await confirmAction('开始上架')
  if (!confirmed) return
  
  try {
    await inboundPickPutawayService.startPutaway(
      row.id,
      userStore.userInfo?.user_id || 0,
      userStore.userInfo?.user_name || '系统用户'
    )
    
    ElMessage.success('开始上架成功')
    fetchPickPutawayList()
  } catch (error: any) {
    ElMessage.error(error.message || '操作失败')
  }
}

const handlePutawayItem = async (item: any) => {
  try {
    if (!item.selected_location_id) {
      ElMessage.warning('请先选择库位')
      return
    }
    
    if (!item.putaway_input_qty || item.putaway_input_qty <= 0) {
      ElMessage.warning('请输入上架数量')
      return
    }
    
    const remainingQty = item.qty - (item.putaway_qty || 0)
    if (item.putaway_input_qty > remainingQty) {
      ElMessage.warning(`上架数量不能超过剩余数量 ${remainingQty}`)
      return
    }
    
    const putawayQty = (item.putaway_qty || 0) + item.putaway_input_qty
    await inboundPickPutawayService.updateItem({
      id: item.id,
      putaway_qty: putawayQty,
      goods_location_id: item.selected_location_id,
      warehouse_id: item.selected_warehouse_id || 0,
      warehouse_area_id: item.selected_area_id || 0,
      putaway_person_id: userStore.userInfo?.user_id || 0,
      putaway_person: userStore.userInfo?.user_name || '系统用户',
      putaway_time: Math.floor(Date.now() / 1000),
      batch_no: item.batch_no || '',
      production_date: item.production_date || 0
    })
    
    ElMessage.success('上架成功')
    item.putaway_qty = putawayQty
    item.goods_location_id = item.selected_location_id
    item.putaway_input_qty = 1
  } catch (error: any) {
    ElMessage.error(error.message || '上架失败')
  }
}

const handleLocationChange = (item: any, _val: number | undefined, info: any) => {
  if (info) {
    item.selected_warehouse_id = info.warehouseId
    item.selected_warehouse_name = info.warehouseName
    item.selected_area_id = info.areaId
    item.selected_area_name = info.areaName
  } else {
    item.selected_warehouse_id = undefined
    item.selected_warehouse_name = ''
    item.selected_area_id = undefined
    item.selected_area_name = ''
  }
}

const handleCompletePutaway = async (row: InboundPickPutawayViewModel) => {
  const confirmed = await confirmAction('完成上架')
  if (!confirmed) return
  
  try {
    await inboundPickPutawayService.completePutaway(row.id)
    
    ElMessage.success('完成上架成功')
    fetchPickPutawayList()
  } catch (error: any) {
    ElMessage.error(error.message || '操作失败')
  }
}

const handleDelete = async (id: number) => {
  const confirmed = await confirmDelete('这个拣货上架单')
  if (!confirmed) return
  
  try {
    await inboundPickPutawayService.delete(id)
    ElMessage.success('删除成功')
    fetchPickPutawayList()
  } catch (error: any) {
    ElMessage.error(error.message || '删除失败')
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
