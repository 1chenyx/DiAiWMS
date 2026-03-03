<template>
  <div class="customer-management">
    <el-card shadow="hover">
      <template #header>
        <div class="card-header">
          <span>客户管理</span>
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon> 添加客户
          </el-button>
        </div>
      </template>
      
      <div class="search-section">
        <el-form :inline="true" :model="searchForm" class="search-form">
          <el-form-item label="客户名称">
            <el-input v-model="searchForm.customer_name" placeholder="请输入客户名称" clearable />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleSearch">搜索</el-button>
            <el-button @click="resetSearch">重置</el-button>
          </el-form-item>
        </el-form>
      </div>
      
      <el-table :data="customerList" style="width: 100%" v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="customer_name" label="客户名称" />
        <el-table-column prop="customer_code" label="客户编码" />
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
    
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="100px"
      >
        <el-form-item label="客户名称" prop="customer_name">
          <el-input v-model="formData.customer_name" placeholder="请输入客户名称" />
        </el-form-item>
        <el-form-item label="客户编码" prop="customer_code">
          <el-input v-model="formData.customer_code" placeholder="请输入客户编码" />
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
import { ElMessageBox, ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { customerService, type Customer } from '@/services/customerService'

const loading = ref(false)
const submitting = ref(false)

const searchForm = reactive({
  customer_name: ''
})

const pagination = reactive({
  page_index: 1,
  page_size: 10,
  total: 0
})

const customerList = ref<Customer[]>([])

const dialogVisible = ref(false)
const dialogTitle = ref('添加客户')
const formRef = ref<FormInstance>()

const formData = reactive({
  id: 0,
  customer_name: '',
  customer_code: '',
  contact: '',
  phone: '',
  email: '',
  address: '',
  description: '',
  is_valid: true
})

const formRules = reactive<FormRules>({
  customer_name: [
    { required: true, message: '请输入客户名称', trigger: 'blur' }
  ],
  customer_code: [
    { required: true, message: '请输入客户编码', trigger: 'blur' }
  ]
})

const fetchCustomerList = async () => {
  loading.value = true
  try {
    const result = await customerService.getPage({
      page_index: pagination.page_index,
      page_size: pagination.page_size,
      customer_name: searchForm.customer_name || undefined
    })
    customerList.value = result.rows
    pagination.total = result.totals
  } catch (error: any) {
    ElMessage.error(error.message || '获取客户列表失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.page_index = 1
  fetchCustomerList()
}

const resetSearch = () => {
  searchForm.customer_name = ''
  pagination.page_index = 1
  fetchCustomerList()
}

const handleSizeChange = (size: number) => {
  pagination.page_size = size
  fetchCustomerList()
}

const handleCurrentChange = (current: number) => {
  pagination.page_index = current
  fetchCustomerList()
}

const handleAdd = () => {
  dialogTitle.value = '添加客户'
  formData.id = 0
  formData.customer_name = ''
  formData.customer_code = ''
  formData.contact = ''
  formData.phone = ''
  formData.email = ''
  formData.address = ''
  formData.description = ''
  formData.is_valid = true
  dialogVisible.value = true
}

const handleEdit = (row: Customer) => {
  dialogTitle.value = '编辑客户'
  formData.id = row.id
  formData.customer_name = row.customer_name
  formData.customer_code = row.customer_code
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
    await ElMessageBox.confirm('确定要删除这个客户吗？', '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await customerService.delete(id)
    ElMessage.success('删除成功')
    fetchCustomerList()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '删除失败')
    }
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    submitting.value = true
    
    if (formData.id) {
      await customerService.update({
        id: formData.id,
        customer_name: formData.customer_name,
        customer_code: formData.customer_code,
        contact: formData.contact,
        phone: formData.phone,
        email: formData.email,
        address: formData.address,
        description: formData.description,
        is_valid: formData.is_valid
      })
      ElMessage.success('更新成功')
    } else {
      await customerService.create({
        customer_name: formData.customer_name,
        customer_code: formData.customer_code,
        contact: formData.contact,
        phone: formData.phone,
        email: formData.email,
        address: formData.address,
        description: formData.description,
        is_valid: formData.is_valid
      })
      ElMessage.success('创建成功')
    }
    
    dialogVisible.value = false
    fetchCustomerList()
  } catch (error: any) {
    ElMessage.error(error.message || '操作失败')
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  fetchCustomerList()
})
</script>

<style scoped>
.customer-management {
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
</style>
