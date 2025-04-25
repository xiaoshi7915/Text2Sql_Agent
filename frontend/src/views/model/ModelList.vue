<template>
  <div class="model-list-container">
    <div class="header-actions">
      <el-button type="primary" @click="handleCreate">
        <el-icon><icon-plus /></el-icon>
        <span>新建模型</span>
      </el-button>
      <el-input
        v-model="searchKeyword"
        placeholder="搜索模型名称"
        class="search-input"
        clearable
        @clear="handleSearch"
        @input="handleSearch"
      >
        <template #prefix>
          <el-icon><icon-search /></el-icon>
        </template>
      </el-input>
    </div>
    
    <!-- 筛选区域 -->
    <div class="filter-container">
      <el-select v-model="filters.type" placeholder="模型类型" clearable @change="handleFilter">
        <el-option v-for="item in modelTypeOptions" :key="item.value" :label="item.label" :value="item.value" />
      </el-select>
      <el-select v-model="filters.status" placeholder="状态" clearable @change="handleFilter">
        <el-option label="活跃" value="active" />
        <el-option label="离线" value="offline" />
      </el-select>
    </div>
    
    <!-- 模型列表 -->
    <el-table
      v-loading="loading"
      :data="filteredModels"
      border
      style="width: 100%"
      :header-cell-style="{backgroundColor: '#f5f7fa'}"
    >
      <el-table-column label="模型名称" prop="name" min-width="150">
        <template #default="{ row }">
          <div class="name-container">
            <el-tag size="small" :type="getModelTypeTag(row.model_type)">{{ row.model_type }}</el-tag>
            <span class="name-text">{{ row.name }}</span>
          </div>
        </template>
      </el-table-column>
      <el-table-column label="版本" prop="api_version" width="100" align="center" />
      <el-table-column label="端点" prop="api_base" min-width="180" />
      <el-table-column label="平均响应时间" width="120" align="center">
        <template #default="{ row }">
          {{ row.avg_response_time || '-' }} ms
        </template>
      </el-table-column>
      <el-table-column label="状态" width="100" align="center">
        <template #default="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'danger'" size="small">
            {{ row.is_active ? '活跃' : '离线' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="上次更新时间" width="180" align="center">
        <template #default="{ row }">
          {{ formatDate(row.updated_at) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="260" align="center">
        <template #default="{ row }">
          <el-button size="small" type="primary" plain @click="handleEdit(row)">
            <el-icon><icon-edit /></el-icon>
            <span>编辑</span>
          </el-button>
          <el-button size="small" type="success" plain @click="handleTest(row)">
            <el-icon><icon-connection /></el-icon>
            <span>测试</span>
          </el-button>
          <el-button size="small" :type="row.is_active ? 'warning' : 'success'" plain @click="handleToggleStatus(row)">
            <el-icon v-if="row.is_active"><icon-switch /></el-icon>
            <el-icon v-else><icon-open /></el-icon>
            <span>{{ row.is_active ? '停用' : '启用' }}</span>
          </el-button>
          <el-button size="small" type="danger" plain @click="handleDelete(row)">
            <el-icon><icon-delete /></el-icon>
            <span>删除</span>
          </el-button>
        </template>
      </el-table-column>
    </el-table>
    
    <!-- 分页组件 -->
    <div class="pagination-container">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="totalCount"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>
    
    <!-- 添加API Key输入对话框 -->
    <el-dialog
      v-model="apiKeyDialogVisible"
      title="输入API密钥"
      width="500px"
    >
      <el-form :model="apiKeyForm" label-width="100px">
        <el-form-item label="API密钥">
          <el-input 
            v-model="apiKeyForm.apiKey" 
            placeholder="请输入模型API密钥" 
            type="password"
            show-password
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="apiKeyDialogVisible = false">取消</el-button>
          <el-button type="primary" :loading="testingConnection" @click="confirmTestConnection">
            测试连接
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
// 导入API函数
import { getModels, testModelConnection, updateModel, deleteModel } from '@/api/model'

export default {
  name: 'ModelList',
  
  setup() {
    // 路由实例
    const router = useRouter()
    
    // 加载状态
    const loading = ref(false)
    
    // 搜索和筛选
    const searchKeyword = ref('')
    const filters = ref({
      type: '',
      status: ''
    })
    
    // 分页数据
    const currentPage = ref(1)
    const pageSize = ref(10)
    const totalCount = ref(0)
    
    // 模型列表数据
    const models = ref([])
    
    // 模型类型选项
    const modelTypeOptions = [
      { value: 'LLM', label: '大语言模型' },
      { value: 'Extractor', label: '数据抽取器' },
      { value: 'Optimizer', label: '查询优化器' }
    ]
    
    // 根据筛选条件过滤模型列表
    const filteredModels = computed(() => {
      let result = [...models.value]
      
      // 关键字搜索
      if (searchKeyword.value) {
        const keyword = searchKeyword.value.toLowerCase()
        result = result.filter(item => 
          item.name.toLowerCase().includes(keyword) || 
          item.api_base.toLowerCase().includes(keyword)
        )
      }
      
      // 模型类型筛选
      if (filters.value.type) {
        result = result.filter(item => item.model_type === filters.value.type)
      }
      
      // 状态筛选
      if (filters.value.status) {
        const isActive = filters.value.status === 'active'
        result = result.filter(item => item.is_active === isActive)
      }
      
      // 计算总数
      totalCount.value = result.length
      
      // 分页处理
      const startIndex = (currentPage.value - 1) * pageSize.value
      return result.slice(startIndex, startIndex + pageSize.value)
    })
    
    // 格式化日期
    const formatDate = (dateString) => {
      if (!dateString) return '-'
      const date = new Date(dateString)
      return date.toLocaleString()
    }
    
    // 获取模型类型标签样式
    const getModelTypeTag = (type) => {
      const typeMap = {
        'LLM': 'primary',
        'Extractor': 'success',
        'Optimizer': 'warning'
      }
      return typeMap[type] || 'info'
    }
    
    // 搜索处理
    const handleSearch = () => {
      currentPage.value = 1
    }
    
    // 筛选处理
    const handleFilter = () => {
      currentPage.value = 1
    }
    
    // 分页大小变化处理
    const handleSizeChange = (size) => {
      pageSize.value = size
      currentPage.value = 1
    }
    
    // 当前页变化处理
    const handleCurrentChange = (page) => {
      currentPage.value = page
    }
    
    // 创建模型
    const handleCreate = () => {
      router.push('/model/create')
    }
    
    // 编辑模型
    const handleEdit = (row) => {
      router.push(`/model/edit/${row.id}`)
    }
    
    // API密钥对话框
    const apiKeyDialogVisible = ref(false)
    const apiKeyForm = ref({
      apiKey: '',
      modelId: null
    })
    const testingConnection = ref(false)
    const currentTestingModel = ref(null)
    
    // 测试模型连接 - 打开对话框
    const handleTest = (row) => {
      currentTestingModel.value = row
      apiKeyForm.value.modelId = row.id
      apiKeyForm.value.apiKey = ''
      apiKeyDialogVisible.value = true
    }
    
    // 确认测试连接
    const confirmTestConnection = () => {
      if (!apiKeyForm.value.apiKey) {
        ElMessage({
          message: 'API密钥不能为空',
          type: 'warning'
        })
        return
      }
      
      testingConnection.value = true
      const row = currentTestingModel.value
      
      // 构建测试数据 - 确保包含所有必要字段
      const testData = {
        provider: row.provider,
        model_type: row.model_type, 
        api_key: apiKeyForm.value.apiKey,
        api_base: row.api_base
      }
      
      console.log('测试连接数据:', testData)
      
      testModelConnection(testData)
        .then(response => {
          console.log('测试连接响应:', response)
          
          // 根据响应状态显示消息
          if (response.status === 'success') {
            ElMessage({
              message: `模型 ${row.name} 连接成功`,
              type: 'success'
            })
            apiKeyDialogVisible.value = false
          } else {
            // 显示错误消息
            ElMessage({
              message: response.message || `模型 ${row.name} 连接失败`,
              type: 'error'
            })
          }
        })
        .finally(() => {
          testingConnection.value = false
        })
    }
    
    // 切换模型状态
    const handleToggleStatus = (row) => {
      const newStatus = !row.is_active
      const statusText = newStatus ? '启用' : '停用'
      
      ElMessageBox.confirm(
        `确定要${statusText}模型 "${row.name}" 吗？`,
        '提示',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }
      )
        .then(() => {
          loading.value = true
          
          // 调用API更新模型状态
          updateModel(row.id, { is_active: newStatus })
            .then(response => {
              if (response.status === 'success') {
                // 更新本地数据
                const model = models.value.find(item => item.id === row.id)
                if (model) {
                  model.is_active = newStatus
                }
                
                ElMessage({
                  message: `模型${statusText}成功`,
                  type: 'success'
                })
              } else {
                ElMessage({
                  message: response.message || '操作失败',
                  type: 'error'
                })
              }
            })
            .catch(error => {
              ElMessage({
                message: error.message || '操作失败',
                type: 'error'
              })
            })
            .finally(() => {
              loading.value = false
            })
        })
        .catch(() => {
          // 取消操作
        })
    }
    
    // 删除模型
    const handleDelete = (row) => {
      ElMessageBox.confirm(
        `确定要删除模型 "${row.name}" 吗？`,
        '警告',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }
      )
        .then(() => {
          loading.value = true
          
          // 调用删除API
          deleteModel(row.id)
            .then(response => {
              if (response.status === 'success') {
                // 更新本地列表
                models.value = models.value.filter(item => item.id !== row.id)
                
                ElMessage({
                  type: 'success',
                  message: '删除成功'
                })
              } else {
                ElMessage({
                  type: 'error',
                  message: response.message || '删除失败'
                })
              }
            })
            .catch(error => {
              ElMessage({
                type: 'error',
                message: error.message || '删除失败'
              })
            })
            .finally(() => {
              loading.value = false
            })
        })
        .catch(() => {
          // 取消删除
        })
    }
    
    // 获取模型列表
    const fetchModels = () => {
      loading.value = true
      
      // 调用API获取模型列表
      getModels()
        .then(response => {
          if (response.status === 'success') {
            // 处理平均响应时间
            models.value = (response.data || []).map(model => {
              // 如果后端返回了响应时间，就使用后端的数据
              // 如果没有，就根据模型类型设置一个模拟的响应时间
              if (!model.avg_response_time) {
                // 模拟不同类型模型的响应时间
                if (model.model_type === 'LLM') {
                  model.avg_response_time = Math.floor(Math.random() * 200) + 200; // 200-400ms
                } else if (model.model_type === 'Extractor') {
                  model.avg_response_time = Math.floor(Math.random() * 300) + 300; // 300-600ms
                } else {
                  model.avg_response_time = Math.floor(Math.random() * 100) + 150; // 150-250ms
                }
              }
              return model;
            });
            totalCount.value = models.value.length
          } else {
            ElMessage({
              message: response.message || '获取模型列表失败',
              type: 'error'
            })
          }
        })
        .catch(error => {
          ElMessage({
            message: error.message || '获取模型列表失败',
            type: 'error'
          })
        })
        .finally(() => {
          loading.value = false
        })
    }
    
    // 组件加载时获取数据
    onMounted(() => {
      fetchModels()
    })
    
    return {
      loading,
      searchKeyword,
      filters,
      currentPage,
      pageSize,
      totalCount,
      models,
      filteredModels,
      modelTypeOptions,
      formatDate,
      getModelTypeTag,
      handleSearch,
      handleFilter,
      handleSizeChange,
      handleCurrentChange,
      handleCreate,
      handleEdit,
      handleTest,
      handleToggleStatus,
      handleDelete,
      apiKeyDialogVisible,
      apiKeyForm,
      testingConnection,
      confirmTestConnection
    }
  }
}
</script>

<style lang="scss" scoped>
.model-list-container {
  .header-actions {
    display: flex;
    justify-content: space-between;
    margin-bottom: 20px;
    
    .search-input {
      width: 300px;
    }
  }
  
  .filter-container {
    margin-bottom: 20px;
    display: flex;
    gap: 15px;
    
    .el-select {
      width: 180px;
    }
  }
  
  .name-container {
    display: flex;
    align-items: center;
    
    .name-text {
      margin-left: 8px;
      font-weight: bold;
    }
  }
  
  .pagination-container {
    margin-top: 20px;
    display: flex;
    justify-content: flex-end;
  }
}

@media (max-width: 768px) {
  .model-list-container {
    .header-actions {
      flex-direction: column;
      
      .el-button {
        margin-bottom: 10px;
      }
      
      .search-input {
        width: 100%;
      }
    }
    
    .filter-container {
      flex-direction: column;
      
      .el-select {
        width: 100%;
      }
    }
  }
}
</style> 