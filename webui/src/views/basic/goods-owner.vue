<template>
  <div class="goods-owner-management">
    <el-card shadow="hover">
      <template #header>
        <div class="card-header">
          <span>货主管理</span>
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon> 添加货主
          </el-button>
        </div>
      </template>
      
      <div class="search-section">
        <el-form :inline="true" :model="searchForm" class="search-form">
          <el-form-item label="货主名称">
            <el-input v-model="searchForm.goods_owner_name" placeholder="请输入货主名称" clearable />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleSearch">搜索</el-button>
            <el-button @click="resetSearch">重置</el-button>
          </el-form-item>
        </el-form>
      </div>
      
      <el-table :data="goodsOwnerList" style="width: 100%" v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="goods_owner_name" label="货主名称" />
        <el-table-column prop="goods_owner_code" label="货主编码" />
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
        <el-form-item label="货主名称" prop="goods_owner_name">
          <el-input v-model="formData.goods_owner_name" placeholder="请输入货主名称" />
        </el-form-item>
        <el-form-item label="货主编码" prop="goods_owner_code">
          <el-input v-model="formData.goods_owner_code" placeholder="请输入货主编码" />
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
import { goodsOwnerService, type GoodsOwner } from '@/services/goodsOwnerService'

const loading = ref(false)
const submitting = ref(false)

const searchForm = reactive({
  goods_owner_name: ''
})

const pagination = reactive({
  page_index: 1,
  page_size: 10,
  total: 0
})

const goodsOwnerList = ref<GoodsOwner[]>([])

const dialogVisible = ref(false)
const dialogTitle = ref('添加货主')
const formRef = ref<FormInstance>()

const formData = reactive({
  id: 0,
  goods_owner_name: '',
  goods_owner_code: '',
  contact: '',
  phone: '',
  email: '',
  address: '',
  description: '',
  is_valid: true
})

const formRules = reactive<FormRules>({
  goods_owner_name: [
    { required: true, message: '请输入货主名称', trigger: 'blur' }
  ],
  goods_owner_code: [
    { required: true, message: '请输入货主编码', trigger: 'blur' }
  ]
})

const fetchGoodsOwnerList = async () => {
  loading.value = true
  try {
    const result = await goodsOwnerService.getPage({
      page_index: pagination.page_index,
      page_size: pagination.page_size,
      goods_owner_name: searchForm.goods_owner_name || undefined
    })
    goodsOwnerList.value = result.rows
    pagination.total = result.totals
  } catch (error: any) {
    ElMessage.error(error.message || '获取货主列表失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.page_index = 1
  fetchGoodsOwnerList()
}

const resetSearch = () => {
  searchForm.goods_owner_name = ''
  pagination.page_index = 1
  fetchGoodsOwnerList()
}

const handleSizeChange = (size: number) => {
  pagination.page_size = size
  fetchGoodsOwnerList()
}

const handleCurrentChange = (current: number) => {
  pagination.page_index = current
  fetchGoodsOwnerList()
}

const handleAdd = () => {
  dialogTitle.value = '添加货主'
  formData.id = 0
  formData.goods_owner_name = ''
  formData.goods_owner_code = ''
  formData.contact = ''
  formData.phone = ''
  formData.email = ''
  formData.address = ''
  formData.description = ''
  formData.is_valid = true
  dialogVisible.value = true
}

const handleEdit = (row: GoodsOwner) => {
  dialogTitle.value = '编辑货主'
  formData.id = row.id
  formData.goods_owner_name = row.goods_owner_name
  formData.goods_owner_code = row.goods_owner_code
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
    await ElMessageBox.confirm('确定要删除这个货主吗？', '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await goodsOwnerService.delete(id)
    ElMessage.success('删除成功')
    fetchGoodsOwnerList()
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
      await goodsOwnerService.update({
        id: formData.id,
        goods_owner_name: formData.goods_owner_name,
        goods_owner_code: formData.goods_owner_code,
        contact: formData.contact,
        phone: formData.phone,
        email: formData.email,
        address: formData.address,
        description: formData.description,
        is_valid: formData.is_valid
      })
      ElMessage.success('更新成功')
    } else {
      await goodsOwnerService.create({
        goods_owner_name: formData.goods_owner_name,
        goods_owner_code: formData.goods_owner_code,
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
    fetchGoodsOwnerList()
  } catch (error: any) {
    ElMessage.error(error.message || '操作失败')
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  fetchGoodsOwnerList()
})
</script>

<style scoped>
.goods-owner-management {
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
