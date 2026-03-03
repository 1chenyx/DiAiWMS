<template>
  <div class="product-management">
    <el-card shadow="hover">
      <template #header>
        <div class="card-header">
          <span>商品管理</span>
          <el-button type="primary" @click="handleAddProduct">
            <el-icon><Plus /></el-icon> 添加商品
          </el-button>
        </div>
      </template>
      
      <div class="content-container">
        <div class="tree-container">
          <div class="tree-header">
            <span>商品分类</span>
            <el-button type="primary" size="small" link @click="handleAddCategory">
              <el-icon><Plus /></el-icon> 添加分类
            </el-button>
          </div>
          <el-tree
            ref="treeRef"
            :data="categoryTreeData"
            :props="treeProps"
            node-key="id"
            default-expand-all
            :expand-on-click-node="false"
            :highlight-current="true"
            @node-click="handleCategoryClick"
            v-loading="categoryLoading"
          >
            <template #default="{ node, data }">
              <span class="custom-tree-node">
                <span class="node-label">{{ node.label }}</span>
                <span class="node-actions">
                  <el-button type="primary" size="small" link @click.stop="handleAddChildCategory(data)">
                    <el-icon><Plus /></el-icon>
                  </el-button>
                  <el-button type="primary" size="small" link @click.stop="handleEditCategory(data)">
                    <el-icon><Edit /></el-icon>
                  </el-button>
                  <el-button type="danger" size="small" link @click.stop="handleDeleteCategory(data)">
                    <el-icon><Delete /></el-icon>
                  </el-button>
                </span>
              </span>
            </template>
          </el-tree>
        </div>
        
        <div class="product-container">
          <div class="search-section">
            <el-form :inline="true" :model="searchForm" class="search-form">
              <el-form-item label="商品名称">
                <el-input v-model="searchForm.spu_name" placeholder="请输入商品名称" clearable />
              </el-form-item>
              <el-form-item label="商品编码">
                <el-input v-model="searchForm.spu_code" placeholder="请输入商品编码" clearable />
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
          
          <el-table :data="spuList" style="width: 100%" v-loading="productLoading">
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="spu_name" label="商品名称" />
            <el-table-column prop="spu_code" label="商品编码" />
            <el-table-column prop="category_name" label="商品分类" />
            <el-table-column prop="brand" label="品牌" />
            <el-table-column prop="supplier_name" label="供应商" />
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
                <el-button type="info" size="small" @click="handleViewDetail(scope.row)">
                  <el-icon><View /></el-icon> 详情
                </el-button>
                <el-button type="primary" size="small" @click="handleEditProduct(scope.row)">
                  <el-icon><Edit /></el-icon> 编辑
                </el-button>
                <el-button type="danger" size="small" @click="handleDeleteProduct(scope.row.id)">
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
        </div>
      </div>
    </el-card>
    
    <el-dialog v-model="categoryDialogVisible" :title="categoryDialogTitle" width="500px">
      <el-form ref="categoryFormRef" :model="categoryFormData" :rules="categoryFormRules" label-width="100px">
        <el-form-item label="分类名称" prop="category_name">
          <el-input v-model="categoryFormData.category_name" placeholder="请输入分类名称" />
        </el-form-item>
        <el-form-item label="分类编码" prop="category_code">
          <el-input v-model="categoryFormData.category_code" placeholder="请输入分类编码" />
        </el-form-item>
        <el-form-item label="父分类" prop="parent_id">
          <el-cascader
            v-model="categoryFormData.parent_id"
            :options="categoryTreeData"
            :props="{ checkStrictly: true, value: 'id', label: 'category_name', emitPath: false }"
            placeholder="请选择父分类"
            clearable
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="排序" prop="sort_order">
          <el-input-number v-model="categoryFormData.sort_order" :min="0" :max="999" />
        </el-form-item>
        <el-form-item label="状态" prop="is_valid">
          <el-switch v-model="categoryFormData.is_valid" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="categoryDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleCategorySubmit" :loading="categorySubmitting">确定</el-button>
        </span>
      </template>
    </el-dialog>
    
    <el-dialog v-model="productDialogVisible" :title="productDialogTitle" width="900px">
      <el-form ref="productFormRef" :model="productFormData" :rules="productFormRules" label-width="100px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="商品名称" prop="spu_name">
              <el-input v-model="productFormData.spu_name" placeholder="请输入商品名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="商品编码" prop="spu_code">
              <el-input v-model="productFormData.spu_code" placeholder="请输入商品编码" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="商品分类" prop="category_id">
          <el-cascader
            v-model="productFormData.category_id"
            :options="categoryList"
            :props="{ checkStrictly: true, value: 'id', label: 'category_name', emitPath: false }"
            placeholder="请选择商品分类"
            clearable
            style="width: 100%"
          />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="品牌" prop="brand">
              <el-input v-model="productFormData.brand" placeholder="请输入品牌" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="供应商" prop="supplier_id">
              <el-select
                v-model="productFormData.supplier_id"
                placeholder="请选择供应商"
                clearable
                filterable
                style="width: 100%"
              >
                <el-option
                  v-for="supplier in supplierList"
                  :key="supplier.id"
                  :label="supplier.supplier_name"
                  :value="supplier.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="描述" prop="spu_description">
          <el-input v-model="productFormData.spu_description" placeholder="请输入描述" type="textarea" />
        </el-form-item>
        <el-form-item label="状态" prop="is_valid">
          <el-switch v-model="productFormData.is_valid" />
        </el-form-item>
        
        <el-divider content-position="left">SKU管理</el-divider>
        
        <div class="sku-section">
          <el-button type="primary" size="small" @click="handleAddSku">
            <el-icon><Plus /></el-icon> 添加SKU
          </el-button>
          <el-table :data="productSkuList" style="width: 100%; margin-top: 10px" border>
            <el-table-column prop="sku_code" label="SKU编码" width="150" />
            <el-table-column prop="sku_name" label="SKU名称" width="150" />
            <el-table-column prop="bar_code" label="条码" width="120" />
            <el-table-column prop="weight" label="重量(kg)" width="100" />
            <el-table-column prop="volume" label="体积(m³)" width="100" />
            <el-table-column prop="length" label="长(cm)" width="80" />
            <el-table-column prop="width" label="宽(cm)" width="80" />
            <el-table-column prop="height" label="高(cm)" width="80" />
            <el-table-column label="操作" width="150" fixed="right">
              <template #default="scope">
                <el-button type="primary" size="small" link @click="handleEditSku(scope.row)">
                  <el-icon><Edit /></el-icon> 编辑
                </el-button>
                <el-button type="danger" size="small" link @click="handleDeleteSku(scope.row)">
                  <el-icon><Delete /></el-icon> 删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="productDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleProductSubmit" :loading="productSubmitting">确定</el-button>
        </span>
      </template>
    </el-dialog>
    
    <el-dialog v-model="skuDialogVisible" :title="skuDialogTitle" width="600px">
      <el-form ref="skuFormRef" :model="skuFormData" :rules="skuFormRules" label-width="100px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="SKU编码" prop="sku_code">
              <el-input v-model="skuFormData.sku_code" placeholder="请输入SKU编码" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="SKU名称" prop="sku_name">
              <el-input v-model="skuFormData.sku_name" placeholder="请输入SKU名称" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="条码" prop="bar_code">
          <el-input v-model="skuFormData.bar_code" placeholder="请输入条码" />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="重量(kg)" prop="weight">
              <el-input-number v-model="skuFormData.weight" :min="0" :step="0.1" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="体积(m³)" prop="volume">
              <el-input-number v-model="skuFormData.volume" :min="0" :step="0.001" :precision="3" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="长(cm)" prop="length">
              <el-input-number v-model="skuFormData.length" :min="0" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="宽(cm)" prop="width">
              <el-input-number v-model="skuFormData.width" :min="0" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="高(cm)" prop="height">
              <el-input-number v-model="skuFormData.height" :min="0" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="skuDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSkuSubmit" :loading="skuSubmitting">确定</el-button>
        </span>
      </template>
    </el-dialog>
    
    <el-dialog v-model="detailDialogVisible" title="商品详情" width="900px">
      <el-descriptions :column="2" border v-if="currentProduct">
        <el-descriptions-item label="商品ID">{{ currentProduct.id }}</el-descriptions-item>
        <el-descriptions-item label="商品名称">{{ currentProduct.spu_name }}</el-descriptions-item>
        <el-descriptions-item label="商品编码">{{ currentProduct.spu_code }}</el-descriptions-item>
        <el-descriptions-item label="商品分类">{{ currentProduct.category_name }}</el-descriptions-item>
        <el-descriptions-item label="品牌">{{ currentProduct.brand || '-' }}</el-descriptions-item>
        <el-descriptions-item label="供应商">{{ currentProduct.supplier_name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="描述" :span="2">{{ currentProduct.spu_description || '-' }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="currentProduct.is_valid ? 'success' : 'danger'">
            {{ currentProduct.is_valid ? '启用' : '禁用' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ currentProduct.create_time }}</el-descriptions-item>
      </el-descriptions>
      
      <el-divider content-position="left">SKU列表</el-divider>
      
      <el-table :data="detailSkuList" style="width: 100%" v-loading="detailSkuLoading" border>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="sku_code" label="SKU编码" width="150" />
        <el-table-column prop="sku_name" label="SKU名称" width="150" />
        <el-table-column prop="bar_code" label="条码" width="120" />
        <el-table-column prop="weight" label="重量(kg)" width="100" />
        <el-table-column prop="volume" label="体积(m³)" width="100" />
        <el-table-column prop="length" label="长(cm)" width="80" />
        <el-table-column prop="width" label="宽(cm)" width="80" />
        <el-table-column prop="height" label="高(cm)" width="80" />
        <el-table-column prop="is_valid" label="状态" width="80">
          <template #default="scope">
            <el-tag :type="scope.row.is_valid ? 'success' : 'danger'" size="small">
              {{ scope.row.is_valid ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="create_time" label="创建时间" width="160" />
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { Plus, Edit, Delete, View } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { spuService, type Spu, type SpuCreate } from '@/services/spuService'
import { categoryService, type Category, type CategoryCreate, type CategoryTreeNode } from '@/services/categoryService'
import { skuService, type Sku, type SkuCreate, type SkuUpdate } from '@/services/skuService'
import { supplierService, type Supplier } from '@/services/supplierService'

const treeRef = ref()
const categoryLoading = ref(false)
const productLoading = ref(false)
const categorySubmitting = ref(false)
const productSubmitting = ref(false)
const skuSubmitting = ref(false)
const detailSkuLoading = ref(false)

const categoryList = ref<CategoryTreeNode[]>([])
const supplierList = ref<Supplier[]>([])
const selectedCategoryId = ref<number | undefined>(undefined)

const categoryTreeData = computed(() => {
  return categoryList.value
})

const treeProps = {
  children: 'children',
  label: 'category_name'
}

const searchForm = reactive({
  spu_name: '',
  spu_code: '',
  is_valid: undefined as boolean | undefined
})

const pagination = reactive({
  page_index: 1,
  page_size: 10,
  total: 0
})

const spuList = ref<Spu[]>([])
const productSkuList = ref<Sku[]>([])
const originalSkuList = ref<Sku[]>([])
const detailSkuList = ref<Sku[]>([])
const currentProduct = ref<Spu | null>(null)

const categoryDialogVisible = ref(false)
const categoryDialogTitle = ref('添加商品分类')
const categoryFormRef = ref<FormInstance>()
const categoryEditingId = ref<number | null>(null)

const categoryFormData = reactive<CategoryCreate & { is_valid: boolean }>({
  category_name: '',
  category_code: '',
  parent_id: undefined,
  sort_order: 0,
  is_valid: true
})

const categoryFormRules = reactive<FormRules>({
  category_name: [{ required: true, message: '请输入分类名称', trigger: 'blur' }],
  category_code: [{ required: true, message: '请输入分类编码', trigger: 'blur' }]
})

const productDialogVisible = ref(false)
const productDialogTitle = ref('添加商品')
const productFormRef = ref<FormInstance>()
const productEditingId = ref<number | null>(null)

const productFormData = reactive<SpuCreate & { is_valid: boolean }>({
  spu_name: '',
  spu_code: '',
  category_id: undefined,
  supplier_id: undefined,
  brand: '',
  spu_description: '',
  is_valid: true
})

const productFormRules = reactive<FormRules>({
  spu_name: [{ required: true, message: '请输入商品名称', trigger: 'blur' }],
  spu_code: [{ required: true, message: '请输入商品编码', trigger: 'blur' }],
  category_id: [{ required: true, message: '请选择商品分类', trigger: 'change' }]
})

const skuDialogVisible = ref(false)
const skuDialogTitle = ref('添加SKU')
const skuFormRef = ref<FormInstance>()
const skuEditingId = ref<number | null>(null)

const skuFormData = reactive<SkuCreate>({
  sku_name: '',
  sku_code: '',
  spu_id: 0,
  bar_code: '',
  weight: undefined,
  volume: undefined,
  length: undefined,
  width: undefined,
  height: undefined
})

const skuFormRules = reactive<FormRules>({
  sku_code: [{ required: true, message: '请输入SKU编码', trigger: 'blur' }],
  sku_name: [{ required: true, message: '请输入SKU名称', trigger: 'blur' }]
})

const detailDialogVisible = ref(false)

const fetchCategoryList = async () => {
  categoryLoading.value = true
  try {
    categoryList.value = await categoryService.getTree()
  } catch (error) {
    console.error('获取分类列表失败:', error)
    ElMessage.error('获取分类列表失败')
  } finally {
    categoryLoading.value = false
  }
}

const fetchSupplierList = async () => {
  try {
    supplierList.value = await supplierService.getAll()
  } catch (error) {
    console.error('获取供应商列表失败:', error)
    ElMessage.error('获取供应商列表失败')
  }
}

const fetchProductList = async () => {
  productLoading.value = true
  try {
    const result = await spuService.getPage({
      page_index: pagination.page_index,
      page_size: pagination.page_size,
      spu_name: searchForm.spu_name || undefined,
      spu_code: searchForm.spu_code || undefined,
      category_id: selectedCategoryId.value,
      is_valid: searchForm.is_valid
    })
    spuList.value = result.data
    pagination.total = result.totals
  } catch (error) {
    console.error('获取商品列表失败:', error)
    ElMessage.error('获取商品列表失败')
  } finally {
    productLoading.value = false
  }
}

const fetchProductSkuList = async (spuId: number) => {
  try {
    productSkuList.value = await skuService.getList(spuId)
  } catch (error) {
    console.error('获取SKU列表失败:', error)
    ElMessage.error('获取SKU列表失败')
  }
}

const handleCategoryClick = (data: Category) => {
  selectedCategoryId.value = data.id
  pagination.page_index = 1
  fetchProductList()
}

const handleSearch = () => {
  pagination.page_index = 1
  fetchProductList()
}

const resetSearch = () => {
  searchForm.spu_name = ''
  searchForm.spu_code = ''
  searchForm.is_valid = undefined
  handleSearch()
}

const handleSizeChange = (size: number) => {
  pagination.page_size = size
  fetchProductList()
}

const handleCurrentChange = (current: number) => {
  pagination.page_index = current
  fetchProductList()
}

const handleAddCategory = () => {
  categoryDialogTitle.value = '添加商品分类'
  categoryEditingId.value = null
  categoryFormData.category_name = ''
  categoryFormData.category_code = ''
  categoryFormData.parent_id = undefined
  categoryFormData.sort_order = 0
  categoryFormData.is_valid = true
  categoryDialogVisible.value = true
}

const handleAddChildCategory = (node: Category) => {
  categoryDialogTitle.value = '添加子分类'
  categoryEditingId.value = null
  categoryFormData.category_name = ''
  categoryFormData.category_code = ''
  categoryFormData.parent_id = node.id
  categoryFormData.sort_order = 0
  categoryFormData.is_valid = true
  categoryDialogVisible.value = true
}

const handleEditCategory = (node: Category) => {
  categoryDialogTitle.value = '编辑商品分类'
  categoryEditingId.value = node.id
  categoryFormData.category_name = node.category_name
  categoryFormData.category_code = node.category_code
  categoryFormData.parent_id = node.parent_id || undefined
  categoryFormData.sort_order = node.sort_order || 0
  categoryFormData.is_valid = node.is_valid
  categoryDialogVisible.value = true
}

const handleDeleteCategory = async (node: Category) => {
  try {
    await ElMessageBox.confirm(`确定要删除分类"${node.category_name}"吗？`, '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await categoryService.delete(node.id)
    ElMessage.success('删除成功')
    await fetchCategoryList()
    if (selectedCategoryId.value === node.id) {
      selectedCategoryId.value = undefined
      fetchProductList()
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handleCategorySubmit = async () => {
  if (!categoryFormRef.value) return
  
  try {
    await categoryFormRef.value.validate()
    categorySubmitting.value = true
    
    if (categoryEditingId.value) {
      await categoryService.update({
        id: categoryEditingId.value,
        category_name: categoryFormData.category_name,
        category_code: categoryFormData.category_code,
        parent_id: categoryFormData.parent_id,
        sort_order: categoryFormData.sort_order,
        is_valid: categoryFormData.is_valid
      })
      ElMessage.success('更新成功')
    } else {
      await categoryService.create(categoryFormData)
      ElMessage.success('创建成功')
    }
    
    categoryDialogVisible.value = false
    await fetchCategoryList()
  } catch (error) {
    console.error('提交失败:', error)
  } finally {
    categorySubmitting.value = false
  }
}

const handleAddProduct = () => {
  productDialogTitle.value = '添加商品'
  productEditingId.value = null
  productFormData.spu_name = ''
  productFormData.spu_code = ''
  productFormData.category_id = selectedCategoryId.value
  productFormData.supplier_id = undefined
  productFormData.brand = ''
  productFormData.spu_description = ''
  productFormData.is_valid = true
  productSkuList.value = []
  originalSkuList.value = []
  productDialogVisible.value = true
}

const handleEditProduct = async (row: Spu) => {
  productDialogTitle.value = '编辑商品'
  productEditingId.value = row.id
  productFormData.spu_name = row.spu_name
  productFormData.spu_code = row.spu_code
  productFormData.category_id = row.category_id
  productFormData.supplier_id = row.supplier_id
  productFormData.brand = row.brand || ''
  productFormData.spu_description = row.spu_description || ''
  productFormData.is_valid = row.is_valid
  await fetchProductSkuList(row.id)
  originalSkuList.value = JSON.parse(JSON.stringify(productSkuList.value))
  productDialogVisible.value = true
}

const handleDeleteProduct = async (id: number) => {
  try {
    await ElMessageBox.confirm('确定要删除这个商品吗？', '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await spuService.delete(id)
    ElMessage.success('删除成功')
    fetchProductList()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handleProductSubmit = async () => {
  if (!productFormRef.value) return
  
  try {
    await productFormRef.value.validate()
    productSubmitting.value = true
    
    if (productEditingId.value) {
      const updateData: any = {
        id: productEditingId.value,
        spu_name: productFormData.spu_name,
        spu_code: productFormData.spu_code,
        category_id: productFormData.category_id,
        supplier_id: productFormData.supplier_id,
        brand: productFormData.brand,
        spu_description: productFormData.spu_description,
        is_valid: productFormData.is_valid
      }
      
      if (productSkuList.value.length > 0) {
        updateData.skus = productSkuList.value.map(sku => ({
          id: sku.id > 0 && String(sku.id).length < 10 ? sku.id : undefined,
          sku_name: sku.sku_name,
          sku_code: sku.sku_code,
          bar_code: sku.bar_code,
          weight: sku.weight,
          volume: sku.volume,
          length: sku.length,
          width: sku.width,
          height: sku.height
        })).filter(sku => sku.sku_name && sku.sku_code)
      }
      
      const deletedSkuIds = originalSkuList.value
        .filter(original => !productSkuList.value.some(sku => sku.id === original.id))
        .map(sku => sku.id)
      
      if (deletedSkuIds.length > 0) {
        updateData.delete_sku_ids = deletedSkuIds
      }
      
      await spuService.update(updateData)
    } else {
      const createData: any = {
        spu_name: productFormData.spu_name,
        spu_code: productFormData.spu_code,
        category_id: productFormData.category_id,
        supplier_id: productFormData.supplier_id,
        brand: productFormData.brand,
        spu_description: productFormData.spu_description,
        is_valid: productFormData.is_valid
      }
      
      if (productSkuList.value.length > 0) {
        createData.skus = productSkuList.value.map(sku => ({
          sku_name: sku.sku_name,
          sku_code: sku.sku_code,
          bar_code: sku.bar_code,
          weight: sku.weight,
          volume: sku.volume,
          length: sku.length,
          width: sku.width,
          height: sku.height
        })).filter(sku => sku.sku_name && sku.sku_code)
      }
      
      await spuService.create(createData)
    }
    
    productDialogVisible.value = false
    fetchProductList()
    ElMessage.success('保存成功')
  } catch (error) {
    console.error('提交失败:', error)
    ElMessage.error('保存失败')
  } finally {
    productSubmitting.value = false
  }
}

const handleAddSku = () => {
  skuDialogTitle.value = '添加SKU'
  skuEditingId.value = null
  skuFormData.sku_name = ''
  skuFormData.sku_code = ''
  skuFormData.spu_id = 0
  skuFormData.bar_code = ''
  skuFormData.weight = undefined
  skuFormData.volume = undefined
  skuFormData.length = undefined
  skuFormData.width = undefined
  skuFormData.height = undefined
  skuDialogVisible.value = true
}

const handleEditSku = (row: Sku) => {
  skuDialogTitle.value = '编辑SKU'
  skuEditingId.value = row.id
  skuFormData.sku_name = row.sku_name
  skuFormData.sku_code = row.sku_code
  skuFormData.spu_id = 0
  skuFormData.bar_code = row.bar_code || ''
  skuFormData.weight = row.weight
  skuFormData.volume = row.volume
  skuFormData.length = row.length
  skuFormData.width = row.width
  skuFormData.height = row.height
  skuDialogVisible.value = true
}

const handleDeleteSku = async (row: Sku) => {
  try {
    await ElMessageBox.confirm('确定要删除这个SKU吗？', '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    const index = productSkuList.value.findIndex(item => item.id === row.id)
    if (index !== -1) {
      productSkuList.value.splice(index, 1)
      ElMessage.success('删除成功')
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handleSkuSubmit = () => {
  if (!skuFormRef.value) return
  
  skuFormRef.value.validate((valid) => {
    if (!valid) return
    
    if (skuEditingId.value) {
      const index = productSkuList.value.findIndex(item => item.id === skuEditingId.value)
      if (index !== -1) {
        productSkuList.value[index] = {
          ...productSkuList.value[index],
          sku_name: skuFormData.sku_name,
          sku_code: skuFormData.sku_code,
          bar_code: skuFormData.bar_code,
          weight: skuFormData.weight,
          volume: skuFormData.volume,
          length: skuFormData.length,
          width: skuFormData.width,
          height: skuFormData.height,
          is_valid: skuFormData.is_valid
        }
        ElMessage.success('更新成功')
      }
    } else {
      const newSku: Sku = {
        id: Date.now(),
        sku_name: skuFormData.sku_name,
        sku_code: skuFormData.sku_code,
        spu_id: 0,
        bar_code: skuFormData.bar_code,
        weight: skuFormData.weight,
        volume: skuFormData.volume,
        length: skuFormData.length,
        width: skuFormData.width,
        height: skuFormData.height,
        is_valid: skuFormData.is_valid,
        create_time: new Date().toISOString(),
        update_time: new Date().toISOString()
      }
      productSkuList.value.push(newSku)
      ElMessage.success('添加成功')
    }
    
    skuDialogVisible.value = false
  })
}

const handleViewDetail = async (row: Spu) => {
  currentProduct.value = row
  detailDialogVisible.value = true
  detailSkuLoading.value = true
  try {
    detailSkuList.value = await skuService.getList(row.id)
  } catch (error) {
    console.error('获取SKU列表失败:', error)
    ElMessage.error('获取SKU列表失败')
  } finally {
    detailSkuLoading.value = false
  }
}

onMounted(() => {
  fetchCategoryList()
  fetchSupplierList()
  fetchProductList()
})
</script>

<style scoped>
.product-management {
  padding: 20px 0;
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
  flex: 0 0 300px;
  border-right: 1px solid #e4e7ed;
  padding-right: 20px;
  overflow-y: auto;
}

.tree-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  font-weight: bold;
}

.product-container {
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
}

.node-actions {
  display: none;
}

.custom-tree-node:hover .node-actions {
  display: flex;
  gap: 4px;
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

.sku-section {
  margin-top: 20px;
}
</style>
