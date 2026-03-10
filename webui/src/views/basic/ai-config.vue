<template>
  <div class="ai-config-management">
    <el-card shadow="hover">
      <template #header>
        <div class="card-header">
          <span>AI配置</span>
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon> 添加配置
          </el-button>
        </div>
      </template>
      
      <el-table :data="configList" style="width: 100%" v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="provider_name" label="AI提供商" />
        <el-table-column prop="model_name" label="模型" />
        <el-table-column prop="api_endpoint" label="API端点" show-overflow-tooltip />
        <el-table-column prop="is_default" label="默认配置" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.is_default ? 'success' : 'info'">
              {{ scope.row.is_default ? '是' : '否' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="creator" label="创建人" />
        <el-table-column prop="create_time" label="创建时间">
          <template #default="scope">
            {{ formatTimestamp(scope.row.create_time) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" fixed="right" width="200">
          <template #default="scope">
            <el-button v-if="!scope.row.is_default" type="success" size="small" @click="handleSetDefault(scope.row.id)">
              设为默认
            </el-button>
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
          v-model:current-page="pagination.page"
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
        <el-form-item label="AI提供商" prop="provider_code">
          <el-select 
            v-model="formData.provider_code" 
            placeholder="请选择AI提供商" 
            style="width: 100%"
            @change="handleProviderChange"
          >
            <el-option 
              v-for="provider in providerList" 
              :key="provider.code" 
              :label="provider.name" 
              :value="provider.code" 
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="AI模型" prop="model_code">
          <el-select 
            v-model="formData.model_code" 
            placeholder="请选择AI模型" 
            style="width: 100%"
            :disabled="!formData.provider_code"
          >
            <el-option 
              v-for="model in modelList" 
              :key="model.code" 
              :label="model.name" 
              :value="model.code" 
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="API密钥" prop="api_key">
          <el-input 
            v-model="formData.api_key" 
            placeholder="请输入API密钥" 
            type="password" 
            show-password
          />
        </el-form-item>
        
        <el-form-item label="API端点" prop="api_endpoint">
          <el-input v-model="formData.api_endpoint" placeholder="请输入API端点URL（可选）" />
        </el-form-item>
        
        <el-form-item label="设为默认" prop="is_default">
          <el-switch v-model="formData.is_default" />
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
import { ref, reactive, onMounted, computed } from 'vue'
import { Plus, Edit, Delete } from '@element-plus/icons-vue'
import { ElMessageBox, ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { 
  aiConfigService, 
  tenantAIConfigService, 
  type AIProviderInfo, 
  type AIModelInfo,
  type TenantAIConfig,
  type TenantAIConfigCreate,
  type TenantAIConfigUpdate
} from '@/services/aiConfigService'
import { formatTimestamp } from '@/utils/format'

const loading = ref(false)
const submitting = ref(false)

const pagination = reactive({
  page: 1,
  page_size: 10,
  total: 0
})

const configList = ref<TenantAIConfig[]>([])
const providerList = ref<AIProviderInfo[]>([])
const providerModelsMap = ref<Map<string, AIModelInfo[]>>(new Map())

const dialogVisible = ref(false)
const dialogTitle = ref('添加配置')
const formRef = ref<FormInstance>()
const isEdit = ref(false)
const currentConfigId = ref(0)

const formData = reactive({
  provider_code: '',
  model_code: '',
  api_key: '',
  api_endpoint: '',
  is_default: false
})

const formRules = reactive<FormRules>({
  provider_code: [
    { required: true, message: '请选择AI提供商', trigger: 'change' }
  ],
  model_code: [
    { required: true, message: '请选择AI模型', trigger: 'change' }
  ],
  api_key: [
    { required: true, message: '请输入API密钥', trigger: 'blur' }
  ]
})

const modelList = computed(() => {
  if (!formData.provider_code) return []
  return providerModelsMap.value.get(formData.provider_code) || []
})

const fetchConfigList = async () => {
  loading.value = true
  try {
    const result = await tenantAIConfigService.getList({
      page: pagination.page,
      page_size: pagination.page_size
    })
    configList.value = result.rows || []
    pagination.total = result.totals
  } catch (error: any) {
    ElMessage.error(error.message || '获取配置列表失败')
  } finally {
    loading.value = false
  }
}

const fetchProviders = async () => {
  try {
    const result = await aiConfigService.getProviders()
    providerList.value = result
  } catch (error: any) {
    console.error('获取AI提供商列表失败:', error)
  }
}

const fetchProvidersWithModels = async () => {
  try {
    const result = await aiConfigService.getProvidersWithModels()
    result.forEach(provider => {
      providerModelsMap.value.set(provider.code, provider.models)
    })
  } catch (error: any) {
    console.error('获取AI提供商及模型失败:', error)
  }
}

const handleProviderChange = () => {
  formData.model_code = ''
}

const handleSizeChange = (size: number) => {
  pagination.page_size = size
  fetchConfigList()
}

const handleCurrentChange = (current: number) => {
  pagination.page = current
  fetchConfigList()
}

const handleAdd = () => {
  dialogTitle.value = '添加配置'
  isEdit.value = false
  currentConfigId.value = 0
  formData.provider_code = ''
  formData.model_code = ''
  formData.api_key = ''
  formData.api_endpoint = ''
  formData.is_default = false
  dialogVisible.value = true
}

const handleEdit = (row: TenantAIConfig) => {
  dialogTitle.value = '编辑配置'
  isEdit.value = true
  currentConfigId.value = row.id
  formData.provider_code = row.provider_code
  formData.model_code = row.model_code
  formData.api_key = row.api_key
  formData.api_endpoint = row.api_endpoint || ''
  formData.is_default = row.is_default
  dialogVisible.value = true
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    submitting.value = true
    
    if (isEdit.value) {
      const updateData: TenantAIConfigUpdate = {
        id: currentConfigId.value,
        api_key: formData.api_key,
        api_endpoint: formData.api_endpoint || undefined,
        is_default: formData.is_default
      }
      await tenantAIConfigService.update(updateData)
      ElMessage.success('更新成功')
    } else {
      const createData: TenantAIConfigCreate = {
        provider_code: formData.provider_code,
        model_code: formData.model_code,
        api_key: formData.api_key,
        api_endpoint: formData.api_endpoint || undefined,
        is_default: formData.is_default
      }
      await tenantAIConfigService.create(createData)
      ElMessage.success('创建成功')
    }
    
    dialogVisible.value = false
    fetchConfigList()
  } catch (error: any) {
    ElMessage.error(error.message || '操作失败')
  } finally {
    submitting.value = false
  }
}

const handleSetDefault = async (id: number) => {
  try {
    await ElMessageBox.confirm('确定要将此配置设为默认吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'info'
    })
    
    await tenantAIConfigService.setDefault(id)
    ElMessage.success('设置成功')
    fetchConfigList()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '设置失败')
    }
  }
}

const handleDelete = async (id: number) => {
  try {
    await ElMessageBox.confirm('确定要删除这个配置吗？', '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await tenantAIConfigService.delete(id)
    ElMessage.success('删除成功')
    fetchConfigList()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '删除失败')
    }
  }
}

onMounted(() => {
  fetchConfigList()
  fetchProviders()
  fetchProvidersWithModels()
})
</script>

<style scoped>
.ai-config-management {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
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
