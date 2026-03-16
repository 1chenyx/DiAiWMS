<template>
  <div class="tool-config">
    <div class="toolbar">
      <el-select v-model="filterCategory" placeholder="选择分类筛选" clearable style="width: 200px; margin-right: 12px;" @change="handleFilterChange">
        <el-option v-for="cat in categoryList" :key="cat.code" :label="cat.name" :value="cat.code" />
      </el-select>
      <el-input v-model="searchKeyword" placeholder="搜索工具名称或代码" style="width: 250px;" clearable @input="handleSearch">
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>
    </div>
    
    <div class="tool-stats">
      <el-tag type="info">系统工具: {{ filteredSystemTools.length }}</el-tag>
      <el-tag type="success">已激活: {{ activatedToolCodes.size }}</el-tag>
    </div>
    
    <div class="tool-grid" v-loading="loading">
      <div
        v-for="tool in filteredSystemTools"
        :key="tool.code"
        :class="['tool-card', { activated: isActivated(tool.code) }]"
      >
        <div class="tool-header">
          <div class="tool-icon">
            <el-icon :size="24"><Tools /></el-icon>
          </div>
          <div class="tool-title">
            <h4>{{ tool.name }}</h4>
            <el-tag size="small" :type="getCategoryTagType(tool.category)">{{ getCategoryName(tool.category) }}</el-tag>
          </div>
        </div>
        
        <div class="tool-body">
          <p class="tool-code">代码: {{ tool.code }}</p>
          <p class="tool-desc">{{ tool.description || '暂无描述' }}</p>
        </div>
        
        <div class="tool-footer">
          <template v-if="isActivated(tool.code)">
            <el-button type="success" size="small" disabled>
              <el-icon><Check /></el-icon> 已激活
            </el-button>
            <el-button type="warning" size="small" @click="handleConfig(tool)">
              <el-icon><Setting /></el-icon> 配置
            </el-button>
            <el-button type="danger" size="small" @click="handleDeactivate(tool.code)">
              <el-icon><Close /></el-icon> 停用
            </el-button>
          </template>
          <template v-else>
            <el-button type="primary" size="small" @click="handleActivate(tool)">
              <el-icon><Plus /></el-icon> 激活
            </el-button>
          </template>
        </div>
      </div>
    </div>
    
    <el-empty v-if="!loading && filteredSystemTools.length === 0" description="没有找到工具" />
    
    <el-dialog v-model="configDialogVisible" title="工具配置" width="500px">
      <el-form ref="configFormRef" :model="configFormData" label-width="100px">
        <el-form-item label="工具代码">
          <el-input v-model="configFormData.tool_code" disabled />
        </el-form-item>
        <el-form-item label="工具名称">
          <el-input v-model="configFormData.tool_name" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="configFormData.description" type="textarea" :rows="2" />
        </el-form-item>
        <el-form-item label="配置JSON">
          <el-input v-model="configFormData.config" type="textarea" :rows="5" placeholder="请输入工具配置JSON（可选）" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="configDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveConfig" :loading="saving">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { Plus, Setting, Check, Close, Search, Tools } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance } from 'element-plus'
import { 
  tenantAIToolService,
  aiConfigService,
  type SystemAITool,
  type AIToolCategoryInfo,
  type TenantAITool,
  type TenantAIToolUpdate
} from '@/services/aiConfigService'

const loading = ref(false)
const saving = ref(false)

const systemTools = ref<SystemAITool[]>([])
const activatedTools = ref<TenantAITool[]>([])
const categoryList = ref<AIToolCategoryInfo[]>([])
const filterCategory = ref('')
const searchKeyword = ref('')

const configDialogVisible = ref(false)
const configFormRef = ref<FormInstance>()
const configFormData = ref({
  tool_code: '',
  tool_name: '',
  description: '',
  config: ''
})

const activatedToolCodes = computed(() => {
  return new Set(activatedTools.value.map(t => t.tool_code))
})

const filteredSystemTools = computed(() => {
  let tools = systemTools.value
  
  if (filterCategory.value) {
    tools = tools.filter(t => t.category === filterCategory.value)
  }
  
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    tools = tools.filter(t => 
      t.name.toLowerCase().includes(keyword) || 
      t.code.toLowerCase().includes(keyword)
    )
  }
  
  return tools
})

