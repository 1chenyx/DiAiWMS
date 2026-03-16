<template>
  <div class="rule-config">
    <div class="toolbar">
      <el-select v-model="filterCategory" placeholder="选择类别筛选" clearable style="width: 200px; margin-right: 12px;" @change="handleFilterChange">
        <el-option v-for="cat in categoryList" :key="cat.code" :label="cat.name" :value="cat.code" />
      </el-select>
      <el-button type="primary" @click="handleAdd">
        <el-icon><Plus /></el-icon> 创建规则
      </el-button>
    </div>
    
    <el-table :data="ruleList" style="width: 100%" v-loading="loading">
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="rule_code" label="规则代码" width="150" />
      <el-table-column prop="rule_name" label="规则名称" width="150" />
      <el-table-column prop="category" label="类别" width="120" />
      <el-table-column prop="description" label="描述" show-overflow-tooltip />
      <el-table-column prop="priority" label="优先级" width="80" sortable />
      <el-table-column prop="is_active" label="状态" width="100">
        <template #default="scope">
          <el-tag :type="scope.row.is_active ? 'success' : 'danger'">
            {{ scope.row.is_active ? '激活' : '停用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="is_system" label="系统规则" width="100">
        <template #default="scope">
          <el-tag :type="scope.row.is_system ? 'warning' : 'info'">
            {{ scope.row.is_system ? '是' : '否' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="creator" label="创建人" width="100" />
      <el-table-column prop="create_time" label="创建时间" width="180">
        <template #default="scope">
          {{ formatTimestamp(scope.row.create_time) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" fixed="right" width="180">
        <template #default="scope">
          <el-button type="primary" size="small" @click="handleEdit(scope.row)" :disabled="scope.row.is_system">
            编辑
          </el-button>
          <el-button type="danger" size="small" @click="handleDelete(scope.row.id)" :disabled="scope.row.is_system">
            删除
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
    
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="700px">
      <el-form ref="formRef" :model="formData" :rules="formRules" label-width="100px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="规则代码" prop="rule_code">
              <el-input v-model="formData.rule_code" placeholder="请输入规则代码" :disabled="isEdit" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="规则名称" prop="rule_name">
              <el-input v-model="formData.rule_name" placeholder="请输入规则名称" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="规则类别" prop="category">
              <el-select v-model="formData.category" placeholder="请选择规则类别" style="width: 100%">
                <el-option v-for="cat in categoryList" :key="cat.code" :label="cat.name" :value="cat.code" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="优先级" prop="priority">
              <el-input-number v-model="formData.priority" :min="1" :max="100" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item label="描述" prop="description">
          <el-input v-model="formData.description" type="textarea" :rows="2" placeholder="请输入规则描述" />
        </el-form-item>
        
        <el-form-item label="规则内容" prop="rule_content">
          <el-input v-model="formData.rule_content" type="textarea" :rows="6" placeholder="请输入规则内容" />
        </el-form-item>
        
        <el-form-item label="激活状态" prop="is_active">
          <el-switch v-model="formData.is_active" />
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
import { Plus } from '@element-plus/icons-vue'
import { ElMessageBox, ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { 
  tenantAIRuleService,
  aiConfigService,
  type TenantAIRule,
  type TenantAIRuleCreate,
  type TenantAIRuleUpdate,
  type AIRuleCategoryInfo
} from '@/services/aiConfigService'
import { formatTimestamp } from '@/utils/format'

const loading = ref(false)
const submitting = ref(false)

const pagination = reactive({
  page_index: 1,
  page_size: 10,
  total: 0
})

const filterCategory = ref('')
const categoryList = ref<AIRuleCategoryInfo[]>([])
const ruleList = ref<TenantAIRule[]>([])

const dialogVisible = ref(false)
const dialogTitle = ref('创建规则')
const formRef = ref<FormInstance>()
const isEdit = ref(false)
const currentRuleId = ref(0)

const formData = reactive({
  rule_code: '',
  rule_name: '',
  category: '',
  description: '',
  rule_content: '',
  priority: 50,
  is_active: true
})

const formRules = reactive<FormRules>({
  rule_code: [{ required: true, message: '请输入规则代码', trigger: 'blur' }],
  rule_name: [{ required: true, message: '请输入规则名称', trigger: 'blur' }],
  category: [{ required: true, message: '请选择规则类别', trigger: 'change' }],
  rule_content: [{ required: true, message: '请输入规则内容', trigger: 'blur' }]
})

const fetchRuleCategories = async () => {
  try {
    categoryList.value = await aiConfigService.getRuleCategories()
  } catch (error: any) {
    console.error('获取规则分类失败:', error)
  }
}

const fetchRuleList = async () => {
  loading.value = true
  try {
    const result = await tenantAIRuleService.getList({
      category: filterCategory.value || undefined,
      page_index: pagination.page_index,
      page_size: pagination.page_size
    })
    ruleList.value = result.data || result.rows || []
    pagination.total = result.totals
  } catch (error: any) {
    ElMessage.error(error.message || '获取规则列表失败')
  } finally {
    loading.value = false
  }
}

const handleFilterChange = () => {
  pagination.page_index = 1
  fetchRuleList()
}

const handleSizeChange = (size: number) => {
  pagination.page_size = size
  fetchRuleList()
}

const handleCurrentChange = (current: number) => {
  pagination.page_index = current
  fetchRuleList()
}

const handleAdd = () => {
  dialogTitle.value = '创建规则'
  isEdit.value = false
  currentRuleId.value = 0
  formData.rule_code = ''
  formData.rule_name = ''
  formData.category = ''
  formData.description = ''
  formData.rule_content = ''
  formData.priority = 50
  formData.is_active = true
  dialogVisible.value = true
}

const handleEdit = (row: TenantAIRule) => {
  dialogTitle.value = '编辑规则'
  isEdit.value = true
  currentRuleId.value = row.id
  formData.rule_code = row.rule_code
  formData.rule_name = row.rule_name
  formData.category = row.category
  formData.description = row.description || ''
  formData.rule_content = row.rule_content
  formData.priority = row.priority
  formData.is_active = row.is_active
  dialogVisible.value = true
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    submitting.value = true
    
    if (isEdit.value) {
      const updateData: TenantAIRuleUpdate = {
        id: currentRuleId.value,
        rule_name: formData.rule_name,
        description: formData.description || undefined,
        rule_content: formData.rule_content,
        priority: formData.priority,
        is_active: formData.is_active
      }
      await tenantAIRuleService.update(updateData)
      ElMessage.success('更新成功')
    } else {
      const createData: TenantAIRuleCreate = {
        rule_code: formData.rule_code,
        rule_name: formData.rule_name,
        category: formData.category,
        description: formData.description || undefined,
        rule_content: formData.rule_content,
        priority: formData.priority,
        is_active: formData.is_active
      }
      await tenantAIRuleService.create(createData)
      ElMessage.success('创建成功')
    }
    
    dialogVisible.value = false
    fetchRuleList()
  } catch (error: any) {
    ElMessage.error(error.message || '操作失败')
  } finally {
    submitting.value = false
  }
}

const handleDelete = async (id: number) => {
  try {
    await ElMessageBox.confirm('确定要删除这个规则吗？', '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await tenantAIRuleService.delete(id)
    ElMessage.success('删除成功')
    fetchRuleList()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '删除失败')
    }
  }
}

onMounted(() => {
  fetchRuleCategories()
  fetchRuleList()
})
</script>

<style scoped>
.rule-config {
  padding: 0;
}

.toolbar {
  margin-bottom: 16px;
  display: flex;
  justify-content: flex-end;
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
</style>
