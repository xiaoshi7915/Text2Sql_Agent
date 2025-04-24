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
            <el-tag size="small" :type="getModelTypeTag(row.type)">{{ row.type }}</el-tag>
            <span class="name-text">{{ row.name }}</span>
          </div>
        </template>
      </el-table-column>
      <el-table-column label="版本" prop="version" width="100" align="center" />
      <el-table-column label="端点" prop="endpoint" min-width="180" />
      <el-table-column label="平均响应时间" width="120" align="center">
        <template #default="{ row }">
          {{ row.avgResponseTime }} ms
        </template>
      </el-table-column>
      <el-table-column label="状态" width="100" align="center">
        <template #default="{ row }">
          <el-tag :type="row.status === 'active' ? 'success' : 'danger'" size="small">
            {{ row.status === 'active' ? '活跃' : '离线' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="上次更新时间" width="180" align="center">
        <template #default="{ row }">
          {{ formatDate(row.updatedAt) }}
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
          <el-button size="small" :type="row.status === 'active' ? 'warning' : 'success'" plain @click="handleToggleStatus(row)">
            <el-icon v-if="row.status === 'active'"><icon-switch /></el-icon>
            <el-icon v-else><icon-open /></el-icon>
            <span>{{ row.status === 'active' ? '停用' : '启用' }}</span>
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
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'

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
    
    // 模型列表（模拟数据）
    const models = ref([
      {
        id: 1,
        name: 'DeepSeek-SQL-7B',
        type: 'LLM',
        version: '1.0.0',
        endpoint: 'https://api.deepseek.com/v1/sql',
        avgResponseTime: 235,
        status: 'active',
        parameters: {
          temperature: 0.7,
          maxTokens: 2048,
          topP: 0.95
        },
        createdAt: '2023-11-01T08:30:00Z',
        updatedAt: '2023-11-06T15:45:00Z'
      },
      {
        id: 2,
        name: 'GitHub Copilot for SQL',
        type: 'LLM',
        version: '2.1.0',
        endpoint: 'https://api.github.com/copilot/sql',
        avgResponseTime: 312,
        status: 'active',
        parameters: {
          temperature: 0.5,
          maxTokens: 1024,
          topP: 0.9
        },
        createdAt: '2023-10-15T10:20:00Z',
        updatedAt: '2023-11-05T14:30:00Z'
      },
      {
        id: 3,
        name: 'Local Database Extractor',
        type: 'Extractor',
        version: '0.2.1',
        endpoint: 'http://localhost:8000/extract',
        avgResponseTime: 450,
        status: 'offline',
        parameters: {
          batchSize: 100,
          timeout: 30000
        },
        createdAt: '2023-11-02T14:10:00Z',
        updatedAt: '2023-11-04T09:15:00Z'
      }
    ])
    
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
          item.endpoint.toLowerCase().includes(keyword)
        )
      }
      
      // 模型类型筛选
      if (filters.value.type) {
        result = result.filter(item => item.type === filters.value.type)
      }
      
      // 状态筛选
      if (filters.value.status) {
        result = result.filter(item => item.status === filters.value.status)
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
    
    // 测试模型连接
    const handleTest = (row) => {
      loading.value = true
      
      // 模拟API调用
      setTimeout(() => {
        loading.value = false
        
        // 显示成功消息
        if (row.status === 'active') {
          ElMessage({
            message: `模型 ${row.name} 连接成功，响应时间: ${row.avgResponseTime}ms`,
            type: 'success'
          })
        } else {
          ElMessage({
            message: `模型 ${row.name} 当前离线，无法连接`,
            type: 'error'
          })
        }
      }, 1000)
    }
    
    // 切换模型状态
    const handleToggleStatus = (row) => {
      const newStatus = row.status === 'active' ? 'offline' : 'active'
      const statusText = newStatus === 'active' ? '启用' : '停用'
      
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
          // 模拟API调用
          loading.value = true
          
          setTimeout(() => {
            // 更新本地数据
            const model = models.value.find(item => item.id === row.id)
            if (model) {
              model.status = newStatus
            }
            
            loading.value = false
            
            ElMessage({
              message: `模型${statusText}成功`,
              type: 'success'
            })
          }, 500)
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
          // 模拟删除操作
          models.value = models.value.filter(item => item.id !== row.id)
          
          ElMessage({
            type: 'success',
            message: '删除成功'
          })
        })
        .catch(() => {
          // 取消删除
        })
    }
    
    // 获取模型列表
    const fetchModels = () => {
      loading.value = true
      
      // 模拟API调用
      setTimeout(() => {
        // 实际项目中应该调用API获取数据
        // models.value = response.data
        
        loading.value = false
      }, 500)
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
      handleDelete
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