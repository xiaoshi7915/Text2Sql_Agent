import { defineStore } from 'pinia'
import { 
  getDatasources, 
  getDatasource, 
  createDatasource, 
  updateDatasource, 
  deleteDatasource,
  testDatasourceConnection,
  getTables,
  getTableSchema
} from '@/api/datasource'

export const useDatasourceStore = defineStore('datasource', {
  state: () => ({
    datasources: [], // 所有数据源列表
    currentDatasource: null, // 当前选中的数据源
    tables: [], // 当前数据源的表列表
    currentTable: null, // 当前选中的表
    tableSchema: null, // 当前表的结构
    loading: false, // 加载状态
    error: null // 错误信息
  }),
  
  getters: {
    // 获取数据源列表
    getDatasourceList: (state) => state.datasources,
    
    // 根据ID获取数据源
    getDatasourceById: (state) => (id) => {
      return state.datasources.find(ds => ds.id === id)
    },
    
    // 获取数据源类型列表
    getDatasourceTypes: () => {
      return [
        { value: 'mysql', label: 'MySQL' },
        { value: 'postgresql', label: 'PostgreSQL' },
        { value: 'oracle', label: 'Oracle' },
        { value: 'sqlserver', label: 'SQL Server' },
        { value: 'kingbase', label: 'KingbaseES' }
      ]
    }
  },
  
  actions: {
    // 加载所有数据源
    async fetchDatasources() {
      this.loading = true
      this.error = null
      
      try {
        const res = await getDatasources()
        this.datasources = res.data || []
      } catch (error) {
        this.error = error.message || '获取数据源列表失败'
        console.error('获取数据源列表失败:', error)
      } finally {
        this.loading = false
      }
    },
    
    // 加载单个数据源详情
    async fetchDatasource(id) {
      this.loading = true
      this.error = null
      
      try {
        const res = await getDatasource(id)
        this.currentDatasource = res.data || null
        return this.currentDatasource
      } catch (error) {
        this.error = error.message || '获取数据源详情失败'
        console.error('获取数据源详情失败:', error)
        return null
      } finally {
        this.loading = false
      }
    },
    
    // 创建数据源
    async addDatasource(data) {
      this.loading = true
      this.error = null
      
      try {
        const res = await createDatasource(data)
        // 添加到列表中
        if (res.data) {
          this.datasources.push(res.data)
        }
        return res
      } catch (error) {
        this.error = error.message || '创建数据源失败'
        console.error('创建数据源失败:', error)
        throw error
      } finally {
        this.loading = false
      }
    },
    
    // 更新数据源
    async editDatasource(id, data) {
      this.loading = true
      this.error = null
      
      try {
        const res = await updateDatasource(id, data)
        // 更新列表中的数据
        if (res.data) {
          const index = this.datasources.findIndex(ds => ds.id === id)
          if (index !== -1) {
            this.datasources[index] = res.data
          }
          if (this.currentDatasource && this.currentDatasource.id === id) {
            this.currentDatasource = res.data
          }
        }
        return res
      } catch (error) {
        this.error = error.message || '更新数据源失败'
        console.error('更新数据源失败:', error)
        throw error
      } finally {
        this.loading = false
      }
    },
    
    // 删除数据源
    async removeDatasource(id) {
      this.loading = true
      this.error = null
      
      try {
        const res = await deleteDatasource(id)
        // 从列表中移除
        this.datasources = this.datasources.filter(ds => ds.id !== id)
        if (this.currentDatasource && this.currentDatasource.id === id) {
          this.currentDatasource = null
        }
        return res
      } catch (error) {
        this.error = error.message || '删除数据源失败'
        console.error('删除数据源失败:', error)
        throw error
      } finally {
        this.loading = false
      }
    },
    
    // 测试数据源连接
    async testConnection(data) {
      this.loading = true
      this.error = null
      
      try {
        const res = await testDatasourceConnection(data)
        return res
      } catch (error) {
        this.error = error.message || '测试连接失败'
        console.error('测试连接失败:', error)
        throw error
      } finally {
        this.loading = false
      }
    },
    
    // 获取数据源的表列表
    async fetchTables(datasourceId) {
      this.loading = true
      this.error = null
      
      try {
        const res = await getTables(datasourceId)
        this.tables = res.data || []
        return this.tables
      } catch (error) {
        this.error = error.message || '获取表列表失败'
        console.error('获取表列表失败:', error)
        return []
      } finally {
        this.loading = false
      }
    },
    
    // 获取表结构
    async fetchTableSchema(datasourceId, table) {
      this.loading = true
      this.error = null
      this.currentTable = table
      
      try {
        const res = await getTableSchema(datasourceId, table)
        this.tableSchema = res.data || null
        return this.tableSchema
      } catch (error) {
        this.error = error.message || '获取表结构失败'
        console.error('获取表结构失败:', error)
        return null
      } finally {
        this.loading = false
      }
    },
    
    // 清空数据源状态
    clearDatasourceState() {
      this.currentDatasource = null
      this.tables = []
      this.currentTable = null
      this.tableSchema = null
      this.error = null
    }
  }
}) 