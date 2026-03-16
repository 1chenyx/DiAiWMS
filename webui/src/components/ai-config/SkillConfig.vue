<template>
  <div class="skill-config">
    <div class="toolbar">
      <el-select v-model="filterSkillType" placeholder="选择类型筛选" clearable style="width: 200px; margin-right: 12px;" @change="handleFilterChange">
        <el-option v-for="type in skillTypeList" :key="type" :label="type" :value="type" />
      </el-select>
      <el-button type="primary" @click="handleAdd">
        <el-icon><Plus /></el-icon> 创建技能
      </el-button>
      <el-button type="success" @click="handleGenerate">
        <el-icon><MagicStick /></el-icon> AI生成
      </el-button>
    </div>
    
    <el-table :data="skillList" style="width: 100%" v-loading="loading">
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="skill_code" label="技能代码" width="150" />
      <el-table-column prop="skill_name" label="技能名称" width="150" />
      <el-table-column prop="skill_type" label="类型" width="120" />
      <el-table-column prop="description" label="描述" show-overflow-tooltip />
      <el-table-column prop="is_active" label="状态" width="100">
        <template #default="scope">
          <el-tag :type="scope.row.is_active ? 'success' : 'danger'">
            {{ scope.row.is_active ? '激活' : '停用' }}
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
          <el-button type="primary" size="small" @click="handleEdit(scope.row)">
            编辑
          </el-button>
          <el-button type="danger" size="small" @click="handleDelete(scope.row.id)">
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
            <el-form-item label="技能代码" prop="skill_code">
              <el-input v-model="formData.skill_code" placeholder="请输入技能代码" :disabled="isEdit" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="技能名称" prop="skill_name">
              <el-input v-model="formData.skill_name" placeholder="请输入技能名称" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="技能类型" prop="skill_type">
              <el-select v-model="formData.skill_type" placeholder="请选择技能类型" style="width: 100%">
                <el-option v-for="type in skillTypeList" :key="type" :label="type" :value="type" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="激活状态" prop="is_active">
              <el-switch v-model="formData.is_active" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item label="描述" prop="description">
          <el-input v-model="formData.description" type="textarea" :rows="2" placeholder="请输入技能描述" />
        </el-form-item>
        
        <el-form-item label="提示模板" prop="prompt_template">
          <el-input v-model="formData.prompt_template" type="textarea" :rows="5" placeholder="请输入提示词模板" />
        </el-form-item>
        
        <el-form-item label="关联工具" prop="tools">
          <el-input v-model="formData.tools" type="textarea" :rows="2" placeholder="请输入关联工具代码，多个用逗号分隔" />
        </el-form-item>
        
        <el-form-item label="关联规则" prop="rules">
          <el-input v-model="formData.rules" type="textarea" :rows="2" placeholder="请输入关联规则代码，多个用逗号分隔" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmit" :loading="submitting">确定</el-button>
        </span>
      </template>
    </el-dialog>
    
    <el-dialog v-model="generateDialogVisible" title="AI智能生成技能" width="600px">
      <el-form ref="generateFormRef" :model="generateFormData" :rules="generateFormRules" label-width="100px">
        <el-form-item label="技能名称" prop="skill_name">
          <el-input v-model="generateFormData.skill_name" placeholder="请输入技能名称" />
        </el-form-item>
        
        <el-form-item label="技能类型" prop="skill_type">
          <el-select v-model="generateFormData.skill_type" placeholder="请选择技能类型" style="width: 100%">
            <el-option v-for="type in skillTypeList" :key="type" :label="type" :value="type" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="功能描述" prop="description">
          <el-input v-model="generateFormData.description" type="textarea" :rows="3" placeholder="请详细描述技能的功能和用途" />
        </el-form-item>
        
        <el-form-item label="业务上下文" prop="business_context">
          <el-input v-model="generateFormData.business_context" type="textarea" :rows="3" placeholder="请输入业务上下文信息（可选）" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="generateDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleGenerateSubmit" :loading="generating">生成</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { Plus, MagicStick } from '@element-plus/icons-vue'
