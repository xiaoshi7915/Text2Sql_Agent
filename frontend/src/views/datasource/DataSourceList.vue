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
            <el-tag size="small" :type="getDbTypeTag(row.ds_type)">{{ row.ds_type }}</el-tag>
            <span class="name-text">{{ row.name }}</span>
          </div>
        </template>
      </el-table-column>
      <el-table-column label="主机地址" prop="host" min-width="150" />
      <el-table-column label="数据库名" prop="database" min-width="120" />
      <el-table-column label="表数量" prop="table_count" width="100" align="center" />
      <el-table-column label="连接状态" width="120" align="center">
        <template #default="{ row }">
          <el-tag 
            :type="row.status?.is_connected ? 'success' : 'danger'" 
            size="small"
          >
            {{ row.status?.is_connected ? '已连接' : '未连接' }}
          </el-tag>
          <div class="last-checked" v-if="row.status?.last_checked">
            <el-tooltip 
              :content="`最后检查: ${formatDate(row.status.last_checked)}`" 
              placement="top"
            >
              <el-icon><icon-time /></el-icon>
            </el-tooltip>
          </div>
        </template>
      </el-table-column>
      <el-table-column label="最后更新时间" width="180" align="center">
        <template #default="{ row }">
          {{ formatDate(row.updated_at) }}
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
import { useDatasourceStore } from '@/store/datasource'

export default {
  name: 'DataSourceList',
  
  setup() {
    // 路由实例
    const router = useRouter()
    
    // 使用数据源Store
    const datasourceStore = useDatasourceStore()
    
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
    
    // 数据源列表
    const dataSources = ref([])
    
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
        result = result.filter(item => item.ds_type === filters.value.type)
      }
      
      // 连接状态筛选
      if (filters.value.status) {
        result = result.filter(item => item.connection_status === filters.value.status)
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
        'mysql': 'primary',
        'PostgreSQL': 'success',
        'postgresql': 'success',
        'SQLServer': 'warning',
        'sqlserver': 'warning',
        'Oracle': 'danger',
        'oracle': 'danger'
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
      router.push('/datasources/create')
    }
    
    // 编辑数据源
    const handleEdit = (row) => {
      router.push(`/datasources/edit/${row.id}`)
    }
    
    // 测试数据源连接
    const handleTest = async (row) => {
      loading.value = true
      
      try {
        // 调用测试连接API
        const result = await datasourceStore.testConnection({
          id: row.id,
          ds_type: row.ds_type,
          host: row.host,
          port: row.port,
          database: row.database,
          username: row.username,
          password: '******' // 密码需要在后端验证
        })
        
        if (result.success) {
          // 显示成功消息
          ElMessage({
            message: `成功连接到数据源 ${row.name}，发现 ${result.tables} 个表`,
            type: 'success'
          })
        } else {
          // 显示详细错误信息
          const errorMsg = result.error || '未知错误'
          const solution = result.details?.possible_solution
            ? `\n可能的解决方案: ${result.details.possible_solution}`
            : ''
          
          ElMessage({
            dangerouslyUseHTMLString: true,
            message: `<strong>无法连接到数据源 ${row.name}</strong><br>${errorMsg}${solution ? `<br><br><em>${solution}</em>` : ''}`,
            type: 'error',
            duration: 5000,
            showClose: true
          })
          
          // 如果错误类型是认证插件错误，提示使用修复工具
          if (result.details?.error_type === 'auth_plugin_error') {
            ElMessage({
              dangerouslyUseHTMLString: true,
              message: `<strong>MySQL 8.0+ 认证问题</strong><br>请使用 <code>python backend/fix_mysql_connection.py</code> 修复认证插件或启用SSL连接`,
              type: 'warning',
              duration: 7000,
              showClose: true
            })
          }
        }
        
        // 刷新数据源列表以获取更新后的状态
        await fetchDataSources()
      } catch (error) {
        // 尝试从错误响应中获取详细信息
        let errorMsg = '测试连接失败'
        let solution = ''
        
        if (error.response && error.response.data) {
          const responseData = error.response.data
          errorMsg = responseData.error || errorMsg
          solution = responseData.details?.possible_solution || ''
        } else {
          errorMsg = error.message || errorMsg
        }
        
        ElMessage({
          dangerouslyUseHTMLString: true,
          message: `<strong>无法连接到数据源 ${row.name}</strong><br>${errorMsg}${solution ? `<br><br><em>${solution}</em>` : ''}`,
          type: 'error',
          duration: 5000,
          showClose: true
        })
        
        // 仍然需要刷新列表以更新失败状态
        await fetchDataSources()
      } finally {
        loading.value = false
      }
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
        .then(async () => {
          loading.value = true
          try {
            await datasourceStore.removeDatasource(row.id)
            ElMessage({
              type: 'success',
              message: '删除成功'
            })
            await fetchDataSources() // 重新获取列表
          } catch (error) {
            ElMessage({
              type: 'error',
              message: `删除失败: ${error.message}`
            })
          } finally {
            loading.value = false
          }
        })
        .catch(() => {
          // 取消删除
        })
    }
    
    // 获取数据源列表
    const fetchDataSources = async () => {
      loading.value = true
      
      try {
        // 调用API获取数据源列表
        await datasourceStore.fetchDatasources()
        dataSources.value = datasourceStore.datasources
      } catch (error) {
        console.error('获取数据源列表失败:', error)
        ElMessage.error(`获取数据源列表失败: ${error.message}`)
      } finally {
        loading.value = false
      }
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
  
  .last-checked {
    margin-top: 5px;
    font-size: 12px;
    color: #909399;
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