const isActivated = (toolCode: string) => {
  return activatedToolCodes.value.has(toolCode)
}

const getCategoryName = (categoryCode: string) => {
  const cat = categoryList.value.find(c => c.code === categoryCode)
  return cat?.name || categoryCode
}

const getCategoryTagType = (categoryCode: string): 'success' | 'warning' | 'info' | 'danger' | '' => {
  const types: Record<string, 'success' | 'warning' | 'info' | 'danger'> = {
    'data': 'success',
    'operation': 'warning',
    'integration': 'info',
    'analysis': 'danger'
  }
  return types[categoryCode] || 'info'
}

const fetchData = async () => {
  loading.value = true
  try {
    const [toolsResult, activatedResult, categoriesResult] = await Promise.all([
      aiConfigService.getSystemTools(),
      tenantAIToolService.getActive(),
      aiConfigService.getToolCategories()
    ])
    
    systemTools.value = toolsResult || []
    activatedTools.value = activatedResult || []
    categoryList.value = categoriesResult || []
  } catch (error: any) {
    ElMessage.error(error.message || '获取数据失败')
  } finally {
    loading.value = false
  }
}

const handleFilterChange = () => {
  // 筛选已通过computed自动处理
}

const handleSearch = () => {
  // 搜索已通过computed自动处理
}

const handleActivate = async (tool: SystemAITool) => {
  try {
    await tenantAIToolService.activate({
      tool_code: tool.code,
      tool_name: tool.name,
      tool_category: tool.category,
      description: tool.description
    })
    ElMessage.success('激活成功')
    await fetchData()
  } catch (error: any) {
    ElMessage.error(error.message || '激活失败')
  }
}

const handleDeactivate = async (toolCode: string) => {
  try {
    await ElMessageBox.confirm('确定要停用这个工具吗？', '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    const tool = activatedTools.value.find(t => t.tool_code === toolCode)
    if (tool) {
      await tenantAIToolService.deactivate(tool.id)
      ElMessage.success('停用成功')
      await fetchData()
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '停用失败')
    }
  }
}

const handleConfig = (tool: SystemAITool) => {
  const activatedTool = activatedTools.value.find(t => t.tool_code === tool.code)
  if (activatedTool) {
    configFormData.value = {
      tool_code: tool.code,
      tool_name: activatedTool.tool_name || tool.name,
      description: activatedTool.description || tool.description || '',
      config: activatedTool.config || ''
    }
    configDialogVisible.value = true
  }
}

const handleSaveConfig = async () => {
  if (!configFormRef.value) return
  
  saving.value = true
  try {
    const tool = activatedTools.value.find(t => t.tool_code === configFormData.value.tool_code)
    if (tool) {
      const updateData: TenantAIToolUpdate = {
        id: tool.id,
        tool_name: configFormData.value.tool_name,
        description: configFormData.value.description || undefined,
        config: configFormData.value.config || undefined
      }
      await tenantAIToolService.update(updateData)
      ElMessage.success('配置保存成功')
      configDialogVisible.value = false
      await fetchData()
    }
  } catch (error: any) {
    ElMessage.error(error.message || '保存失败')
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.tool-config {
  padding: 0;
}

.toolbar {
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.tool-stats {
  margin-bottom: 16px;
  display: flex;
  gap: 12px;
}

.tool-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 16px;
}

.tool-card {
  background: #fff;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 16px;
  transition: all 0.3s;
}

.tool-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.tool-card.activated {
  border-color: #67c23a;
  background: linear-gradient(135deg, #f6ffed 0%, #fff 100%);
}

.tool-header {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 12px;
}

.tool-icon {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, #409eff 0%, #66b1ff 100%);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  flex-shrink: 0;
}

.tool-card.activated .tool-icon {
  background: linear-gradient(135deg, #67c23a 0%, #85ce61 100%);
}

.tool-title {
  flex: 1;
}

.tool-title h4 {
  margin: 0 0 8px 0;
  font-size: 16px;
  color: #303133;
}

.tool-body {
  margin-bottom: 12px;
}

.tool-code {
  margin: 0 0 8px 0;
  font-size: 12px;
  color: #909399;
  font-family: monospace;
}

.tool-desc {
  margin: 0;
  font-size: 13px;
  color: #606266;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.tool-footer {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}
</style>