import { ElMessageBox, ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { 
  tenantAISkillService, 
  type TenantAISkill,
  type TenantAISkillCreate,
  type TenantAISkillUpdate,
  type SkillGenerateRequest
} from '@/services/aiConfigService'
import { formatTimestamp } from '@/utils/format'

const loading = ref(false)
const submitting = ref(false)
const generating = ref(false)

const pagination = reactive({
  page_index: 1,
  page_size: 10,
  total: 0
})

const filterSkillType = ref('')
const skillTypeList = ref<string[]>(['库存查询', '订单处理', '数据分析', '报表生成', '智能推荐', '异常处理'])
const skillList = ref<TenantAISkill[]>([])

const dialogVisible = ref(false)
const dialogTitle = ref('创建技能')
const formRef = ref<FormInstance>()
const isEdit = ref(false)
const currentSkillId = ref(0)

const formData = reactive({
  skill_code: '',
  skill_name: '',
  skill_type: '',
  description: '',
  prompt_template: '',
  tools: '',
  rules: '',
  is_active: true
})

const formRules = reactive<FormRules>({
  skill_code: [{ required: true, message: '请输入技能代码', trigger: 'blur' }],
  skill_name: [{ required: true, message: '请输入技能名称', trigger: 'blur' }],
  skill_type: [{ required: true, message: '请选择技能类型', trigger: 'change' }]
})

const generateDialogVisible = ref(false)
const generateFormRef = ref<FormInstance>()
const generateFormData = reactive({
  skill_name: '',
  skill_type: '',
  description: '',
  business_context: ''
})

const generateFormRules = reactive<FormRules>({
  skill_name: [{ required: true, message: '请输入技能名称', trigger: 'blur' }],
  skill_type: [{ required: true, message: '请选择技能类型', trigger: 'change' }],
  description: [{ required: true, message: '请输入功能描述', trigger: 'blur' }]
})

const fetchSkillList = async () => {
  loading.value = true
  try {
    const result = await tenantAISkillService.getList({
      skill_type: filterSkillType.value || undefined,
      page_index: pagination.page_index,
      page_size: pagination.page_size
    })
    skillList.value = result.data || result.rows || []
    pagination.total = result.totals
  } catch (error: any) {
    ElMessage.error(error.message || '获取技能列表失败')
  } finally {
    loading.value = false
  }
}

const handleFilterChange = () => {
  pagination.page_index = 1
  fetchSkillList()
}

const handleSizeChange = (size: number) => {
  pagination.page_size = size
  fetchSkillList()
}

const handleCurrentChange = (current: number) => {
  pagination.page_index = current
  fetchSkillList()
}

const handleAdd = () => {
  dialogTitle.value = '创建技能'
  isEdit.value = false
  currentSkillId.value = 0
  formData.skill_code = ''
  formData.skill_name = ''
  formData.skill_type = ''
  formData.description = ''
  formData.prompt_template = ''
  formData.tools = ''
  formData.rules = ''
  formData.is_active = true
  dialogVisible.value = true
}

const handleEdit = (row: TenantAISkill) => {
  dialogTitle.value = '编辑技能'
  isEdit.value = true
  currentSkillId.value = row.id
  formData.skill_code = row.skill_code
  formData.skill_name = row.skill_name
  formData.skill_type = row.skill_type
  formData.description = row.description || ''
  formData.prompt_template = row.prompt_template || ''
  formData.tools = row.tools || ''
  formData.rules = row.rules || ''
  formData.is_active = row.is_active
  dialogVisible.value = true
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    submitting.value = true
    
    if (isEdit.value) {
      const updateData: TenantAISkillUpdate = {
        id: currentSkillId.value,
        skill_name: formData.skill_name,
        description: formData.description || undefined,
        prompt_template: formData.prompt_template || undefined,
        tools: formData.tools || undefined,
        rules: formData.rules || undefined,
        is_active: formData.is_active
      }
      await tenantAISkillService.update(updateData)
      ElMessage.success('更新成功')
    } else {
      const createData: TenantAISkillCreate = {
        skill_code: formData.skill_code,
        skill_name: formData.skill_name,
        skill_type: formData.skill_type,
        description: formData.description || undefined,
        prompt_template: formData.prompt_template || undefined,
        tools: formData.tools || undefined,
        rules: formData.rules || undefined,
        is_active: formData.is_active
      }
      await tenantAISkillService.create(createData)
      ElMessage.success('创建成功')
    }
    
    dialogVisible.value = false
    fetchSkillList()
  } catch (error: any) {
    ElMessage.error(error.message || '操作失败')
  } finally {
    submitting.value = false
  }
}

const handleDelete = async (id: number) => {
  try {
    await ElMessageBox.confirm('确定要删除这个技能吗？', '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await tenantAISkillService.delete(id)
    ElMessage.success('删除成功')
    fetchSkillList()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '删除失败')
    }
  }
}

const handleGenerate = () => {
  generateFormData.skill_name = ''
  generateFormData.skill_type = ''
  generateFormData.description = ''
  generateFormData.business_context = ''
  generateDialogVisible.value = true
}

const handleGenerateSubmit = async () => {
  if (!generateFormRef.value) return
  
  try {
    await generateFormRef.value.validate()
    generating.value = true
    
    const request: SkillGenerateRequest = {
      skill_name: generateFormData.skill_name,
      skill_type: generateFormData.skill_type,
      description: generateFormData.description,
      business_context: generateFormData.business_context || undefined
    }
    
    const result = await tenantAISkillService.generate(request)
    ElMessage.success('AI生成成功')
    
    generateDialogVisible.value = false
    
    formData.skill_code = result.skill_code
    formData.skill_name = result.skill_name
    formData.skill_type = result.skill_type
    formData.description = result.description || ''
    formData.prompt_template = result.prompt_template || ''
    formData.tools = result.tools || ''
    formData.rules = result.rules || ''
    formData.is_active = result.is_active ?? true
    isEdit.value = false
    currentSkillId.value = 0
    dialogTitle.value = '创建技能（AI生成）'
    dialogVisible.value = true
    
  } catch (error: any) {
    ElMessage.error(error.message || 'AI生成失败')
  } finally {
    generating.value = false
  }
}

onMounted(() => {
  fetchSkillList()
})
</script>

<style scoped>
.skill-config {
  padding: 0;
}

.toolbar {
  margin-bottom: 16px;
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 12px;
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
