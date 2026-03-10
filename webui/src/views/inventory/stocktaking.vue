<template>
  <div class="stocktaking-management">
    <el-card shadow="hover">
      <template #header>
        <div class="card-header">
          <span>库存盘点</span>
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon> 新增盘点
          </el-button>
        </div>
      </template>
      
      <div class="search-section">
        <el-form :inline="true" :model="searchForm" class="search-form">
          <el-form-item label="作业编号">
            <el-input v-model="searchForm.job_code" placeholder="请输入作业编号" clearable />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleSearch">搜索</el-button>
            <el-button @click="resetSearch">重置</el-button>
          </el-form-item>
        </el-form>
      </div>
      
      <el-table :data="stocktakingList" style="width: 100%" v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="job_code" label="作业编号" />
        <el-table-column prop="sku_code" label="SKU编码" />
        <el-table-column prop="sku_name" label="SKU名称" />
        <el-table-column prop="location_code" label="库位编码" />
        <el-table-column prop="book_qty" label="账面数量" />
        <el-table-column prop="counted_qty" label="盘点数量" />
        <el-table-column prop="difference_qty" label="差异数量">
          <template #default="scope">
            <el-tag :type="getDifferenceType(scope.row.difference_qty)">
              {{ scope.row.difference_qty }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="job_status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.job_status ? 'success' : 'warning'">
              {{ scope.row.job_status ? '已完成' : '进行中' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="creator" label="创建人" />
        <el-table-column prop="create_time" label="创建时间">
          <template #default="scope">
            {{ formatTimestamp(scope.row.create_time) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" fixed="right">
          <template #default="scope">
            <el-button 
              v-if="!scope.row.job_status" 
              type="primary" 
              size="small" 
              @click="handleCount(scope.row)"
            >
              <el-icon><Edit /></el-icon> 盘点
            </el-button>
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
    
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="120px"
      >
        <el-form-item label="作业编号" prop="job_code">
          <el-input v-model="formData.job_code" placeholder="请输入作业编号" />
        </el-form-item>
        
        <el-form-item label="SKU" prop="sku_id">
          <el-select v-model="formData.sku_id" placeholder="请选择SKU" filterable style="width: 100%">
            <el-option 
              v-for="sku in skuList" 
              :key="sku.id" 
              :label="`${sku.sku_code} - ${sku.sku_name}`" 
              :value="sku.id" 
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="货位" prop="goods_location_id">
          <el-select v-model="formData.goods_location_id" placeholder="请选择货位" filterable style="width: 100%">
            <el-option 
              v-for="location in locationList" 
              :key="location.id" 
              :label="location.node_name" 
              :value="location.id" 
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="货主" prop="goods_owner_id">
          <el-select v-model="formData.goods_owner_id" placeholder="请选择货主" filterable style="width: 100%">
            <el-option 
              v-for="owner in goodsOwnerList" 
              :key="owner.id" 
              :label="owner.goods_owner_name" 
              :value="owner.id" 
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="序列号" prop="series_number">
          <el-input v-model="formData.series_number" placeholder="请输入序列号" />
        </el-form-item>
        
        <el-form-item label="过期日期" prop="expiry_date">
          <el-date-picker
            v-model="expiryDate"
            type="date"
            placeholder="请选择过期日期"
            style="width: 100%"
            value-format="X"
          />
        </el-form-item>
        
        <el-form-item label="价格" prop="price">
          <el-input-number v-model="formData.price" :min="0" :precision="2" style="width: 100%" />
        </el-form-item>
        
        <el-form-item label="上架日期" prop="putaway_date">
          <el-date-picker
            v-model="putawayDate"
            type="date"
            placeholder="请选择上架日期"
            style="width: 100%"
            value-format="X"
          />
        </el-form-item>
        
        <el-form-item label="账面数量" prop="book_qty">
          <el-input-number v-model="formData.book_qty" :min="0" style="width: 100%" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmit" :loading="submitting">确定</el-button>
        </span>
      </template>
    </el-dialog>
    
    <el-dialog
      v-model="countDialogVisible"
      title="库存盘点"
      width="500px"
    >
      <el-form
        ref="countFormRef"
        :model="countFormData"
        :rules="countFormRules"
        label-width="120px"
      >
        <el-descriptions :column="2" border class="count-info">
          <el-descriptions-item label="作业编号">{{ countFormData.job_code }}</el-descriptions-item>
          <el-descriptions-item label="SKU编码">{{ selectedStocktaking?.sku_code }}</el-descriptions-item>
          <el-descriptions-item label="SKU名称" :span="2">{{ selectedStocktaking?.sku_name }}</el-descriptions-item>
          <el-descriptions-item label="库位编码">{{ selectedStocktaking?.location_code }}</el-descriptions-item>
          <el-descriptions-item label="账面数量">{{ selectedStocktaking?.book_qty }}</el-descriptions-item>
        </el-descriptions>
        
        <el-form-item label="盘点数量" prop="counted_qty" style="margin-top: 20px">
          <el-input-number v-model="countFormData.counted_qty" :min="0" style="width: 100%" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="countDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleCountSubmit" :loading="submitting">确定</el-button>
        </span>
      </template>
    </el-dialog>
    
    <el-dialog
      v-model="detailDialogVisible"
      title="盘点详情"
      width="700px"
    >
      <el-descriptions :column="2" border v-if="selectedStocktaking">
        <el-descriptions-item label="ID">{{ selectedStocktaking.id }}</el-descriptions-item>
        <el-descriptions-item label="作业编号">{{ selectedStocktaking.job_code }}</el-descriptions-item>
        <el-descriptions-item label="SKU编码">{{ selectedStocktaking.sku_code }}</el-descriptions-item>
        <el-descriptions-item label="SKU名称">{{ selectedStocktaking.sku_name }}</el-descriptions-item>
        <el-descriptions-item label="库位编码">{{ selectedStocktaking.location_code }}</el-descriptions-item>
        <el-descriptions-item label="账面数量">{{ selectedStocktaking.book_qty }}</el-descriptions-item>
        <el-descriptions-item label="盘点数量">{{ selectedStocktaking.counted_qty }}</el-descriptions-item>
        <el-descriptions-item label="差异数量">
          <el-tag :type="getDifferenceType(selectedStocktaking.difference_qty || 0)">
            {{ selectedStocktaking.difference_qty || 0 }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="selectedStocktaking.job_status ? 'success' : 'warning'">
            {{ selectedStocktaking.job_status ? '已完成' : '进行中' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="创建人">{{ selectedStocktaking.creator }}</el-descriptions-item>
        <el-descriptions-item label="处理人">{{ selectedStocktaking.handler || '-' }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ formatTimestamp(selectedStocktaking.create_time) }}</el-descriptions-item>
        <el-descriptions-item label="处理时间">{{ formatTimestamp(selectedStocktaking.handle_time) }}</el-descriptions-item>
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
import { Plus, Edit, Delete, View } from '@element-plus/icons-vue'
import { ElMessageBox, ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { stocktakingService, type Stocktaking, type StocktakingCreate, type StocktakingUpdate } from '@/services/stocktakingService'
import { skuService, type Sku } from '@/services/skuService'
import { warehouseLocationService } from '@/services/warehouseLocationService'
import { goodsOwnerService, type GoodsOwner } from '@/services/goodsOwnerService'
import { formatTimestamp } from '@/utils/format'

const loading = ref(false)
const submitting = ref(false)
const stocktakingList = ref<Stocktaking[]>([])
const skuList = ref<Sku[]>([])
const locationList = ref<any[]>([])
const goodsOwnerList = ref<GoodsOwner[]>([])

const searchForm = reactive({
  job_code: ''
})

const pagination = reactive({
  page_index: 1,
  page_size: 10,
  total: 0
})

const dialogVisible = ref(false)
const dialogTitle = ref('新增盘点')
const formRef = ref<FormInstance>()
const expiryDate = ref<number | null>(null)
const putawayDate = ref<number | null>(null)

const formData = reactive<StocktakingCreate>({
  job_code: '',
  sku_id: 0,
  goods_owner_id: 0,
  goods_location_id: 0,
  series_number: '',
  expiry_date: 0,
  price: 0,
  putaway_date: 0,
  book_qty: 0
})

const formRules = reactive<FormRules>({
  job_code: [
    { required: true, message: '请输入作业编号', trigger: 'blur' }
  ],
  sku_id: [
    { required: true, message: '请选择SKU', trigger: 'change' }
  ]
})

const countDialogVisible = ref(false)
const countFormRef = ref<FormInstance>()
const selectedStocktaking = ref<Stocktaking | null>(null)

const countFormData = reactive<StocktakingUpdate>({
  id: 0,
  job_code: '',
  sku_id: 0,
  goods_owner_id: 0,
  goods_location_id: 0,
  series_number: '',
  expiry_date: 0,
  price: 0,
  putaway_date: 0,
  book_qty: 0,
  counted_qty: 0
})

const countFormRules = reactive<FormRules>({
  counted_qty: [
    { required: true, message: '请输入盘点数量', trigger: 'blur' }
  ]
})

const detailDialogVisible = ref(false)

const getDifferenceType = (diff: number): string => {
  if (diff > 0) return 'danger'
  if (diff < 0) return 'warning'
  return 'success'
}

const fetchStocktakingList = async () => {
  loading.value = true
  try {
    const result = await stocktakingService.getPage({
      page_index: pagination.page_index,
      page_size: pagination.page_size,
      job_code: searchForm.job_code || undefined
    })
    stocktakingList.value = result.rows || []
    pagination.total = result.totals
  } catch (error: any) {
    ElMessage.error(error.message || '获取盘点列表失败')
  } finally {
    loading.value = false
  }
}

const fetchSkuList = async () => {
  try {
    skuList.value = await skuService.getList()
  } catch (error: any) {
    console.error('获取SKU列表失败', error)
  }
}

const fetchLocationList = async () => {
  try {
    const result = await warehouseLocationService.getAll(3)
    locationList.value = result
  } catch (error: any) {
    console.error('获取库位列表失败', error)
  }
}

const fetchGoodsOwnerList = async () => {
  try {
    const result = await goodsOwnerService.getAll()
    goodsOwnerList.value = result
  } catch (error: any) {
    console.error('获取货主列表失败', error)
  }
}

const handleSearch = () => {
  pagination.page_index = 1
  fetchStocktakingList()
}

const resetSearch = () => {
  searchForm.job_code = ''
  pagination.page_index = 1
  fetchStocktakingList()
}

const handleSizeChange = () => {
  fetchStocktakingList()
}

const handleCurrentChange = () => {
  fetchStocktakingList()
}

const handleAdd = () => {
  dialogTitle.value = '新增盘点'
  resetForm()
  dialogVisible.value = true
}

const handleCount = (row: Stocktaking) => {
  selectedStocktaking.value = row
  Object.assign(countFormData, {
    id: row.id,
    job_code: row.job_code,
    sku_id: row.sku_id,
    goods_owner_id: row.goods_owner_id,
    goods_location_id: row.goods_location_id,
    series_number: row.series_number,
    expiry_date: row.expiry_date,
    price: row.price,
    putaway_date: row.putaway_date,
    book_qty: row.book_qty,
    counted_qty: 0
  })
  countDialogVisible.value = true
}

const handleCountSubmit = async () => {
  if (!countFormRef.value) return
  
  await countFormRef.value.validate(async (valid) => {
    if (!valid) return
    
    submitting.value = true
    try {
      await stocktakingService.update(countFormData)
      ElMessage.success('盘点完成')
      countDialogVisible.value = false
      await fetchStocktakingList()
    } catch (error: any) {
      ElMessage.error(error.message || '盘点失败')
    } finally {
      submitting.value = false
    }
  })
}

const handleViewDetail = async (row: Stocktaking) => {
  try {
    const result = await stocktakingService.getById(row.id)
    selectedStocktaking.value = result
    detailDialogVisible.value = true
  } catch (error: any) {
    ElMessage.error(error.message || '获取详情失败')
  }
}

const handleDelete = async (id: number) => {
  try {
    await ElMessageBox.confirm('确定要删除该盘点记录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await stocktakingService.delete(id)
    ElMessage.success('删除成功')
    await fetchStocktakingList()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '删除失败')
    }
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    
    submitting.value = true
    try {
      const data: StocktakingCreate = {
        job_code: formData.job_code,
        sku_id: formData.sku_id,
        goods_owner_id: formData.goods_owner_id,
        goods_location_id: formData.goods_location_id,
        series_number: formData.series_number,
        expiry_date: expiryDate.value || 0,
        price: formData.price,
        putaway_date: putawayDate.value || 0,
        book_qty: formData.book_qty
      }
      
      await stocktakingService.create(data)
      ElMessage.success('创建成功')
      dialogVisible.value = false
      await fetchStocktakingList()
    } catch (error: any) {
      ElMessage.error(error.message || '创建失败')
    } finally {
      submitting.value = false
    }
  })
}

const resetForm = () => {
  Object.assign(formData, {
    job_code: '',
    sku_id: 0,
    goods_owner_id: 0,
    goods_location_id: 0,
    series_number: '',
    expiry_date: 0,
    price: 0,
    putaway_date: 0,
    book_qty: 0
  })
  expiryDate.value = null
  putawayDate.value = null
  formRef.value?.clearValidate()
}

onMounted(() => {
  fetchStocktakingList()
  fetchSkuList()
  fetchLocationList()
  fetchGoodsOwnerList()
})
</script>

<style scoped>
.stocktaking-management {
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
  align-items: center;
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

.count-info {
  margin-bottom: 20px;
}
</style>
