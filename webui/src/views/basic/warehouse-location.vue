<template>
  <div class="warehouse-location-management">
    <el-card shadow="hover">
      <template #header>
        <div class="card-header">
          <span>仓库管理</span>
          <el-button type="primary" @click="handleAddRoot">
            <el-icon><Plus /></el-icon> 添加仓库
          </el-button>
        </div>
      </template>
      
      <div class="content-container">
        <div class="tree-container">
          <el-tree
            ref="treeRef"
            :data="treeData"
            :props="treeProps"
            node-key="id"
            default-expand-all
            :expand-on-click-node="false"
            :highlight-current="true"
            @node-click="handleNodeClick"
            v-loading="treeLoading"
          >
            <template #default="{ node, data }">
              <span class="custom-tree-node">
                <el-icon v-if="data.node_type === 1"><OfficeBuilding /></el-icon>
                <el-icon v-else-if="data.node_type === 2"><Grid /></el-icon>
                <el-icon v-else><Location /></el-icon>
                <span class="node-label">{{ node.label }}</span>
                <span class="node-type-tag">
                  <el-tag :type="getNodeTypeTagType(data.node_type)" size="small">
                    {{ getNodeTypeName(data.node_type) }}
                  </el-tag>
                </span>
                <span class="node-actions">
                  <el-button type="primary" size="small" link @click.stop="handleAddChild(data)">
                    <el-icon><Plus /></el-icon>
                  </el-button>
                  <el-button type="primary" size="small" link @click.stop="handleEdit(data)">
                    <el-icon><Edit /></el-icon>
                  </el-button>
                  <el-button type="danger" size="small" link @click.stop="handleDelete(data)">
                    <el-icon><Delete /></el-icon>
                  </el-button>
                </span>
              </span>
            </template>
          </el-tree>
        </div>
        
        <div class="detail-container">
          <el-card v-if="selectedNode" shadow="hover">
            <template #header>
              <div class="detail-header">
                <span>{{ getNodeTypeName(selectedNode.node_type) }}详情</span>
                <el-tag :type="selectedNode.is_valid ? 'success' : 'danger'">
                  {{ selectedNode.is_valid ? '启用' : '禁用' }}
                </el-tag>
              </div>
            </template>
            
            <el-descriptions :column="2" border>
              <el-descriptions-item label="节点ID">{{ selectedNode.id }}</el-descriptions-item>
              <el-descriptions-item label="节点类型">{{ getNodeTypeName(selectedNode.node_type) }}</el-descriptions-item>
              <el-descriptions-item label="节点名称" :span="2">{{ selectedNode.node_name }}</el-descriptions-item>
              <el-descriptions-item label="父节点ID">{{ selectedNode.parent_id || '无' }}</el-descriptions-item>
              <el-descriptions-item label="创建人">{{ selectedNode.creator }}</el-descriptions-item>
              
              <template v-if="selectedNode.node_type === 1">
                <el-descriptions-item label="城市">{{ selectedNode.city }}</el-descriptions-item>
                <el-descriptions-item label="管理员">{{ selectedNode.manager }}</el-descriptions-item>
                <el-descriptions-item label="地址" :span="2">{{ selectedNode.address }}</el-descriptions-item>
                <el-descriptions-item label="联系电话">{{ selectedNode.contact_tel }}</el-descriptions-item>
                <el-descriptions-item label="邮箱">{{ selectedNode.email }}</el-descriptions-item>
              </template>
              
              <template v-if="selectedNode.node_type === 2">
                <el-descriptions-item label="区域属性">{{ getAreaPropertyText(selectedNode.area_property) }}</el-descriptions-item>
              </template>
              
              <template v-if="selectedNode.node_type === 3">
                <el-descriptions-item label="长度(m)">{{ selectedNode.location_length }}</el-descriptions-item>
                <el-descriptions-item label="宽度(m)">{{ selectedNode.location_width }}</el-descriptions-item>
                <el-descriptions-item label="高度(m)">{{ selectedNode.location_height }}</el-descriptions-item>
                <el-descriptions-item label="体积(m³)">{{ selectedNode.location_volume }}</el-descriptions-item>
                <el-descriptions-item label="载重(kg)">{{ selectedNode.location_load }}</el-descriptions-item>
                <el-descriptions-item label="巷道号">{{ selectedNode.roadway_number }}</el-descriptions-item>
                <el-descriptions-item label="货架号">{{ selectedNode.shelf_number }}</el-descriptions-item>
                <el-descriptions-item label="层号">{{ selectedNode.layer_number }}</el-descriptions-item>
                <el-descriptions-item label="标签号" :span="2">{{ selectedNode.tag_number }}</el-descriptions-item>
              </template>
              
              <el-descriptions-item label="创建时间">{{ formatTime(selectedNode.create_time) }}</el-descriptions-item>
              <el-descriptions-item label="更新时间">{{ formatTime(selectedNode.last_update_time) }}</el-descriptions-item>
            </el-descriptions>
          </el-card>
          
          <el-empty v-else description="请选择节点查看详情" />
        </div>
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
        <el-form-item label="节点类型" prop="node_type">
          <el-select v-model="formData.node_type" placeholder="请选择节点类型" disabled>
            <el-option label="仓库" :value="1" />
            <el-option label="库区" :value="2" />
            <el-option label="库位" :value="3" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="节点名称" prop="node_name">
          <el-input v-model="formData.node_name" placeholder="请输入节点名称" />
        </el-form-item>
        
        <el-form-item v-if="formData.node_type === 1" label="城市" prop="city">
          <el-input v-model="formData.city" placeholder="请输入城市" />
        </el-form-item>
        
        <el-form-item v-if="formData.node_type === 1" label="地址" prop="address">
          <el-input v-model="formData.address" placeholder="请输入地址" type="textarea" />
        </el-form-item>
        
        <el-form-item v-if="formData.node_type === 1" label="管理员" prop="manager">
          <el-input v-model="formData.manager" placeholder="请输入管理员" />
        </el-form-item>
        
        <el-form-item v-if="formData.node_type === 1" label="联系电话" prop="contact_tel">
          <el-input v-model="formData.contact_tel" placeholder="请输入联系电话" />
        </el-form-item>
        
        <el-form-item v-if="formData.node_type === 1" label="邮箱" prop="email">
          <el-input v-model="formData.email" placeholder="请输入邮箱" />
        </el-form-item>
        
        <el-form-item v-if="formData.node_type === 2" label="区域属性" prop="area_property">
          <el-select v-model="formData.area_property" placeholder="请选择区域属性">
            <el-option label="收货区" :value="1" />
            <el-option label="存储区" :value="2" />
            <el-option label="拣货区" :value="3" />
            <el-option label="发货区" :value="4" />
            <el-option label="退货区" :value="5" />
          </el-select>
        </el-form-item>
        
        <el-form-item v-if="formData.node_type === 3" label="长度(m)" prop="location_length">
          <el-input-number v-model="formData.location_length" :min="0" :precision="2" style="width: 100%" />
        </el-form-item>
        
        <el-form-item v-if="formData.node_type === 3" label="宽度(m)" prop="location_width">
          <el-input-number v-model="formData.location_width" :min="0" :precision="2" style="width: 100%" />
        </el-form-item>
        
        <el-form-item v-if="formData.node_type === 3" label="高度(m)" prop="location_height">
          <el-input-number v-model="formData.location_height" :min="0" :precision="2" style="width: 100%" />
        </el-form-item>
        
        <el-form-item v-if="formData.node_type === 3" label="体积(m³)" prop="location_volume">
          <el-input-number v-model="formData.location_volume" :min="0" :precision="2" style="width: 100%" />
        </el-form-item>
        
        <el-form-item v-if="formData.node_type === 3" label="载重(kg)" prop="location_load">
          <el-input-number v-model="formData.location_load" :min="0" :precision="2" style="width: 100%" />
        </el-form-item>
        
        <el-form-item v-if="formData.node_type === 3" label="巷道号" prop="roadway_number">
          <el-input v-model="formData.roadway_number" placeholder="请输入巷道号" />
        </el-form-item>
        
        <el-form-item v-if="formData.node_type === 3" label="货架号" prop="shelf_number">
          <el-input v-model="formData.shelf_number" placeholder="请输入货架号" />
        </el-form-item>
        
        <el-form-item v-if="formData.node_type === 3" label="层号" prop="layer_number">
          <el-input v-model="formData.layer_number" placeholder="请输入层号" />
        </el-form-item>
        
        <el-form-item v-if="formData.node_type === 3" label="标签号" prop="tag_number">
          <el-input v-model="formData.tag_number" placeholder="请输入标签号" />
        </el-form-item>
        
        <el-form-item label="状态" prop="is_valid">
          <el-switch v-model="formData.is_valid" active-text="启用" inactive-text="禁用" />
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
import { Plus, Edit, Delete, OfficeBuilding, Grid, Location } from '@element-plus/icons-vue'
import { ElMessageBox, ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { warehouseLocationService, type WarehouseLocation, type WarehouseLocationCreate, type WarehouseLocationUpdate, type WarehouseLocationTreeNode } from '@/services/warehouseLocationService'

const treeRef = ref()
const treeLoading = ref(false)
const treeData = ref<WarehouseLocationTreeNode[]>([])
const selectedNode = ref<WarehouseLocation | null>(null)
const dialogVisible = ref(false)
const dialogTitle = ref('添加节点')
const formRef = ref<FormInstance>()
const isEdit = ref(false)
const submitting = ref(false)

const treeProps = {
  children: 'children',
  label: 'node_name'
}

const formData = reactive<WarehouseLocationCreate>({
  node_type: 1,
  parent_id: 0,
  node_name: '',
  city: '',
  address: '',
  email: '',
  manager: '',
  contact_tel: '',
  area_property: 0,
  location_length: 0,
  location_width: 0,
  location_height: 0,
  location_volume: 0,
  location_load: 0,
  roadway_number: '',
  shelf_number: '',
  layer_number: '',
  tag_number: '',
  is_valid: true
})

const formRules = reactive<FormRules>({
  node_type: [
    { required: true, message: '请选择节点类型', trigger: 'change' }
  ],
  node_name: [
    { required: true, message: '请输入节点名称', trigger: 'blur' }
  ]
})

const getNodeTypeName = (nodeType: number): string => {
  const typeMap: Record<number, string> = {
    1: '仓库',
    2: '库区',
    3: '库位'
  }
  return typeMap[nodeType] || '未知'
}

const getNodeTypeTagType = (nodeType: number): string => {
  const typeMap: Record<number, string> = {
    1: 'primary',
    2: 'success',
    3: 'warning'
  }
  return typeMap[nodeType] || 'info'
}

const getAreaPropertyText = (property: number): string => {
  const propertyMap: Record<number, string> = {
    0: '未设置',
    1: '收货区',
    2: '存储区',
    3: '拣货区',
    4: '发货区',
    5: '退货区'
  }
  return propertyMap[property] || '未知'
}

const formatTime = (timestamp: number): string => {
  if (!timestamp) return ''
  const date = new Date(timestamp * 1000)
  return date.toLocaleString('zh-CN')
}

const fetchTreeData = async () => {
  treeLoading.value = true
  try {
    const result = await warehouseLocationService.getTree()
    treeData.value = result
  } catch (error: any) {
    ElMessage.error(error.message || '获取树形数据失败')
  } finally {
    treeLoading.value = false
  }
}

const handleNodeClick = async (data: WarehouseLocationTreeNode) => {
  try {
    const result = await warehouseLocationService.getById(data.id)
    selectedNode.value = result
  } catch (error: any) {
    ElMessage.error(error.message || '获取节点详情失败')
  }
}

const handleAddRoot = () => {
  isEdit.value = false
  dialogTitle.value = '添加仓库'
  resetForm()
  formData.node_type = 1
  formData.parent_id = 0
  dialogVisible.value = true
}

const handleAddChild = (node: WarehouseLocationTreeNode) => {
  isEdit.value = false
  const nextNodeType = node.node_type + 1
  if (nextNodeType > 3) {
    ElMessage.warning('库位下不能添加子节点')
    return
  }
  dialogTitle.value = `添加${getNodeTypeName(nextNodeType)}`
  resetForm()
  formData.node_type = nextNodeType
  formData.parent_id = node.id
  dialogVisible.value = true
}

const handleEdit = async (node: WarehouseLocationTreeNode) => {
  isEdit.value = true
  dialogTitle.value = `编辑${getNodeTypeName(node.node_type)}`
  try {
    const result = await warehouseLocationService.getById(node.id)
    Object.assign(formData, {
      node_type: result.node_type,
      parent_id: result.parent_id,
      node_name: result.node_name,
      city: result.city,
      address: result.address,
      email: result.email,
      manager: result.manager,
      contact_tel: result.contact_tel,
      area_property: result.area_property,
      location_length: result.location_length,
      location_width: result.location_width,
      location_height: result.location_height,
      location_volume: result.location_volume,
      location_load: result.location_load,
      roadway_number: result.roadway_number,
      shelf_number: result.shelf_number,
      layer_number: result.layer_number,
      tag_number: result.tag_number,
      is_valid: result.is_valid
    })
    dialogVisible.value = true
  } catch (error: any) {
    ElMessage.error(error.message || '获取节点信息失败')
  }
}

const handleDelete = async (node: WarehouseLocationTreeNode) => {
  try {
    await ElMessageBox.confirm(`确定要删除${getNodeTypeName(node.node_type)}"${node.node_name}"吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await warehouseLocationService.delete(node.id)
    ElMessage.success('删除成功')
    await fetchTreeData()
    if (selectedNode.value && selectedNode.value.id === node.id) {
      selectedNode.value = null
    }
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
      if (isEdit.value && selectedNode.value) {
        const updateData: WarehouseLocationUpdate = {
          id: selectedNode.value.id,
          node_name: formData.node_name,
          city: formData.city,
          address: formData.address,
          email: formData.email,
          manager: formData.manager,
          contact_tel: formData.contact_tel,
          area_property: formData.area_property,
          location_length: formData.location_length,
          location_width: formData.location_width,
          location_height: formData.location_height,
          location_volume: formData.location_volume,
          location_load: formData.location_load,
          roadway_number: formData.roadway_number,
          shelf_number: formData.shelf_number,
          layer_number: formData.layer_number,
          tag_number: formData.tag_number,
          is_valid: formData.is_valid
        }
        await warehouseLocationService.update(updateData)
        ElMessage.success('更新成功')
      } else {
        await warehouseLocationService.create(formData)
        ElMessage.success('创建成功')
      }
      dialogVisible.value = false
      await fetchTreeData()
    } catch (error: any) {
      ElMessage.error(error.message || '操作失败')
    } finally {
      submitting.value = false
    }
  })
}

const resetForm = () => {
  Object.assign(formData, {
    node_type: 1,
    parent_id: 0,
    node_name: '',
    city: '',
    address: '',
    email: '',
    manager: '',
    contact_tel: '',
    area_property: 0,
    location_length: 0,
    location_width: 0,
    location_height: 0,
    location_volume: 0,
    location_load: 0,
    roadway_number: '',
    shelf_number: '',
    layer_number: '',
    tag_number: '',
    is_valid: true
  })
  formRef.value?.clearValidate()
}

onMounted(() => {
  fetchTreeData()
})
</script>

<style scoped>
.warehouse-location-management {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.content-container {
  display: flex;
  gap: 20px;
  min-height: 600px;
}

.tree-container {
  flex: 0 0 350px;
  border-right: 1px solid #e4e7ed;
  padding-right: 20px;
  overflow-y: auto;
}

.detail-container {
  flex: 1;
  overflow-y: auto;
}

.custom-tree-node {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-right: 8px;
  font-size: 14px;
}

.node-label {
  flex: 1;
  margin-left: 8px;
}

.node-type-tag {
  margin-left: 8px;
}

.node-actions {
  display: none;
  margin-left: 8px;
}

.custom-tree-node:hover .node-actions {
  display: flex;
  gap: 4px;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>
