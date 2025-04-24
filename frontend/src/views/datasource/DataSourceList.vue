<template>
  <div class="datasource-list-container">
    <div class="header-actions">
      <el-button type="primary" @click="handleCreate">
        <el-icon><icon-plus /></el-icon>
        <span>新建数据源</span>
      </el-button>
      <el-input
        v-model="searchKeyword"
        placeholder="搜索数据源名称"
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
      <el-select v-model="filters.type" placeholder="数据库类型" clearable @change="handleFilter">
        <el-option v-for="item in dbTypeOptions" :key="item.value" :label="item.label" :value="item.value" />
      </el-select>
      <el-select v-model="filters.status" placeholder="连接状态" clearable @change="handleFilter">
        <el-option label="已连接" value="connected" />
        <el-option label="未连接" value="disconnected" />
      </el-select>
    </div>
    
    <!-- 数据源列表 -->
    <el-table
      v-loading="loading"
      :data="filteredDataSources"
      border
      style="width: 100%"
      :header-cell-style="{backgroundColor: '#f5f7fa'}"
    >
      <el-table-column label="数据源名称" prop="name" min-width="150">
        <template #default="{ row }">
          <div class="name-container">
            <el-tag size="small" :type="getDbTypeTag(row.type)">{{ row.type }}</el-tag>
            <span class="name-text">{{ row.name }}</span>
          </div>
        </template>
      </el-table-column>
      <el-table-column label="主机地址" prop="host" min-width="150" />
      <el-table-column label="数据库名" prop="database" min-width="120" />
      <el-table-column label="表数量" prop="tableCount" width="100" align="center" />
      <el-table-column label="连接状态" width="120" align="center">
        <template #default="{ row }">
          <el-tag :type="row.status === 'connected' ? 'success' : 'danger'" size="small">
            {{ row.status === 'connected' ? '已连接' : '未连接' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="最后更新时间" width="180" align="center">
        <template #default="{ row }">
          {{ formatDate(row.updatedAt) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="240" align="center">
        <template #default="{ row }">
          <el-button size="small" type="primary" plain @click="handleEdit(row)">
            <el-icon><icon-edit /></el-icon>
            <span>编辑</span>
          </el-button>
          <el-button size="small" type="success" plain @click="handleTest(row)">
            <el-icon><icon-connection /></el-icon>
            <span>测试</span>
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
  name: 'DataSourceList',
  
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
    
    // 数据源列表（模拟数据）
    const dataSources = ref([
      {
        id: 1,
        name: '生产环境MySQL数据库',
        type: 'MySQL',
        host: '192.168.1.100',
        port: 3306,
        database: 'production_db',
        username: 'root',
        password: '******',
        tableCount: 32,
        status: 'connected',
        createdAt: '2023-11-05T08:30:00Z',
        updatedAt: '2023-11-06T15:45:00Z'
      },
      {
        id: 2,
        name: '测试环境PostgreSQL',
        type: 'PostgreSQL',
        host: '192.168.1.101',
        port: 5432,
        database: 'test_db',
        username: 'postgres',
        password: '******',
        tableCount: 18,
        status: 'connected',
        createdAt: '2023-11-03T10:20:00Z',
        updatedAt: '2023-11-06T14:30:00Z'
      },
      {
        id: 3,
        name: '开发环境SQL Server',
        type: 'SQLServer',
        host: '192.168.1.102',
        port: 1433,
        database: 'dev_db',
        username: 'sa',
        password: '******',
        tableCount: 25,
        status: 'disconnected',
        createdAt: '2023-11-02T14:10:00Z',
        updatedAt: '2023-11-04T09:15:00Z'
      },
      {
        id: 4,
        name: '历史数据Oracle',
        type: 'Oracle',
        host: '192.168.1.103',
        port: 1521,
        database: 'history_db',
        username: 'system',
        password: '******',
        tableCount: 45,
        status: 'connected',
        createdAt: '2023-10-28T11:25:00Z',
        updatedAt: '2023-11-05T16:40:00Z'
      },
      {
        id: 5,
        name: '分析环境MySQL',
        type: 'MySQL',
        host: '192.168.1.104',
        port: 3306,
        database: 'analytics_db',
        username: 'analytics_user',
        password: '******',
        tableCount: 12,
        status: 'disconnected',
        createdAt: '2023-11-01T13:50:00Z',
        updatedAt: '2023-11-03T10:25:00Z'
      }
    ])
    
    // 数据库类型选项
    const dbTypeOptions = [
      { value: 'MySQL', label: 'MySQL' },
      { value: 'PostgreSQL', label: 'PostgreSQL' },
      { value: 'SQLServer', label: 'SQL Server' },
      { value: 'Oracle', label: 'Oracle' }
    ]
    
    // 根据筛选条件过滤数据源列表
    const filteredDataSources = computed(() => {
      let result = [...dataSources.value]
      
      // 关键字搜索
      if (searchKeyword.value) {
        const keyword = searchKeyword.value.toLowerCase()
        result = result.filter(item => 
          item.name.toLowerCase().includes(keyword) || 
          item.host.toLowerCase().includes(keyword) ||
          item.database.toLowerCase().includes(keyword)
        )
      }
      
      // 数据库类型筛选
      if (filters.value.type) {
        result = result.filter(item => item.type === filters.value.type)
      }
      
      // 连接状态筛选
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
    
    // 获取数据库类型标签样式
    const getDbTypeTag = (type) => {
      const typeMap = {
        'MySQL': 'primary',
        'PostgreSQL': 'success',
        'SQLServer': 'warning',
        'Oracle': 'danger'
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
    
    // 创建数据源
    const handleCreate = () => {
      router.push('/datasource/create')
    }
    
    // 编辑数据源
    const handleEdit = (row) => {
      router.push(`/datasource/edit/${row.id}`)
    }
    
    // 测试数据源连接
    const handleTest = (row) => {
      loading.value = true
      
      // 模拟API调用
      setTimeout(() => {
        loading.value = false
        
        // 显示成功消息
        if (row.status === 'connected') {
          ElMessage({
            message: `成功连接到数据源 ${row.name}`,
            type: 'success'
          })
        } else {
          ElMessage({
            message: `无法连接到数据源 ${row.name}，请检查配置`,
            type: 'error'
          })
        }
      }, 1000)
    }
    
    // 删除数据源
    const handleDelete = (row) => {
      ElMessageBox.confirm(
        `确定要删除数据源 "${row.name}" 吗？`,
        '警告',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }
      )
        .then(() => {
          // 模拟删除操作
          dataSources.value = dataSources.value.filter(item => item.id !== row.id)
          
          ElMessage({
            type: 'success',
            message: '删除成功'
          })
        })
        .catch(() => {
          // 取消删除
        })
    }
    
    // 获取数据源列表
    const fetchDataSources = () => {
      loading.value = true
      
      // 模拟API调用
      setTimeout(() => {
        // 实际项目中应该调用API获取数据
        // dataSources.value = response.data
        
        loading.value = false
      }, 500)
    }
    
    // 组件加载时获取数据
    onMounted(() => {
      fetchDataSources()
    })
    
    return {
      loading,
      searchKeyword,
      filters,
      currentPage,
      pageSize,
      totalCount,
      dataSources,
      filteredDataSources,
      dbTypeOptions,
      formatDate,
      getDbTypeTag,
      handleSearch,
      handleFilter,
      handleSizeChange,
      handleCurrentChange,
      handleCreate,
      handleEdit,
      handleTest,
      handleDelete
    }
  }
}
</script>

<style lang="scss" scoped>
.datasource-list-container {
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
  .datasource-list-container {
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