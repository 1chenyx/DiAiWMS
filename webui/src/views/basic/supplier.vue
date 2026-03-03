<template>
  <div class="supplier-management">
    <el-card shadow="hover">
      <template #header>
        <div class="card-header">
          <span>供应商管理</span>
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon> 添加供应商
          </el-button>
        </div>
      </template>
      
      <div class="search-section">
        <el-form :inline="true" :model="searchForm" class="search-form">
          <el-form-item label="供应商名称">
            <el-input v-model="searchForm.supplier_name" placeholder="请输入供应商名称" clearable />
          </el-form-item>
          <el-form-item label="状态">
            <el-select v-model="searchForm.is_valid" placeholder="请选择状态" clearable>
              <el-option label="启用" :value="true" />
              <el-option label="禁用" :value="false" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleSearch">搜索</el-button>
            <el-button @click="resetSearch">重置</el-button>
          </el-form-item>
        </el-form>
      </div>
      
      <el-table :data="supplierList" style="width: 100%" v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="supplier_name" label="供应商名称" />
        <el-table-column prop="supplier_code" label="供应商编码" />
        <el-table-column prop="contact" label="联系人" />
        <el-table-column prop="phone" label="联系电话" />
        <el-table-column prop="email" label="邮箱" />
        <el-table-column prop="address" label="地址" />
        <el-table-column prop="is_valid" label="状态" width="80">
          <template #default="scope">
            <el-tag :type="scope.row.is_valid ? 'success' : 'danger'">
              {{ scope.row.is_valid ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="create_time" label="创建时间" />
        <el-table-column label="操作" fixed="right">
          <template #default="scope">
            <el-button type="primary" size="small" @click="handleEdit(scope.row)">
              <el-icon><Edit /></el-icon> 编辑
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
    
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="600px">
      <el-form ref="formRef" :model="formData" :rules="formRules" label-width="100px">
        <el-form-item label="供应商名称" prop="supplier_name">
          <el-input v-model="formData.supplier_name" placeholder="请输入供应商名称" />
        </el-form-item>
        <el-form-item label="供应商编码" prop="supplier_code">
          <el-input v-model="formData.supplier_code" placeholder="请输入供应商编码" />
        </el-form-item>
        <el-form-item label="联系人" prop="contact">
          <el-input v-model="formData.contact" placeholder="请输入联系人" />
        </el-form-item>
        <el-form-item label="联系电话" prop="phone">
          <el-input v-model="formData.phone" placeholder="请输入联系电话" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="formData.email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item label="地址" prop="address">
          <el-input v-model="formData.address" placeholder="请输入地址" type="textarea" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="formData.description" placeholder="请输入描述" type="textarea" />
        </el-form-item>
        <el-form-item label="状态" prop="is_valid">
          <el-switch v-model="formData.is_valid" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmit" :loading="submitting">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { Plus, Edit, Delete } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { supplierService, type Supplier, type SupplierCreate, type SupplierUpdate } from '@/services/supplierService'

const loading = ref(false)
const submitting = ref(false)

const searchForm = reactive({
  supplier_name: '',
  is_valid: undefined as boolean | undefined
})

const pagination = reactive({
  page_index: 1,
  page_size: 10,
  total: 0
})

const supplierList = ref<Supplier[]>([])

const dialogVisible = ref(false)
const dialogTitle = ref('添加供应商')
const formRef = ref<FormInstance>()
const editingId = ref<number | null>(null)

const formData = reactive<SupplierCreate & { is_valid: boolean }>({
  supplier_name: '',
  supplier_code: '',
  contact: '',
  phone: '',
  email: '',
  address: '',
  description: '',
  is_valid: true
})

const formRules = reactive<FormRules>({
  supplier_name: [{ required: true, message: '请输入供应商名称', trigger: 'blur' }],
  supplier_code: [{ required: true, message: '请输入供应商编码', trigger: 'blur' }]
})

const fetchData = async () => {
  loading.value = true
  try {
    const result = await supplierService.getPage({
      page_index: pagination.page_index,
      page_size: pagination.page_size,
      supplier_name: searchForm.supplier_name || undefined,
      is_valid: searchForm.is_valid
    })
    supplierList.value = result.rows
    pagination.total = result.totals
  } catch (error) {
    console.error('获取供应商列表失败:', error)
    ElMessage.error('获取供应商列表失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.page_index = 1
  fetchData()
}

const resetSearch = () => {
  searchForm.supplier_name = ''
  searchForm.is_valid = undefined
  handleSearch()
}

const handleSizeChange = (size: number) => {
  pagination.page_size = size
  fetchData()
}

const handleCurrentChange = (current: number) => {
  pagination.page_index = current
  fetchData()
}

const handleAdd = () => {
  dialogTitle.value = '添加供应商'
  editingId.value = null
  formData.supplier_name = ''
  formData.supplier_code = ''
  formData.contact = ''
  formData.phone = ''
  formData.email = ''
  formData.address = ''
  formData.description = ''
  formData.is_valid = true
  dialogVisible.value = true
}

const handleEdit = (row: Supplier) => {
  dialogTitle.value = '编辑供应商'
  editingId.value = row.id
  formData.supplier_name = row.supplier_name
  formData.supplier_code = row.supplier_code
  formData.contact = row.contact || ''
  formData.phone = row.phone || ''
  formData.email = row.email || ''
  formData.address = row.address || ''
  formData.description = row.description || ''
  formData.is_valid = row.is_valid
  dialogVisible.value = true
}

const handleDelete = async (id: number) => {
  try {
    await ElMessageBox.confirm('确定要删除这个供应商吗？', '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await supplierService.delete(id)
    ElMessage.success('删除成功')
    fetchData()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    submitting.value = true
    
    if (editingId.value) {
      const updateData: SupplierUpdate = {
        id: editingId.value,
        supplier_name: formData.supplier_name,
        supplier_code: formData.supplier_code,
        contact: formData.contact,
        phone: formData.phone,
        email: formData.email,
        address: formData.address,
        description: formData.description,
        is_valid: formData.is_valid
      }
      await supplierService.update(updateData)
      ElMessage.success('更新成功')
    } else {
      await supplierService.create(formData)
      ElMessage.success('创建成功')
    }
    
    dialogVisible.value = false
    fetchData()
  } catch (error) {
    console.error('提交失败:', error)
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.supplier-management {
  padding: 20px 0;
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
  gap: 10px;
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
