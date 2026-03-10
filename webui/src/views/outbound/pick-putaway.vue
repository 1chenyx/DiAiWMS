<template>
  <div class="outbound-pick-putaway-management">
    <el-card shadow="hover">
      <template #header>
        <div class="card-header">
          <span>出库拣货管理</span>
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon> 创建拣货单
          </el-button>
        </div>
      </template>
      
      <div class="search-section">
        <el-form :inline="true" :model="searchForm" class="search-form">
          <el-form-item label="拣货单号">
            <el-input v-model="searchForm.pick_putaway_no" placeholder="请输入拣货单号" clearable />
          </el-form-item>
          <el-form-item label="出库订单号">
            <el-input v-model="searchForm.order_no" placeholder="请输入出库订单号" clearable />
          </el-form-item>
          <el-form-item label="状态">
            <el-select v-model="searchForm.pick_putaway_status" placeholder="请选择状态" clearable>
              <el-option label="待拣货" :value="0" />
              <el-option label="拣货中" :value="1" />
              <el-option label="拣货完成" :value="2" />
              <el-option label="已生成出库单" :value="3" />
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
        <el-table-column prop="pick_putaway_no" label="拣货单号" />
        <el-table-column prop="order_no" label="出库订单号" />
        <el-table-column prop="customer_name" label="客户" />
        <el-table-column prop="warehouse_name" label="仓库" />
        <el-table-column prop="total_qty" label="总数量" />
        <el-table-column prop="total_picked_qty" label="已拣货数量" />
        <el-table-column prop="pick_putaway_status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.pick_putaway_status)">
              {{ getStatusText(scope.row.pick_putaway_status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="picker" label="拣货人" />
        <el-table-column prop="create_time" label="创建时间" />
        <el-table-column label="操作" fixed="right" width="280">
          <template #default="scope">
            <el-button type="primary" size="small" @click="handleViewDetail(scope.row)">
              <el-icon><View /></el-icon> 详情
            </el-button>
            <el-button v-if="scope.row.pick_putaway_status === 0" type="success" size="small" @click="handleStartPick(scope.row)">
              <el-icon><Select /></el-icon> 开始拣货
            </el-button>
            <el-button v-if="scope.row.pick_putaway_status === 1" type="success" size="small" @click="handleCompletePick(scope.row)">
              <el-icon><Check /></el-icon> 完成拣货
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
    
    <el-dialog v-model="dialogVisible" title="创建拣货单" width="600px">
      <el-form ref="formRef" :model="formData" :rules="formRules" label-width="120px">
        <el-form-item label="出库订单" prop="outbound_order_id">
          <el-select v-model="formData.outbound_order_id" placeholder="请选择出库订单" style="width: 100%" filterable>
            <el-option 
              v-for="order in orderList" 
              :key="order.id" 
              :label="`${order.order_no} - ${order.customer_name}`" 
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
    
    <el-dialog v-model="detailDialogVisible" title="拣货单详情" width="1200px">
      <div class="pick-putaway-detail" v-if="selectedPickPutaway">
        <el-descriptions :column="2" border class="pick-putaway-header">
          <el-descriptions-item label="拣货单号">{{ selectedPickPutaway.pick_putaway_no }}</el-descriptions-item>
          <el-descriptions-item label="状态">{{ getStatusText(selectedPickPutaway.pick_putaway_status) }}</el-descriptions-item>
          <el-descriptions-item label="出库订单号">{{ selectedPickPutaway.order_no }}</el-descriptions-item>
          <el-descriptions-item label="客户">{{ selectedPickPutaway.customer_name }}</el-descriptions-item>
          <el-descriptions-item label="仓库">{{ selectedPickPutaway.warehouse_name }}</el-descriptions-item>
          <el-descriptions-item label="拣货人">{{ selectedPickPutaway.picker }}</el-descriptions-item>
          <el-descriptions-item label="总数量">{{ selectedPickPutaway.total_qty }}</el-descriptions-item>
          <el-descriptions-item label="已拣货数量">{{ selectedPickPutaway.total_picked_qty }}</el-descriptions-item>
          <el-descriptions-item label="拣货时间">{{ selectedPickPutaway.pick_time }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ selectedPickPutaway.create_time }}</el-descriptions-item>
        </el-descriptions>
        
        <div v-if="selectedPickPutaway.items && selectedPickPutaway.items.length > 0">
          <h4>商品明细</h4>
          <el-table :data="selectedPickPutaway.items" style="width: 100%" border>
            <el-table-column prop="sku_code" label="SKU编码" width="120" />
            <el-table-column prop="sku_name" label="SKU名称" width="150" />
            <el-table-column prop="spu_name" label="SPU名称" width="150" />
            <el-table-column prop="qty" label="应拣货数量" width="100" />
            <el-table-column prop="picked_qty" label="已拣货数量" width="100" />
            <el-table-column prop="goods_location_code" label="当前库位" width="150" />
            <el-table-column label="选择库位" width="250" v-if="selectedPickPutaway.pick_putaway_status === 1">
              <template #default="scope">
                <el-tree-select
                  v-model="scope.row.selected_location_id"
                  :data="locationTree"
                  :props="treeProps"
                  placeholder="请选择库位"
                  filterable
                  check-strictly
                  style="width: 100%"
                  @change="(val: number) => handleLocationChange(scope.row, val)"
                />
              </template>
            </el-table-column>
            <el-table-column label="本次拣货数量" width="120" v-if="selectedPickPutaway.pick_putaway_status === 1">
              <template #default="scope">
                <el-input-number
                  v-model="scope.row.pick_input_qty"
                  :min="1"
                  :max="scope.row.qty - (scope.row.picked_qty || 0)"
                  size="small"
                  style="width: 100%"
                  placeholder="数量"
                />
              </template>
            </el-table-column>
            <el-table-column label="操作" width="100" v-if="selectedPickPutaway.pick_putaway_status === 1">
              <template #default="scope">
                <el-button 
                  type="primary" 
                  size="small" 
                  @click="handlePickItem(scope.row)"
                  :disabled="!scope.row.selected_location_id || !scope.row.pick_input_qty"
                >
                  确认拣货
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
import { ElMessageBox, ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { outboundPickPutawayService, type OutboundPickPutawayViewModel } from '@/services/outboundPickPutawayService'
import { outboundOrderService, type OutboundOrderViewModel } from '@/services/outboundOrderService'
import { warehouseLocationService } from '@/services/warehouseLocationService'
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

const pickPutawayList = ref<OutboundPickPutawayViewModel[]>([])
const orderList = ref<OutboundOrderViewModel[]>([])
const locationTree = ref<any[]>([])

const treeProps = {
  value: 'id',
  label: 'node_name',
  children: 'children',
  disabled: (data: any) => {
    return data.node_type !== 3
  }
}

const dialogVisible = ref(false)
const formRef = ref<FormInstance>()
const formData = reactive({
  outbound_order_id: undefined as number | undefined
})

const formRules = reactive<FormRules>({
  outbound_order_id: [{ required: true, message: '请选择出库订单', trigger: 'change' }]
})

const detailDialogVisible = ref(false)
const selectedPickPutaway = ref<OutboundPickPutawayViewModel | null>(null)
const userStore = useUserStore()

const fetchPickPutawayList = async () => {
  loading.value = true
  try {
    const result = await outboundPickPutawayService.getPage({
      page_index: pagination.page_index,
      page_size: pagination.page_size,
      pick_putaway_no: searchForm.pick_putaway_no || undefined,
      order_no: searchForm.order_no || undefined,
      pick_putaway_status: searchForm.pick_putaway_status
    })
    pickPutawayList.value = result.rows || []
    pagination.total = result.totals
  } catch (error: any) {
    ElMessage.error(error.message || '获取拣货单列表失败')
  } finally {
    loading.value = false
  }
}

const fetchOrderList = async () => {
  try {
    const result = await outboundOrderService.getPage({
      page_index: 1,
      page_size: 1000,
      order_status: 0
    })
    orderList.value = result.rows || []
  } catch (error: any) {
    console.error('获取出库订单列表失败:', error)
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
  formData.outbound_order_id = undefined
  dialogVisible.value = true
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    submitting.value = true
    
    await outboundPickPutawayService.create({
      outbound_order_id: formData.outbound_order_id!
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

const handleViewDetail = async (row: OutboundPickPutawayViewModel) => {
  try {
    const result = await outboundPickPutawayService.getById(row.id)
    result.items?.forEach((item: any) => {
      item.selected_location_id = item.goods_location_id
      item.pick_input_qty = 1
    })
    selectedPickPutaway.value = result
    
    if (result.warehouse_id) {
      const treeResult = await warehouseLocationService.getTreeByWarehouse(result.warehouse_id)
      locationTree.value = [treeResult]
    }
    
    detailDialogVisible.value = true
  } catch (error: any) {
    ElMessage.error(error.message || '获取详情失败')
  }
}

const handleStartPick = async (row: OutboundPickPutawayViewModel) => {
  try {
    await ElMessageBox.confirm('确定要开始拣货吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'info'
    })
    
    await outboundPickPutawayService.startPick(
      row.id,
      userStore.userInfo?.user_id || 0,
      userStore.userInfo?.user_name || '系统用户'
    )
    
    ElMessage.success('开始拣货成功')
    fetchPickPutawayList()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '操作失败')
    }
  }
}

const handlePickItem = async (item: any) => {
  try {
    if (!item.selected_location_id) {
      ElMessage.warning('请先选择库位')
      return
    }
    
    if (!item.pick_input_qty || item.pick_input_qty <= 0) {
      ElMessage.warning('请输入拣货数量')
      return
    }
    
    const remainingQty = item.qty - (item.picked_qty || 0)
    if (item.pick_input_qty > remainingQty) {
      ElMessage.warning(`拣货数量不能超过剩余数量 ${remainingQty}`)
      return
    }
    
    const pickedQty = (item.picked_qty || 0) + item.pick_input_qty
    await outboundPickPutawayService.updateItem({
      id: item.id,
      picked_qty: pickedQty,
      goods_location_id: item.selected_location_id,
      picker_id: userStore.userInfo?.user_id || 0,
      picker: userStore.userInfo?.user_name || '系统用户',
      pick_time: Math.floor(Date.now() / 1000)
    })
    
    ElMessage.success('拣货成功')
    item.picked_qty = pickedQty
    item.goods_location_id = item.selected_location_id
    item.pick_input_qty = 1
  } catch (error: any) {
    ElMessage.error(error.message || '拣货失败')
  }
}

const handleLocationChange = (item: any, val: number) => {
  if (!locationTree.value || locationTree.value.length === 0) return
  
  const findLocationInfo = (nodes: any[], val: number, path: any[] = []): any => {
    for (const node of nodes) {
      if (node.id === val) {
        return { ...node, path }
      }
      if (node.children && node.children.length > 0) {
        const result = findLocationInfo(node.children, val, [...path, node])
        if (result) return result
      }
    }
    return null
  }
  
  const locationInfo = findLocationInfo(locationTree.value, val)
  if (locationInfo) {
    const path = locationInfo.path || []
    let warehouseName = ''
    let areaName = ''
    
    for (const node of path) {
      if (node.node_type === 1) {
        warehouseName = node.node_name
      } else if (node.node_type === 2) {
        areaName = node.node_name
      }
    }
    
    item.selected_warehouse_name = warehouseName
    item.selected_area_name = areaName
  }
}

const handleCompletePick = async (row: OutboundPickPutawayViewModel) => {
  try {
    await ElMessageBox.confirm('确定要完成拣货吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'info'
    })
    
    await outboundPickPutawayService.completePick(row.id)
    
    ElMessage.success('完成拣货成功')
    fetchPickPutawayList()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '操作失败')
    }
  }
}

const handleDelete = async (id: number) => {
  try {
    await ElMessageBox.confirm('确定要删除这个拣货单吗？', '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await outboundPickPutawayService.delete(id)
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
    case 0: return 'info'
    case 1: return 'warning'
    case 2: return 'success'
    case 3: return 'primary'
    case 4: return 'danger'
    default: return ''
  }
}

const getStatusText = (status: number) => {
  switch (status) {
    case 0: return '待拣货'
    case 1: return '拣货中'
    case 2: return '拣货完成'
    case 3: return '已生成出库单'
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
.outbound-pick-putaway-management { padding: 20px }
.card-header { display: flex; justify-content: space-between; align-items: center }
.search-section { margin-bottom: 20px }
.search-form { display: flex; flex-wrap: wrap }
.pagination { margin-top: 20px; display: flex; justify-content: flex-end }
.dialog-footer { display: flex; justify-content: flex-end; gap: 10px }
.pick-putaway-detail { padding: 10px 0 }
.pick-putaway-header { margin-bottom: 20px }
.pick-putaway-detail h4 { margin: 20px 0 15px 0; font-size: 16px; color: #303133 }
</style>
